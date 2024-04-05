import carla
import weakref
import math

class ImuSensor:
    def __init__(self, world, vehicle, blueprints):
        self.parent = vehicle
        self.world = world
        imu_blueprint = blueprints.find('sensor.other.imu')
        self.sensor = world.spawn_actor(imu_blueprint, carla.Transform(), attach_to=vehicle)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda sensor_data: ImuSensor._Imu_callback(weak_self, sensor_data))
        self.data = {"accelerometer": (0.0, 0.0, 0.0), "gyroscope": (0.0, 0.0, 0.0), "compass": 0.0}

    def get_data(self):
        """Returns all IMU data as a dictionary."""
        return self.data

    def destroy(self):
        """Destroys the sensor."""
        self.sensor.destroy()

    @staticmethod
    def _Imu_callback(weak_self, sensor_data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.data["accelerometer"] = (
            max(limits[0], min(limits[1], sensor_data.accelerometer.x)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.y)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.z)))
        self.data["gyroscope"] = (
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.z))))
        self.data["compass"] = math.degrees(sensor_data.compass)
