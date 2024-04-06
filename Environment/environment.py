import random 
import time 
import math 
import cv2 
import carla
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from tensorflow.keras.models import load_model

TIME_PER_SCENARIO = 30
CHANNELS = 3
SPIN = 10

HEIGHT = 720
WIDTH = 1280

class CarEnvironment(gym.Env):
    prefered_speed = 35
    speed_threshold = 2
    

    def __inti__(self):
        
        self.action_center = spaces.MultiDiscrete([9])
        self.CNN_image = None
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(7,18,8),
            dtype=np.float32,
        )
        self.client = carla.Client("localhost", 2000)
        self.world = self.client.get_world()
        self.blueprints = self.world.get_blueprint_libaray()
