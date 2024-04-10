import os
import sys
import traceback
from Constants import SCENARIO_RUNNER_PATH
from Environment.Sensors.CollisionDetector import CollisionDetector
from Environment.Sensors.RgbCameraSensor import RgbCameraSensor
from Environment.Sensors.GnssSensor import GnssSensor
from Environment.Sensors.ImuSensor import ImuSensor
from Environment.Sensors.SemanticLidarSensor import SemanticLidarSensor
from Environment.Sensors.DepthCameraSensor import DepthCameraSensor
from Environment.Sensors.TrafficLightSensor import TrafficLightSensor
from Environment.Sensors.TrafficSignSensor import SpeedLimitSensor
from Environment.Sensors.RadarSensor import RadarSensor
from Environment.Sensors.LaneInvasionSensor import LaneInvasionSensor
from Environment.Sensors.WeatherSensor import WeatherSensor


from Environment.Scenarios.CustomScenarioManager import CustomScenarioManager
sys.path.append(SCENARIO_RUNNER_PATH)
from scenario_runner import ScenarioRunner 
from srunner.scenarios.open_scenario import OpenScenario
from srunner.scenarios.route_scenario import RouteScenario
# from srunner.scenarios.osc2_scenario import OSC2Scenario
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider



def attach_sensors(world,vehicle,blueprints):
        collisionSensor = CollisionDetector(world, vehicle, blueprints)
        rgbCameraSensor = RgbCameraSensor(world, vehicle, blueprints)
        gnssSensor = GnssSensor(world, vehicle, blueprints)
        imuSensor = ImuSensor(world, vehicle, blueprints)
        semanticLidarSensor = SemanticLidarSensor(world, vehicle, blueprints)
        depthCameraSensor = DepthCameraSensor(world,vehicle,blueprints)
        trafficLightSensor = TrafficLightSensor(world, vehicle, blueprints)
        speedLimitSensor = SpeedLimitSensor(world, vehicle, blueprints)
        radarSensor = RadarSensor(world, vehicle, blueprints)
        laneInvasionSensor = LaneInvasionSensor(world, vehicle, blueprints)
        # pedestrianDetectionSensor = PedestrianDetectionSensor(world, vehicle)
        weatherSensor = WeatherSensor(world)
        return {
            "Collision_Sensor": collisionSensor,
            "RGB Sensor" : rgbCameraSensor,
            "GNSS Sensor" : gnssSensor,
            "IMU Sensor" : imuSensor,
            "Semantic Lidar Sensor" : semanticLidarSensor,
            "Depth Camera Sensor" : depthCameraSensor,
            "Traffic Light Sensor" : trafficLightSensor,
            "Speed Limit Sensor" : speedLimitSensor,
            "Radar Sensor" : radarSensor,
            "Lane Invsion Sensor" : laneInvasionSensor,
            "Weather Sensor" : weatherSensor
        }
class CustomScenarioRunner(ScenarioRunner):   
    def __init__(self, args):
        super().__init__(args)
        self.manager = CustomScenarioManager(self._args.debug, self._args.sync, self._args.timeout)


    def _load_and_run_scenario(self, config):
        """
        Load and run the scenario given by config
        """
        result = False
        if not self._load_and_wait_for_world(config.town, config.ego_vehicles):
            self._cleanup()
            return False

        if self._args.agent:
            agent_class_name = self.module_agent.__name__.title().replace('_', '')
            try:
                self.agent_instance = getattr(self.module_agent, agent_class_name)(self._args.agentConfig)
                config.agent = self.agent_instance
            except Exception as e:          # pylint: disable=broad-except
                traceback.print_exc()
                print("Could not setup required agent due to {}".format(e))
                self._cleanup()
                return False

        CarlaDataProvider.set_traffic_manager_port(int(self._args.trafficManagerPort))
        tm = self.client.get_trafficmanager(int(self._args.trafficManagerPort))
        tm.set_random_device_seed(int(self._args.trafficManagerSeed))
        if self._args.sync:
            tm.set_synchronous_mode(True)

        # Prepare scenario
        print("Preparing scenario: " + config.name)
        try:
            self._prepare_ego_vehicles(config.ego_vehicles)
            if self.ego_vehicles:
                print("Created Ego Vehicle")
                self.sensors = attach_sensors(self.world, self.ego_vehicles[0], self.world.get_blueprint_library())
            if self._args.openscenario:
                scenario = OpenScenario(world=self.world,
                                        ego_vehicles=self.ego_vehicles,
                                        config=config,
                                        config_file=self._args.openscenario,
                                        timeout=100000)
            elif self._args.route:
                scenario = RouteScenario(world=self.world,
                                            config=config,
                                            debug_mode=self._args.debug)
            else:
                scenario_class = self._get_scenario_class_or_fail(config.type)
                scenario = scenario_class(world=self.world,
                                            ego_vehicles=self.ego_vehicles,
                                            config=config,
                                            randomize=self._args.randomize,
                                            debug_mode=self._args.debug)
        except Exception as exception:                  # pylint: disable=broad-except
            print("The scenario cannot be loaded")
            traceback.print_exc()
            print(exception)
            self._cleanup()
            return False

        
        try:
            if self._args.record:
                recorder_name = "{}/{}/{}.log".format(
                    os.getenv('SCENARIO_RUNNER_ROOT', "./"), self._args.record, config.name)
                self.client.start_recorder(recorder_name, True)

            # Load scenario and run it
            self.manager.load_scenario(scenario, self.agent_instance)
            self.manager.run_scenario(self.sensors)
            # Provide outputs if required
            self._analyze_scenario(config)

            # Remove all actors, stop the recorder and save all criterias (if needed)
            scenario.remove_all_actors()
            if self._args.record:
                self.client.stop_recorder()
                self._record_criteria(self.manager.scenario.get_criteria(), recorder_name)

            result = True

        except Exception as e:              # pylint: disable=broad-except
            traceback.print_exc()
            print(e)
            result = False

        self._cleanup()
        return result