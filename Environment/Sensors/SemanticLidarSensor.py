import carla
import numpy as np
import cv2
class SemanticLidarSensor:
    def __init__(self, world, vehicle, blueprints):
        self.parent = vehicle
        self.world = world
        self.lidar_data = np.zeros((360, 1))  # Placeholder for lidar data
        self.semantic_lidar_bp = blueprints.find('sensor.lidar.ray_cast_semantic')
        # Set lidar attributes as needed
        self.semantic_lidar_bp.set_attribute('channels', '1')
        self.semantic_lidar_bp.set_attribute('points_per_second', '100000')
        self.semantic_lidar_bp.set_attribute('range', '100')
        # Define lidar sensor location and rotation
        lidar_transform = carla.Transform(carla.Location(z=2.0, x=0.0, y=0.0))
        # Spawn lidar sensor
        self.sensor = self.world.spawn_actor(self.semantic_lidar_bp, lidar_transform, attach_to=self.parent)
        # Listen to lidar data
        self.sensor.listen(lambda data: self._lidar_callback(data))

    def destroy(self):
        self.sensor.destroy()

    def get_lidar_data(self):
        return self.lidar_data

    def _lidar_callback(self, data):
        # Process incoming lidar data and create an image
        lidar_data = np.array(data)

        # Assuming each lidar point has a semantic label (e.g., 0 for road, 1 for vehicles, etc.)
        # You need to adjust this according to the format of your lidar data
        semantic_labels = lidar_data[:, 3]  # Assuming semantic labels are in the fourth column

        # Convert semantic labels to RGB colors (you can define your own color mapping)
        color_mapping = {
            0: (255, 255, 255),  # White for road
            1: (255, 0, 0),      # Red for vehicles
            # Add more color mappings as needed...
        }

        # Create an image from lidar data
        image_height = 360  # Adjust based on your lidar configuration
        image_width = 360   # Adjust based on your lidar configuration
        lidar_image = np.zeros((image_height, image_width, 3), dtype=np.uint8)

        for i, label in enumerate(semantic_labels):
            # Map each lidar point to its corresponding color
            color = color_mapping.get(label, (0, 0, 0))  # Default to black if label not found
            # Convert lidar point to image coordinates (adjust as needed)
            x = int(lidar_data[i, 0] * image_width / 100)  # Assuming lidar x coordinate is in meters
            y = int(lidar_data[i, 1] * image_height / 100)  # Assuming lidar y coordinate is in meters
            # Set pixel color in lidar image
            lidar_image[y, x] = color

        # Display or process the lidar image as needed
        cv2.imshow('Semantic LIDAR Image', lidar_image)
        cv2.waitKey(1)  # Display the image for a short time (adjust as needed)
