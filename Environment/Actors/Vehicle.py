import carla
import random
import numpy as np
# from Sensors.CollisionDetector import CollisionDetector
# from Sensors.RgbCameraSensor import RgbCameraSensor
# from Sensors.GnssSensor import GnssSensor
# from Sensors.ImuSensor import ImuSensor
# from Sensors.SemanticLidarSensor import SemanticLidarSensor
# from Sensors.DepthCameraSensor import DepthCameraSensor
# from Sensors.TrafficLightSensor import TrafficLightSensor
# from Sensors.TrafficSignSensor import TrafficSignSensor
# from Sensors.RadarSensor import RadarSensor
# from Sensors.LaneInvasionSensor import LaneInvasionSensor
# from Sensors.WeatherSensor import WeatherSensor
# from Sensors.VehicleCameras import VehicleCameras

from Environment.Sensors.CollisionDetector import CollisionDetector
from Environment.Sensors.RgbCameraSensor import RgbCameraSensor
from Environment.Sensors.GnssSensor import GnssSensor
from Environment.Sensors.ImuSensor import ImuSensor
from Environment.Sensors.SemanticLidarSensor import SemanticLidarSensor
from Environment.Sensors.DepthCameraSensor import DepthCameraSensor
from Environment.Sensors.TrafficLightSensor import TrafficLightSensor
from Environment.Sensors.TrafficSignSensor import TrafficSignSensor
from Environment.Sensors.RadarSensor import RadarSensor
from Environment.Sensors.LaneInvasionSensor import LaneInvasionSensor
from Environment.Sensors.WeatherSensor import WeatherSensor
from Environment.Sensors.VehicleCameras import VehicleCameras


class Vehicle:
    def __init__(self, client, spawn_point, model,is_ego=False):
        self.client = client
        self.world = client.get_world()
        self.blueprints = self.world.get_blueprint_library()
        vehicle_blueprint = self.blueprints.find(model)
        self.type_id = vehicle_blueprint.id 
        self.vehicle = self.world.try_spawn_actor(vehicle_blueprint, spawn_point)
        self.is_ego = is_ego
        if self.is_ego:
            self.attach_sensors()

    def attach_sensors(self):   
        self.collisionSensor = CollisionDetector(self.world, self.vehicle, self.blueprints)
        self.rgbCameraSensor = RgbCameraSensor(self.world, self.vehicle, self.blueprints)
        self.gnssSensor = GnssSensor(self.world, self.vehicle, self.blueprints)
        self.imuSensor = ImuSensor(self.world, self.vehicle, self.blueprints)
        self.semanticLidarSensor = SemanticLidarSensor(self.world, self.vehicle, self.blueprints)
        self.depthCameraSensor = DepthCameraSensor(self.world, self.vehicle, self.blueprints)
        self.trafficLightSensor = TrafficLightSensor(self.world, self.vehicle, self.blueprints)
        self.TrafficSignSensor = TrafficSignSensor(self.world, self.vehicle, self.blueprints)
        self.radarSensor = RadarSensor(self.world, self.vehicle, self.blueprints)
        self.laneInvasionSensor = LaneInvasionSensor(self.world, self.vehicle,self.blueprints)
        self.weatherSensor = WeatherSensor(self.world)
        self.semanticSegmentationSensor = VehicleCameras(self.world, self.vehicle)

    def maintain_speed(self, speed, preferred_speed):
        if speed >= preferred_speed:
            return 0
        elif speed < preferred_speed - 2:
            return 0.8
        else:
            return 0.4

    def control(self, throttle, steering_angle):
        self.vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steering_angle))
    
    
    def get_velocity(self):
        """ Returns the velocity of the vehicle as a carla.Vector3D object. """
        return self.vehicle.get_velocity()

    def destroy(self):
        if self.is_ego:
            self.vehicle.destroy()
            self.collisionSensor.destroy()
            self.rgbCameraSensor.destroy()
            self.gnssSensor.destroy()
            self.imuSensor.destroy()
            self.semanticLidarSensor.destroy()
            self.depthCameraSensor.destroy()
            self.trafficLightSensor.destroy()
            self.TrafficSignSensor.destroy()
            self.radarSensor.destroy()
            self.laneInvasionSensor.destroy()
            self.weatherSensor.destroy()
