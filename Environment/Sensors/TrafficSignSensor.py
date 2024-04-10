import carla
import numpy as np
class TrafficSignSensor:
    def __init__(self, world,vehicle,blueprint):
        self.vehicle = vehicle
        self.world = world
        self.traffic_sign = self.world.get_actors().filter('traffic.traffic_signs')
        self.traffic_sign_state = {"type" : None, "value" : None}

    def update(self):
        vehicle_location = self.vehicle.get_location()
        vehicle_rotation = self.vehicle.get_transform().rotation.yaw
        relevant_traffic_sign = None
        min_distance = 30  # Define a maximum search radius

        for traffic_sign in self.traffic_signs:
            sign_location = traffic_sign.get_location()
            distance = vehicle_location.distance(sign_location)

            # Calculate the angle between the vehicle's forward direction and the vector to the traffic sign
            direction_vector = sign_location - vehicle_location
            angle = np.rad2deg(np.arctan2(direction_vector.y, direction_vector.x)) - vehicle_rotation

            # Normalize the angle to the range [-180, 180]
            angle = (angle + 180) % 360 - 180

            # Check if the traffic sign is within a certain distance and angle threshold
            if distance < min_distance and abs(angle) < 45:  # Use a smaller angle threshold
                min_distance = distance
                relevant_traffic_sign = traffic_sign

        if relevant_traffic_sign is not None:
            # Extract the type of the traffic sign from its type_id
            sign_type = relevant_traffic_sign.type_id.split('.')[-1]  # Extract the type from type_id
            self.traffic_sign_state = {"type": sign_type}
        else:
            self.traffic_sign_state = {"type": None}


    def get_traffic_sign(self):
        return self.traffic_sign_state

    def destroy(self):
        pass  # No specific destruction needed for this sensor
