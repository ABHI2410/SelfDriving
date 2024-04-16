import sys
import traceback
import carla
import signal
import time
from datetime import datetime
from Constants import SCENARIO_RUNNER_PATH
sys.path.append(SCENARIO_RUNNER_PATH)
from Environment.Scenarios.CustomScenarioManager import CustomScenarioManager
from srunner.scenarios.route_scenario import RouteScenario
from srunner.tools.route_parser import RouteParser
from srunner.scenarios import *
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider




class Scenario():
    ego_vehicles = []

    # Tunable parameters
    client_timeout = 10.0  # in seconds
    wait_for_world = 20.0  # in seconds
    frame_rate = 20.0      # in Hz

    # CARLA world and scenario handlers
    world = None
    manager = None

    finished = False

    additional_scenario_module = None

    agent_instance = None
    module_agent = None
    def __init__(self, args):
        self._args = args
        if args.timeout:
            self.client_timeout = args.timeout
        

        self.client = carla.Client(args.host,int(args.port))
        self.client.set_timeout(self.client_timeout)
        self.manager = CustomScenarioManager(self._args.debug, self._args.sync, self._args.timeout)

        # Create signal handler for SIGINT
        self._shutdown_requested = False
        if sys.platform != 'win32':
            signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self._start_wall_time = datetime.now()
    
    def destroy(self):
        """
        Cleanup and delete actors, ScenarioManager and CARLA world
        """

        self._cleanup()
        if self.manager is not None:
            del self.manager
        if self.world is not None:
            del self.world
        if self.client is not None:
            del self.client
            
    def _signal_handler(self,*args):
        """
        Terminate scenario ticking when receiving a signal interrupt
        """
        self._shutdown_requested = True
        if self.manager:
            self.manager.stop_scenario()
            self._cleanup()
            if not self.manager.get_running_status():
                raise RuntimeError("Timeout occurred during scenario execution")


    def load_and_wait_for_world(self,town,ego_vehicles=None):
        self.world = self.client.load_world(town)
        self.world = self.client.get_world()
        CarlaDataProvider.set_client(self.client)
        CarlaDataProvider.set_world(self.world)

        # Wait for the world to be ready
        if CarlaDataProvider.is_sync_mode():
            self.world.tick()
        else:
            self.world.wait_for_tick()
        map_name = CarlaDataProvider.get_map().name.split('/')[-1]
        if map_name not in (town, "OpenDriveMap"):
            print("The CARLA server uses the wrong map: {}".format(map_name))
            print("This scenario requires to use map: {}".format(town))
            return False
        else:
            print(f"Loaded Map: {map_name}")

        return True


    
    def _prepare_ego_vehicles(self, ego_vehicles):
        """
        Spawn or update the ego vehicles
        """
        self.blueprints = CarlaDataProvider.get_client().get_world().get_blueprint_library()
        for vehicle in ego_vehicles:
            self.ego_vehicles.append(CarlaDataProvider.request_new_actor(vehicle.model,
                                                                     actor_category=vehicle.category))
            self.attach_sensors(self.ego_vehicles[-1])


            for i, _ in enumerate(self.ego_vehicles):
                self.ego_vehicles[i].set_transform(ego_vehicles[i].transform)
                self.ego_vehicles[i].set_target_velocity(carla.Vector3D())
                self.ego_vehicles[i].set_target_angular_velocity(carla.Vector3D())
                self.ego_vehicles[i].apply_control(carla.VehicleControl())
                CarlaDataProvider.register_actor(self.ego_vehicles[i], ego_vehicles[i].transform)

        # sync state
        if CarlaDataProvider.is_sync_mode():
            self.world.tick()
        else:
            self.world.wait_for_tick()
        print("Created ego vehicle ")
    
    def _cleanup(self):
        """
        Remove and destroy all actors
        """
        if self.finished:
            return

        self.finished = True

    def load_and_run_scenario(self,config):
        result = False
        if not self.load_and_wait_for_world(config.town, config.ego_vehicles):
            self._cleanup()
            return False
        CarlaDataProvider.set_traffic_manager_port(int(self._args.trafficManagerPort))
        tm = self.client.get_trafficmanager(int(self._args.trafficManagerPort))
        tm.set_random_device_seed(int(self._args.trafficManagerSeed))
                
        print("Preparing scenario: " + config.name)

        try: 
            self._prepare_ego_vehicles(config.ego_vehicles)
            scenario = RouteScenario(world=self.world,
                                        config=config,
                                        debug_mode=self._args.debug)
            self.route_waypoints = scenario.route
            
        except Exception as exception:                 
            print("The scenario cannot be loaded")
            traceback.print_exc()
            print(exception)
            self._cleanup()
            return False


        try:
            # Load scenario and run it
            self.manager.load_scenario(scenario)
            self.manager.run_scenario()
            scenario.remove_all_actors()
            result = True

        except Exception as e:              # pylint: disable=broad-except
            traceback.print_exc()
            print(e)
            result = False

        self._cleanup()
        return result



    def run_route(self):
        """
        Run the route scenario
        """
        result = False

        # retrieve routes
        route_configurations = RouteParser.parse_routes_file(self._args.route, self._args.route_id)

        for config in route_configurations:
            for _ in range(self._args.repetitions):
                result = self.load_and_run_scenario(config)

                self._cleanup()
        return result

    def run(self):
        result = self.run_route()