import sys
from Environment.Scenarios.CustomScenarioRunner import CustomScenarioRunner
sys.path.append("/home/carla/Desktop/Carla/scenario_runner/")

from srunner.tools.scenario_parser import ScenarioConfigurationParser
from srunner.scenarios import *
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider


'''

Scenarios: 
EnterActorFlow_1
ChangeLane_1/2
ControlLoss_1-15
CutInFrom_left_Lane
CutInFrom_right_Lane
FollowLeadingVehicle_1-11
FollowLeadingVehicleWithObstacle_1-11
FreeRide_1-4
MultiEgo_1/2
HighwayCutIn_1
OtherLeadingVehicle_1-10
NoSignalJunctionCrossing
StationaryObjectCrossing_1-8
DynamicObjectCrossing_1-9
ConstructionObstacle
ManeuverOppositeDirection_1-4
Accident_1
Construction_1
OppositeVehicleRunningRedLight_1-5
SignalizedJunctionLeftTurn_1-6
SignalizedJunctionRightTurn_1-7
VehicleOpensDoorTwoWays_1
VehicleTurningLeft_1-8
VehicleTurningRight_1-8

ActorConfigurationData
        self.model = model
        self.rolename = rolename
        self.transform = transform
        self.speed = speed
        self.autopilot = autopilot
        self.random_location = random
        self.color = color
        self.category = category
        self.args = args


ScenarioConfiguration
        self.trigger_points = []
        self.ego_vehicles = []
        self.other_actors = []
        self.other_parameters = {}
        self.town = None
        self.name = None
        self.type = None
        self.route = None
        self.agent = None
        self.weather = carla.WeatherParameters(sun_altitude_angle=70, cloudiness=50)
        self.friction = None
        self.subtype = None
        self.route_var_name = None
'''


class Scenario():
    def __init__(self,world):
        self.additionalScenario='' 
        self.agent=None 
        self.agentConfig='' 
        self.configFile='' 
        self.debug=False 
        self.file=False 
        self.host='localhost' 
        self.json=False 
        self.junit=False 
        self.list=False 
        self.openscenario=None 
        self.openscenario2=None 
        self.openscenarioparams=None 
        self.output=True 
        self.outputDir='' 
        self.port='2000' 
        self.randomize=False 
        self.record='' 
        self.reloadWorld=True 
        self.repetitions=1 
        self.route=None 
        self.route_id='' 
        self.scenario='NoSignalJunctionCrossing'
        self.sync=False 
        self.timeout='10' 
        self.trafficManagerPort='8000' 
        self.trafficManagerSeed='0' 
        self.waitForEgo=False
        self.start_scenario(world)    

    def start_scenario(self,world):
        scenario_runner = None
        result = False
        self.world = world
        self.blueprints = self.world.get_blueprint_library()
        CarlaDataProvider.set_world(self.world)
        self.scene = CustomScenarioRunner(self)
        self.scene.world = self.world
        configurations = ScenarioConfigurationParser.parse_scenario_configuration(
                self.scenario,
                self.configFile)

        if len(configurations) < 1:
            # print("Configuration for scenario {} cannot be found!".format(self._args.scenario))
            return result
        
        for config in configurations:
            for _ in range(self.scene._args.repetitions):
                    self.scene.finished = False
                    result = self.scene._load_and_run_scenario(config)
            self.scene._cleanup()
        return result