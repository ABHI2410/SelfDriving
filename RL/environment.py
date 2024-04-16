import random
import time
import numpy as np
import math 
import cv2
import gymnasium as gym
from gymnasium import spaces
import carla
import os
from RL.ModelDefination import ProcessData


SECONDS_PER_EPISODE = 100
N_CHANNELS = 3
HEIGHT = 240
WIDTH = 320
SPIN = 10 #angle of random spin
HEIGHT_REQUIRED_PORTION = 0.5 #bottom share, e.g. 0.1 is take lowest 10% of rows
WIDTH_REQUIRED_PORTION = 0.9


class Env(gym.Env):
    steer_amt = 1.0
    width = 640
    height = 480
    def __init__(self,sce) -> None:
        super(Env,self).__init__()
        self.action_space = spaces.MultiDiscrete([9,9,4])
        self.observation_space = spaces.Box(low=0.0, high=1.0,
                                            shape=(8,480,360,3), dtype=np.float32)
        self.sce = sce
        

    def maintain_speed(self, speed, preferred_speed):
        if speed >= preferred_speed:
            return 0
        elif speed < preferred_speed - 2:
            return 0.8
        else:
            return 0.4


    def get_next_route_waypoint(self):
        # Get the current location of the ego vehicle
        ego_location = self.sce.ego_vehicles[0].get_location()

        # Find the closest waypoint to the current location
        closest_waypoint = None
        closest_distance = float('inf')
        for waypoint in self.sce.route_waypoints:
            distance = waypoint.location.distance(ego_location)
            if distance < closest_distance:
                closest_distance = distance
                closest_waypoint = waypoint

        # Get the next waypoint along the route from the current waypoint
        next_waypoint = closest_waypoint.next(1)[0]

        return (closest_waypoint,next_waypoint)

    def step (self,action):
        ego_location = self.sce.ego_vehicles[0].get_transform()
        self.spectator.set_transform(carla.Transform(ego_location.location + carla.Location(z=20),carla.Rotation(yaw =-180, pitch=-90)))

        steer = action[0]
        if steer == 0: 
            steer = -1.0
        elif steer == 1:
            steer = -4.5
        elif steer == 2:
            steer = -1.5
        elif steer == 3:
            steer == -0.05
        elif steer == 4:
            steer = 0.0
        elif steer == 5: 
            steer = 0.05
        elif steer == 6:
            steer = 1.5
        elif steer == 7:
            steer = 4.5
        elif steer == 8:
            steer == 1

        throttle = action[1]
        if throttle ==0:
            throttle = 0.0
        elif throttle ==1:
            throttle = 0.1
        elif throttle ==2:
            throttle = 0.2
        elif throttle ==3:
            throttle = 0.3
        elif throttle ==4:
            throttle = 0.4 
        elif throttle ==5:
            throttle = 0.5
        elif throttle ==6:
            throttle = 0.65
        elif throttle ==7:
            throttle = 0.8
        elif throttle ==8:
            throttle = 1.0
        v = self.sce.ego_vehicles[0].get_velocity()
        speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2),0)
    
        self.sce.ego_vehicles[0].apply_control(carla.VehicleControl(throttle=throttle, steer=steer, brake = 1-throttle))

        distance= self.start.distance(self.sce.ego_vehicles[0].get_location())
        sensor_data = self.sce.manager.sensors
        rgb_img = sensor_data.get("RGB Sensor").get_image()
        img_to_show = sensor_data.get("Scemantic_Camera").get_image().get("Front").get("image")
        combined_image = np.concatenate((cv2.resize(rgb_img, (620, 480)),cv2.resize(img_to_show, (620, 480))),axis=1)
        cv2.imshow('Carla', combined_image)
        cv2.waitKey(1)

        lock_duration = 0
        if self.steering_lock == False:
            if steer<-0.6 or steer>0.6:
                self.steering_lock = True
                self.steering_lock_start = time.time()
        else:
            if steer<-0.6 or steer>0.6:
                lock_duration = time.time() - self.steering_lock_start
        
        reward = 0
        done = False
        car_location = self.sce.ego_vehicles[0].get_transform()
        waypoint = [waypoint for point in self.sce.route_waypoints if car_location.location.x == point.location.x and car_location.location.y == point.location.y]
        # LEFT = 1
        # RIGHT = 2
        # STRAIGHT = 3
        # LANEFOLLOW = 4
        # CHANGELANELEFT = 5
        # CHANGELANERIGHT = 6
        if waypoint[1].value == 1 and steer > 0:
            done = True
            reward = reward - 200
        elif waypoint[1].value == 2 and steer < 0:
            done = True
            reward = reward - 200
        elif (waypoint[1].value == 3 or waypoint[1].value == 3)  and steer < 0.4 and steer >-0.4:
            done = True
            reward = reward + 200
        if speed < 20 and (waypoint[1].value == 5 or waypoint[1].value == 6)  and self.sce.manager.sensors.get("Lane Invsion Sensor").get_data()[0]:
            reward = reward - 300
           
    
        if len(sensor_data.get("Collision_Sensor").history)!=0:
            done = True
            reward = reward - 300
        if len(sensor_data.get("Lane Invsion Sensor").history)!=0:
            done = True
            reward = reward - 300
        if lock_duration>3:
            reward = reward - 150
            done = True
        elif lock_duration > 1:
            reward = reward - 20
        
        if distance < 30:
            reward = reward - 100
        elif distance < 50:
            reward = reward + 100
        else:
            reward = reward + 300
        if speed > 50:
            reward = reward - 100 
        if action[2] == 0.0:
            if speed<10:
                reward = reward - 100
            elif speed < 50 and speed > 20:
                reward = reward + 300
        if self.start + SECONDS_PER_EPISODE < time.time():
            done = True
        scemantic_camers = self.sce.sensors.get("Scemantic_Camera").get_image()
        lane_invasion = self.sce.sensors.get("Lane Invsion Sensor").get_data()
        collisons = self.sce.sensors.get("Collision_Sensor").get_collision_history()
        nearby_vehicle = self.sce.sensors.get("Semantic Lidar Sensor").get_vehicle_distances()
        traffic_light = self.sce.sensors.get("Traffic Light Sensor").get_traffic_light_state()
        car_location = self.sce.ego_vehicles[0].get_transform()
        waypoint = self.get_next_route_waypoint()[1]
        p = ProcessData(scemantic_camers,lane_invasion,collisons,nearby_vehicle,traffic_light,speed,waypoint)
        obs = p._get_data()
        
        return obs,reward,done,{}
        
    def rest(self):
        print("rest requested")
        self.sce._cleanup()
        self.sce.manager.cleanup()
        result = self.sce.run_route()
        self.start = self.sce.ego_vehicles[0].get_location()
        self.sce.ego_vehicles[0].apply_control(carla.VehicleControl(throttle=0.0, brake=0.0))

        angle = random.randrange(-10,10,1)
        throttle = random.randrange(0,1,0.1)
        trans = self.sce.ego_vehicles[0].get_transform()
        trans.rotation.yaw = trans.rotation.yaw + angle
        self.sce.ego_vehicles[0].set_transform(trans)
        self.episode_start = time.time()
        self.steering_lock = False
        self.steering_lock_start = None 
        self.step_counter = 0
        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=0.0))
        v = self.sce.ego_vehicles[0].get_velocity()
        speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2),0)
        scemantic_camers = self.sce.sensors.get("Scemantic_Camera").get_image()
        lane_invasion = self.sce.sensors.get("Lane Invsion Sensor").get_data()
        collisons = self.sce.sensors.get("Collision_Sensor").get_collision_history()
        nearby_vehicle = self.sce.sensors.get("Semantic Lidar Sensor").get_vehicle_distances()
        traffic_light = self.sce.sensors.get("Traffic Light Sensor").get_traffic_light_state()
        car_location = self.sce.ego_vehicles[0].get_transform()
        waypoint = self.get_next_route_waypoint()[1]
        p = ProcessData(scemantic_camers,lane_invasion,collisons,nearby_vehicle,traffic_light,speed,waypoint)
        obs = p._get_data()
        return obs