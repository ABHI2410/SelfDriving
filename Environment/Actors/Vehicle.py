import carla
import random
import numpy as np
from Environment.Sensors import CollisionDetector,RgbCameraSensor,GnssSensor,ImuSensor,SemanticLidarSensor

class Vehicle:
    def __init__(self, client, spawn_point):
        self.client = client
        self.world = client.get_world()
        self.blueprints = self.world.get_blueprint_library()
        vehicelBlueprint = random.choice(self.blueprints.filter('vehicle.*'))
        self.vehicle = self.world.try_spawn_actor(vehicelBlueprint, spawn_point)
        self.attach_sensors()

    def attach_sensors(self):
        self.collisionSensor = CollisionDetector.CollisionDetector(self.world,self.vehicle,self.blueprints)
        self.rgbCameraSensor = RgbCameraSensor.RgbCameraSensor(self.world,self.vehicle,self.blueprints)
        self.gnssSensor = GnssSensor.GnssSensor(self.world,self.vehicle,self.blueprints)
        self.imuSensor = ImuSensor.ImuSensor(self.world,self.vehicle,self.blueprints)
        self.semanticLidarSensor = SemanticLidarSensor.SemanticLidarSensor(self.world,self.vehicle,self.blueprints)

    def maintain_speed (self,speed,prefered_speed):
        if speed >= prefered_speed:
            return 0
        elif speed < prefered_speed - 2:
            return 0.8
        else :
            return 0.4
    
    def control(self,throttle,steering_angle):
        self.vehicle.apply_control(carla.VehicleControl(
            throttle = throttle,
            steer = steering_angle
        ))
    
    def destroy(self):
        self.vehicle.destroy()
        self.collisionSensor.destroy()
        self.rgbCameraSensor.destroy()
        self.gnssSensor.destroy()
        self.imuSensor.destroy()
        self.semanticLidarSensor.destroy()