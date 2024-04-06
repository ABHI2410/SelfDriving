import carla
class RadarSensor:
    def __init__(self, world, vehicle,blueprint):
        self.vehicle = vehicle
        self.world = world
        radar_blueprint = blueprint.find('sensor.other.radar')
        radar_blueprint.set_attribute('horizontal_fov', '35')
        radar_blueprint.set_attribute('vertical_fov', '20')
        self.sensor = self.world.spawn_actor(radar_blueprint, carla.Transform(carla.Location(x=2.0, z=1.0)), attach_to=self.vehicle)
        self.sensor.listen(lambda data: self.process_data(data))
        self.detected_objects = []

    def process_data(self, radar_data):
        self.detected_objects = [(d.azimuth, d.altitude, d.depth) for d in radar_data]

    def get_detected_objects(self):
        return self.detected_objects

    def destroy(self):
        self.sensor.destroy()


# A radar sensor can detect objects around the vehicle, providing information about their distance, velocity, and angle relative to the vehicle. This can be useful for collision avoidance and adaptive cruise control.