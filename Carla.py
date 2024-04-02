import carla
import random
import cv2
import math
import numpy as np
from Environment.Actors.Vehicle import Vehicle

class Carla:
    def __init__(self) -> None:
        self.client = carla.Client('localhost', 2000)
        self.world = self.client.get_world()
        self.spawn_points = self.world.get_map().get_spawn_points()
        spawn_point = random.choice(self.spawn_points)
        self.actor = Vehicle(self.client,spawn_point)
    
    def _game(self):

        while True:
            self.world.tick()
            if cv2.waitKey(1) == ord('q'):
                quit = True
                break
            image = self.actor.rgbCameraSensor.get_image()
            steering_angle = 0
            v = self.actor.vehicle.get_velocity()
            speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2),0)
            image = cv2.putText(image, f"Speed: {str(int(speed))} kmh", (30,50),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
            estimate_throttle = self.actor.maintain_speed(speed,20)
            self.actor.control(estimate_throttle,0)
            cv2.imshow('Carla ',image)

        self.actor.destroy()



obj = Carla()
obj._game()
