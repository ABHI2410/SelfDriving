import carla

class TrafficLightSensor:
    def __init__(self, world, vehicle,blueprint):
        self.vehicle = vehicle
        self.world = world
        self.traffic_light_state = "Unknown"

    def update(self):
        traffic_light = self.vehicle.get_traffic_light()
        if traffic_light is not None:
            self.traffic_light_state = traffic_light.get_state()

    def get_traffic_light_state(self):
        return self.traffic_light_state

    def destroy(self):
        pass  # No specific destruction needed for this sensor
