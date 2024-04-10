import sys
from Constants import SCENARIO_RUNNER_PATH
from Environment.Scenarios.CustomScenarioRunner import CustomScenarioRunner
sys.path.append(SCENARIO_RUNNER_PATH)

from srunner.tools.scenario_parser import ScenarioConfigurationParser
from srunner.scenarios import *
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider


class Scenario():
    def __init__(self,world,scenario,timeout_duration):
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
        self.scenario=scenario
        self.sync=False 
        self.timeout='10' 
        self.trafficManagerPort='8000' 
        self.trafficManagerSeed='0' 
        self.waitForEgo=False
        self.scenario_timeout = timeout_duration
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