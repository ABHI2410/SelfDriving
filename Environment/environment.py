import os
import sys
import carla
import gymnasium as gym

sys.path.append("/home/carla/Desktop/Carla/leaderboard")
from leaderboard.utils.statistics_manager import StatisticsManager, FAILURE_MESSAGES
from leaderboard.utils.route_indexer import RouteIndexer
from leaderboard.scenarios.route_scenario import RouteScenario

LEADERBOARD_ROOT = os.environ["LEADERBOARD_ROOT"]
ROUTE = os.path.join(LEADERBOARD_ROOT, "data/routes_devtest.xml")
ROUTE_SUBSET = 0
REPETITIONS = 1
DEBUG_CHALLENGE=1

CHECKPOINT_ENDPOINT = "../RL/results.json"
CHECKPOINT_DEBUG = "../RL/results.txt"


class CustomLeaderboardEvaluator():
    def __init__(self, world, statistics_manager,resume):
        self.world = world
        self.resume = resume
        self.checkpoint = CHECKPOINT_ENDPOINT
        self.statistics_manager = statistics_manager
        self.sensors_initialized = False

    def load_world(self):
        settings = self.world.get_settings()
        settings.title_stream_distance = 650 
        settings.actor_active_distance = 650 
        self.world.apply_settings(settings)

        self.world.reset_all_traffic_lights()
        

    def load_and_run(self,config):
        print("Statrting leaderboard scenario")
        route_name = f"{config.name}_rep{config.repetition_index}"
        self.statistics_manager.create_route_data(route_name,config.index)
        try:
            self.load_world(config.town)
            self.route_scenario = RouteScenario(world = self.world,config = config, debug_mode=DEBUG_CHALLENGE)
            self.statistics_manager.set_scenario(self.route_scenario)
        except Exception:
            print("The scenario could not be loaded")
            print()

    def run(self,routes,repetitions,routes_subset):
        route_indexer = RouteIndexer(routes, repetitions, routes_subset)
        
        # if self.resume:
        #     resume = route_indexer.validate_and_resume(self.checkpoint)
        #     if resume:
        #         self.statistics_manager.add_file_records(self.checkpoint)

        # else:
        #     self.statistics_manager.clear_records()
        # self.statistics_manager.save_progress(route_indexer.index,route_indexer.total)
        # self.statistics_manager.write_statistics()

        crashed = False
        while route_indexer.peek() and not crashed:
            config = route_indexer.get_next_config()
            crashed = self.load_and_run(config)

        # if not crashed:
        #     self.statistics_manager.compute_global_statistics()
        #     self.statistics_manager.validate_and_write_statistics(self.sensors_initialized, crashed)

        return crashed
        

    

class EnvVariables():
    def __init__(self) -> None:
        self.debug = 0
        self.record = ''
        self.timeout = 300.0
        self.routes = ROUTE
        self.route_subset = ROUTE_SUBSET
        self.repetitions = REPETITIONS
        self.agent = '/home/carla/Desktop/SelfDriving/Carla.py'
        self.agent_config = ''
        self.track = "SENSORS"
        self.resume = False
        self.checkpoint = CHECKPOINT_ENDPOINT
        self.checkpoint_debug = CHECKPOINT_DEBUG
class Environemnt(gym.Env):
    def __init__(self) -> None:
        super().__init__()
        
    def main(self):
        envVars = EnvVariables()
        statistics_manager = StatisticsManager(envVars.checkpoint,envVars.checkpoint_debug)
        leaderboard = CustomLeaderboardEvaluator(statistics_manager,envVars.checkpoint,False)
        leaderboard.run(envVars.routes,envVars.repetitions,envVars.route_subset)

obj = Environemnt()
obj.main()