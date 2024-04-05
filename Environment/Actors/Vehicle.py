import carla
import random
import numpy as np
from Environment.Sensors.CollisionDetector import CollisionDetector
from Environment.Sensors.RgbCameraSensor import RgbCameraSensor
from Environment.Sensors.GnssSensor import GnssSensor
from Environment.Sensors.ImuSensor import ImuSensor
from Environment.Sensors.SemanticLidarSensor import SemanticLidarSensor
from Environment.Sensors.DepthCameraSensor import DepthCameraSensor
from Environment.Sensors.TrafficLightSensor import TrafficLightSensor
from Environment.Sensors.SpeedLimitSensor import SpeedLimitSensor
from Environment.Sensors.RadarSensor import RadarSensor
from Environment.Sensors.LaneInvasionSensor import LaneInvasionSensor
# from Environment.Sensors.PedestrianDetectionSensor import PedestrianDetectionSensor
from Environment.Sensors.WeatherSensor import WeatherSensor


class Vehicle:
    def __init__(self, client, spawn_point):
        self.client = client
        self.world = client.get_world()
        self.blueprints = self.world.get_blueprint_library()
        vehicle_blueprint = random.choice(self.blueprints.filter('*cooper_s*'))
        self.vehicle = self.world.try_spawn_actor(vehicle_blueprint, spawn_point)
        self.attach_sensors()

    def attach_sensors(self):
        self.collisionSensor = CollisionDetector(self.world, self.vehicle, self.blueprints)
        self.rgbCameraSensor = RgbCameraSensor(self.world, self.vehicle, self.blueprints)
        self.gnssSensor = GnssSensor(self.world, self.vehicle, self.blueprints)
        self.imuSensor = ImuSensor(self.world, self.vehicle, self.blueprints)
        self.semanticLidarSensor = SemanticLidarSensor(self.world, self.vehicle, self.blueprints)
        self.depthCameraSensor = DepthCameraSensor(self.vehicle)
        self.trafficLightSensor = TrafficLightSensor(self.world, self.vehicle)
        self.speedLimitSensor = SpeedLimitSensor(self.vehicle)
        self.radarSensor = RadarSensor(self.world, self.vehicle)
        self.laneInvasionSensor = LaneInvasionSensor(self.world, self.vehicle)
        # self.pedestrianDetectionSensor = PedestrianDetectionSensor(self.world, self.vehicle)
        self.weatherSensor = WeatherSensor(self.world)

    def maintain_speed(self, speed, preferred_speed):
        if speed >= preferred_speed:
            return 0
        elif speed < preferred_speed - 2:
            return 0.8
        else:
            return 0.4

    def control(self, throttle, steering_angle):
        self.vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steering_angle))

    def destroy(self):
        self.vehicle.destroy()
        self.collisionSensor.destroy()
        self.rgbCameraSensor.destroy()
        self.gnssSensor.destroy()
        self.imuSensor.destroy()
        self.semanticLidarSensor.destroy()
        self.depthCameraSensor.destroy()
        self.trafficLightSensor.destroy()
        self.speedLimitSensor.destroy()
        self.radarSensor.destroy()
        self.laneInvasionSensor.destroy()
        # self.pedestrianDetectionSensor.destroy()
        self.weatherSensor.destroy()
