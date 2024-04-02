import carla as carla
import weakref as weakref
import math as math

class ImuSensor(object):
    def __init__(self, world,vehicle,blueprints):
        self.parent = vehicle
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        world = world
        imuBluePrint = blueprints.find('sensor.other.imu')
        self.sensor = world.spawn_actor(imuBluePrint, carla.Transform(), attach_to=self.parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda sensor_data: ImuSensor._Imu_callback(weak_self, sensor_data))
    
    def get_accelerometer_data(self):
        return self.accelerometer
    
    def get_gyroscope_data(self):
        return self.gyroscope
    
    def get_compass_data(self):
        return self.compass

    def destroy(self):
        self.sensor.destroy()
        
    @staticmethod
    def _Imu_callback(weak_self, sensor_data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.accelerometer = (
            max(limits[0], min(limits[1], sensor_data.accelerometer.x)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.y)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.z)))
        self.gyroscope = (
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.z))))
        self.compass = math.degrees(sensor_data.compass)