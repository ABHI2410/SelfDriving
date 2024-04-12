import carla

class Rules:
    def __init__(self, vehicle):
        self.vehicle = vehicle

    def obey_speed_limit(self):
        """Rule to obey the speed limit."""
        speed_limit = self.vehicle.speedLimitSensor.get_speed_limit()
        current_speed = self.vehicle.get_speed()
        if current_speed > speed_limit:
            return -100, "Speeding"  # Negative reward for speeding
        return 5, "Speed limit obeyed"  # Positive reward for obeying speed limit

    def stop_at_red_traffic_light(self):
        """Rule to stop at red traffic lights."""
        traffic_light_state = self.vehicle.trafficLightSensor.get_traffic_light_state()
        if traffic_light_state == carla.TrafficLightState.Red:
            return -100, "Red light violation"  # Negative reward for running a red light
        return 5, "Stopped at red light"  # Positive reward for stopping at a red light

    def avoid_collisions(self):
        """Rule to avoid collisions."""
        collision_detected = self.vehicle.collisionSensor.has_collided()
        if collision_detected:
            return -200, "Collision"  # Large negative reward for collisions
        return 10, "No collisions"  # Positive reward for avoiding collisions

    def stay_in_lane(self):
        """Rule to stay in lane."""
        lane_invasion_detected = self.vehicle.laneInvasionSensor.is_lane_invasion_detected()
        if lane_invasion_detected:
            return -50, "Lane invasion"  # Negative reward for lane invasion
        return 5, "Stayed in lane"  # Positive reward for staying in lane

    def evaluate_all_rules(self):
        """Evaluate all rules and return the total reward."""
        total_reward = 0
        messages = []
        for rule_method in [self.obey_speed_limit, self.stop_at_red_traffic_light, self.avoid_collisions, self.stay_in_lane]:
            reward, message = rule_method()
            total_reward += reward
            messages.append(message)
        return total_reward, messages
