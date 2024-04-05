import carla

class Rules:
    def __init__(self, vehicle):
        self.vehicle = vehicle

    def obey_speed_limit(self):
        """Rule to obey the speed limit."""
        speed_limit = self.vehicle.speedLimitSensor.get_speed_limit()
        current_speed = self.vehicle.get_speed()
        if current_speed > speed_limit:
            return False, f"Speeding: {current_speed} km/h > {speed_limit} km/h"
        return True, "Speed limit obeyed"

    def stop_at_red_traffic_light(self):
        """Rule to stop at red traffic lights."""
        traffic_light_state = self.vehicle.trafficLightSensor.get_traffic_light_state()
        if traffic_light_state == carla.TrafficLightState.Red:
            return False, "Vehicle did not stop at red traffic light"
        return True, "Stopped at red traffic light"

    def avoid_collisions(self):
        """Rule to avoid collisions."""
        collision_detected = self.vehicle.collisionSensor.has_collided()
        if collision_detected:
            return False, "Collision detected"
        return True, "No collisions"

    def stay_in_lane(self):
        """Rule to stay in lane."""
        lane_invasion_detected = self.vehicle.laneInvasionSensor.is_lane_invasion_detected()
        if lane_invasion_detected:
            return False, "Lane invasion detected"
        return True, "Stayed in lane"

    def evaluate_all_rules(self):
        """Evaluate all rules and return the results."""
        results = {
            "obey_speed_limit": self.obey_speed_limit(),
            "stop_at_red_traffic_light": self.stop_at_red_traffic_light(),
            "avoid_collisions": self.avoid_collisions(),
            "stay_in_lane": self.stay_in_lane()
        }
        return results
