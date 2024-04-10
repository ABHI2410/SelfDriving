import carla
import random
import cv2
import math
import numpy as np
import open3d as o3d
import time
from Environment.Actors.Vehicle import Vehicle

class Carla:
    def __init__(self) -> None:
        self.client = carla.Client('localhost', 2000)
        self.world = self.client.get_world()
        self.specator = self.world.get_spectator().get_transform().location
        self.spawn_points = self.world.get_map().get_spawn_points()
        spawn_point = random.choice(self.spawn_points)
        # spawn_point = carla.Transform(self.specator)
        self.actor = Vehicle(self.client,spawn_point, attach_sensors = True)

    def _game(self):

        while True:
            self.world.tick()
            if cv2.waitKey(1) == ord('q'):
                quit = True
                break
            # image = self.actor.semanticSegmentationSensor.get_image()
            rgb_camera = self.actor.rgbCameraSensor.get_image()
            self.actor.trafficLightSensor.update()
            Traffic_light = self.actor.trafficLightSensor.get_traffic_light_state()
            lane_invasion = self.actor.laneInvasionSensor.get_data()
            # Traffic_sign = self.actor.TrafficSignSensor.get_traffic_sign()
            # Radar = self.actor.radarSensor.get_detected_objects()
            # print(Radar)
            v = self.actor.vehicle.get_velocity()
            speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2),0)
            estimate_throttle = self.actor.maintain_speed(speed,20)
            self.actor.control(estimate_throttle,0)

            # segmented= cv2.resize(image.get('Front').get('image'), (640, 480))
            rgb_camera = cv2.resize(rgb_camera,(1080,720))
            if Traffic_light: 
                rgb_camera = cv2.putText(rgb_camera, f"Traffic Light: {str(Traffic_light)}", (30,50),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
            if lane_invasion[0]:
                rgb_camera = cv2.putText(rgb_camera, f'{str(lane_invasion[1].get("actor"))} crossed {str(lane_invasion[1].get("crossed_line"))}', (30,50),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)

            # new_img = np.concatenate((segmented,rgb_camera),axis=1)
            cv2.imshow('Carla', rgb_camera)


        # self.actor.destroy()



obj = Carla()
obj._game()