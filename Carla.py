import os 
os.environ["SCENARIO_RUNNER_ROOT"] = "/home/carla/Desktop/Carla/scenario_runner/"

import carla
import random
import cv2
import math
import numpy as np
import time
from Environment.Actors.Vehicle import Vehicle
from Environment.Scenarios.scenarios import Scenario
class Carla:
    def __init__(self,path):
        self.host='localhost' 
        self.port='2000'
        self.timeout = 200
        self.trafficManagerPort='8000'
        self.trafficManagerSeed='0'
        self.sync = False
        self.route = path
        self.route_id = 0
        self.output = True
        self.outputDir = '../../SelfDriving'
        self.configFile = ''
        self.additionalScenario = ''
        self.debug = True
        self.reloadWorld = True
        self.repetitions = 1

no_of_routes = 89 
os.chdir("../Carla/scenario_runner/srunner/data")
file_path = os.getcwd()
os.chdir("../../../../SelfDriving")
files = os.listdir(file_path)
route_data = [file for file in files if "town10" in file][0]
training_route = os.path.join(file_path,route_data)
obj = Carla(training_route)
sce = Scenario(obj)
sce.run()