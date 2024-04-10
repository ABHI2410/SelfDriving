import carla

class LaneInvasionSensor:
    def __init__(self, world, vehicle,blueprint):
        self.vehicle = vehicle
        self.world = world
        self.lane_invasion_history = []
        self.lane_invasion_detected = False
        self.lane_invasion = {"actor" : None, "crossed_line" : None}
        lane_invasion_blueprint = blueprint.find('sensor.other.lane_invasion')
        self.sensor = self.world.spawn_actor(lane_invasion_blueprint, carla.Transform(), attach_to=self.vehicle)
        self.sensor.listen(lambda event: self.process_event(event))

    def process_event(self, event):
        self.lane_invasion = {"actor" : event.actor , "crossed_line": event.crossed_lane_markings }
        self.lane_invasion_detected = True

    def reset(self):
        self.lane_invasion_detected = False

    def get_data(self):
        return (self.lane_invasion_detected, self.lane_invasion)

    def destroy(self):
        self.sensor.destroy()
