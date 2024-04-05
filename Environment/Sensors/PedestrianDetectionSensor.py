import carla

class PedestrianDetectionSensor:
    def __init__(self, world, vehicle):
        self.vehicle = vehicle
        self.world = world
        self.pedestrians_detected = []
        pedestrian_detector_blueprint = self.world.get_blueprint_library().find('sensor.other.pedestrian_detector')
        self.sensor = self.world.spawn_actor(pedestrian_detector_blueprint, carla.Transform(), attach_to=self.vehicle)
        self.sensor.listen(lambda event: self.process_event(event))

    def process_event(self, event):
        self.pedestrians_detected = event.other_actors  # List of pedestrians detected

    def get_pedestrians_detected(self):
        return self.pedestrians_detected

    def destroy(self):
        self.sensor.destroy()
