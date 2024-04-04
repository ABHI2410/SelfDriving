import carla


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
        Processes the data from the depth camera sensor.
        """
        # I need to add the logic to process the depth image data
        # For simplicity, we're just printing the frame number
        print(f"Depth Camera frame {data.frame}")
