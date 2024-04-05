import os 
os.environ["SCENARIO_RUNNER_ROOT"] = "/home/carla/Desktop/Carla/scenario_runner-0.9.15/"

import carla
import random
import cv2
import math
import numpy as np
import time
from Environment.Actors.Vehicle import Vehicle
from Environment.Scenarios.scenarios import start_scenario 
class Carla:
    def __init__(self) -> None:
        self.client = carla.Client('localhost', 2000)
        self.world = self.client.get_world()
        self.spawn_points = self.world.get_map().get_spawn_points()
        spawn_point = random.choice(self.spawn_points)
        self.actor = Vehicle(self.client, spawn_point)

    # def _scenario(self):
    #     scenarios.followLeadingVehicle(self.client,self.world)

    def _game(self):
        while True:
            self.world.tick()
            if cv2.waitKey(1) == ord('q'):
                break
            spectator = self.world.get_spectator()
            rgb_image = self.actor.rgbCameraSensor.get_image()
            # semantic_lidar_image = self.actor.semanticLidarSensor.get_image()
            steering_angle = 0
            v = self.actor.vehicle.get_velocity()
            speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2),0)
            rgb_image = cv2.putText(rgb_image, f"Speed: {str(int(speed))} kmh", (30,50),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
            estimate_throttle = self.actor.maintain_speed(speed,20)
            self.actor.control(estimate_throttle,0)
            vehicle_location = self.actor.vehicle.get_transform()
            spectator.set_transform(carla.Transform(carla.Location(vehicle_location.location.x-5,vehicle_location.location.y,vehicle_location.location.z+40) , carla.Rotation(pitch=-90)))
            # self.actor.semanticLidarSensor.get_image()
            # cv2.imshow('Carla ',rgb_image)
            # cv2.imshow('Lidr', semantic_lidar_image)

            # Adjust throttle based on speed limit and traffic light state
            if traffic_light_state == carla.TrafficLightState.Red or speed > speed_limit:
                estimate_throttle = 0
            else:
                estimate_throttle = self.actor.maintain_speed(speed, 20)

            self.actor.control(estimate_throttle, steering_angle)

            # Display sensor data
            cv2.imshow('Carla', rgb_image)
            # cv2.imshow('Lidar', semantic_lidar_image)  # Uncomment to display semantic lidar image

obj = Carla()
start_scenario(obj.world,obj.actor)
# obj._game()
# obj._scenario()

obj = Carla()
obj._game()
