import carla
import numpy as np

class DepthCameraSensor:
    def __init__(self, vehicle, height=960, width=1280, fov=110, location=(0.0, 0.0, 2.5), rotation=(0.0, 0.0, 0.0)):
        self.vehicle = vehicle
        self.height = height
        self.width = width
        self.fov = fov
        self.location = carla.Location(*location)
        self.rotation = carla.Rotation(*rotation)
        self.sensor = None
        self.init_sensor()
        self.average_distance = None  # Added to store the average distance to obstacles

    def init_sensor(self):
        """
        Initializes the depth camera sensor.
        """
        blueprint_library = self.vehicle.get_world().get_blueprint_library()
        depth_camera_bp = blueprint_library.find('sensor.camera.depth')
        depth_camera_bp.set_attribute('image_size_x', f'{self.width}')
        depth_camera_bp.set_attribute('image_size_y', f'{self.height}')
        depth_camera_bp.set_attribute('fov', f'{self.fov}')

        # Transform relative to the vehicle
        transform = carla.Transform(self.location, self.rotation)

        self.sensor = self.vehicle.get_world().spawn_actor(depth_camera_bp, transform, attach_to=self.vehicle)
        self.sensor.listen(lambda data: self.process_data(data))

    def process_data(self, data):
        """
        Processes the depth data from the depth camera sensor.
        """
        image_data = np.frombuffer(data.raw_data, dtype=np.dtype("uint8"))

        # Reshape and discard the alpha channel
        image_data = np.reshape(image_data, (data.height, data.width, 4))
        image_data = image_data[:, :, :3]
        # Convert to distances
        depth_data = np.dot(image_data[..., :3], [0.299, 0.587, 0.114])
        depth_data = depth_data * (1.0 / 255.0)  # Normalize

        # Calculate the average distance to obstacles
        self.average_distance = np.mean(depth_data)
        # print(f"Average distance to obstacles: {self.average_distance} meters")
        # if self.average_distance < 1.0:  # Threshold of 5 meters
        #     print("Obstacle detected ahead!")

    def get_average_distance(self):
        """Returns the average distance to obstacles."""
        return self.average_distance

    def destroy(self):
        """Destroys the sensor."""
        self.sensor.destroy()
