import carla

class LaneInvasionSensor:
    def __init__(self, world, vehicle,blueprint):
        self.vehicle = vehicle
        self.world = world
        self.history = []
        self.lane_invasion = None
        self.lane_invasion_detected = False
        lane_invasion_blueprint = blueprint.find('sensor.other.lane_invasion')
        self.sensor = self.world.spawn_actor(lane_invasion_blueprint, carla.Transform(), attach_to=self.vehicle)
        self.sensor.listen(lambda event: self.process_event(event))

    def process_event(self, event):
        self.lane_invasion_detected = False
        self.lane_invasion = None
        crossing_type = [str(lane_marking.type) for lane_marking in event.crossed_lane_markings]
        if crossing_type:
            self.lane_invasion_detected = True
            invasion_detail = {
                'frame': event.frame,
                'timestamp': event.timestamp,
                'crossed_lane_types': crossing_type[0],
                'mark_color' : [str(lane_marking.color) for lane_marking in event.crossed_lane_markings][0],
                'lane_change' : [str(lane_marking.lane_change) for lane_marking in event.crossed_lane_markings][0]
            }
            self.lane_invasion = invasion_detail
            self.history.appeend(self.lane_invasion)
    
    def reset(self):
        self.lane_invasion_detected = False

    def get_data(self):
        return (self.lane_invasion_detected,self.lane_invasion)


    def destroy(self):
        self.sensor.destroy()
