import carla

class SpeedLimitSensor:
    def __init__(self, world,vehicle,blueprint):
        self.vehicle = vehicle
        self.speed_limit = 0.0

    def update(self):
        waypoint = self.vehicle.get_world().get_map().get_waypoint(self.vehicle.get_location())
        if waypoint is not None:
            self.speed_limit = waypoint.speed_limit

    def get_speed_limit(self):
        return self.speed_limit

    def destroy(self):
        pass  # No specific destruction needed for this sensor
