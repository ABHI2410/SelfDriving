import os
from Constants import SCENARIO_RUNNER_PATH
os.environ["SCENARIO_RUNNER_ROOT"] = SCENARIO_RUNNER_PATH

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

