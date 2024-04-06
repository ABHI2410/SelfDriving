import carla
import sys
import traceback

sys.path.append("/home/carla/Desktop/Carla/scenario_runner-0.9.15/")
from scenario_runner import ScenarioRunner 
from srunner.tools.scenario_parser import ScenarioConfigurationParser
from srunner.scenarios import *
from Environment.Sensors.CollisionDetector import CollisionDetector
from Environment.Sensors.RgbCameraSensor import RgbCameraSensor
from Environment.Sensors.GnssSensor import GnssSensor
from Environment.Sensors.ImuSensor import ImuSensor
from Environment.Sensors.SemanticLidarSensor import SemanticLidarSensor
from Environment.Sensors.DepthCameraSensor import DepthCameraSensor
from Environment.Sensors.TrafficLightSensor import TrafficLightSensor
from Environment.Sensors.SpeedLimitSensor import SpeedLimitSensor
from Environment.Sensors.RadarSensor import RadarSensor
from Environment.Sensors.LaneInvasionSensor import LaneInvasionSensor
from Environment.Sensors.WeatherSensor import WeatherSensor
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

    def attach_sensors(self):
        self.collisionSensor = CollisionDetector(self.world, self.vehicle, self.blueprints)
        self.rgbCameraSensor = RgbCameraSensor(self.world, self.vehicle, self.blueprints)
        self.gnssSensor = GnssSensor(self.world, self.vehicle, self.blueprints)
        self.imuSensor = ImuSensor(self.world, self.vehicle, self.blueprints)
        self.semanticLidarSensor = SemanticLidarSensor(self.world, self.vehicle, self.blueprints)
        self.depthCameraSensor = DepthCameraSensor(self.vehicle)
        self.trafficLightSensor = TrafficLightSensor(self.world, self.vehicle)
        self.speedLimitSensor = SpeedLimitSensor(self.vehicle)
        self.radarSensor = RadarSensor(self.world, self.vehicle)
        self.laneInvasionSensor = LaneInvasionSensor(self.world, self.vehicle)
        # self.pedestrianDetectionSensor = PedestrianDetectionSensor(self.world, self.vehicle)
        self.weatherSensor = WeatherSensor(self.world)

    def start_scenario(self,world):
        scenario_runner = None
        result = False
        self.world = world
        self.blueprints = self.world.get_blueprint_library()

        scene = ScenarioRunner(self)
        configurations = ScenarioConfigurationParser.parse_scenario_configuration(
                self.scenario,
                self.configFile)
        if configurations[0].ego_vehicles[0].rolename == "hero":
             self.vehicle = configurations[0].ego_vehicles[0]
             print(self.vehicle.model)
             self.attach_sensors()

        if len(configurations) < 1:
            print("Configuration for scenario {} cannot be found!".format(self._args.scenario))
            return result
        
        for config in configurations:
            for _ in range(scene._args.repetitions):
                    scene.finished = False
                    result = scene._load_and_run_scenario(config)
            scene._cleanup()
        return result