import os 
os.environ["SCENARIO_RUNNER_ROOT"] = "/home/carla/Desktop/Carla/scenario_runner-0.9.15/"

import carla
import random
import cv2
import math
import numpy as np
import time
from Environment.Actors.Vehicle import Vehicle
from Environment.Scenarios.scenarios import Scenario
class Carla:
    def __init__(self) -> None:
        self.client = carla.Client('localhost', 2000)
        self.world = self.client.get_world()
        self.scene = Scenario(self.world)
    

obj = Carla()

