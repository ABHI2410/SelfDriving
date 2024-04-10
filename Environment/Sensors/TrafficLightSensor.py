import carla
import numpy as np

class TrafficLightSensor:
    def __init__(self, world, vehicle,blueprint):
        self.vehicle = vehicle
        self.world = world
        self.traffic_lights = self.world.get_actors().filter('traffic.traffic_light')
        self.traffic_light_state = None

    def update(self):
        vehicle_location = self.vehicle.get_location()
        vehicle_rotation = self.vehicle.get_transform().rotation.yaw
        approaching_traffic_light = None

        for traffic_light in self.traffic_lights:
            tl_location = traffic_light.get_location()
            distance = vehicle_location.distance(tl_location)

            # Calculate the angle between the vehicle's forward direction and the vector to the traffic light
            direction_vector = tl_location - vehicle_location
            angle = np.rad2deg(np.arctan2(direction_vector.y, direction_vector.x)) - vehicle_rotation

            # Normalize the angle to the range [-180, 180]
            angle = (angle + 180) % 360 - 180

            # Check if the traffic light is within a certain distance and angle threshold (e.g., 30 meters and 45 degrees)
            if distance < 30 and abs(angle) < 45:
                approaching_traffic_light = traffic_light
                break
        if approaching_traffic_light is not None:
            tl_state = approaching_traffic_light.get_state()

            if tl_state == carla.TrafficLightState.Red:
                self.traffic_light_state = "Red"
            elif tl_state == carla.TrafficLightState.Yellow:
                self.traffic_light_state = "Yellow"
            elif tl_state == carla.TrafficLightState.Green:
                self.traffic_light_state = "Green"
        else:
            self.traffic_light_state = None


    def get_traffic_light_state(self):
        return self.traffic_light_state

    def destroy(self):
        pass  # No specific destruction needed for this sensor
