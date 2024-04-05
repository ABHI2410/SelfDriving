import carla

class LaneInvasionSensor:
    def __init__(self, world, vehicle):
        self.vehicle = vehicle
        self.world = world
        self.lane_invasion_detected = False
        lane_invasion_blueprint = self.world.get_blueprint_library().find('sensor.other.lane_invasion')
        self.sensor = self.world.spawn_actor(lane_invasion_blueprint, carla.Transform(), attach_to=self.vehicle)
        self.sensor.listen(lambda event: self.process_event(event))

    def process_event(self, event):
        self.lane_invasion_detected = True

    def reset(self):
        self.lane_invasion_detected = False

    def is_lane_invasion_detected(self):
        return self.lane_invasion_detected

    def destroy(self):
        self.sensor.destroy()
