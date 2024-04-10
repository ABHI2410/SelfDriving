import carla
import numpy as np

class RgbCameraSensor:
    def __init__(self, world, vehicle, blueprints):
        self.parent = vehicle
        self.world = world
        rgb_camera_bp = blueprints.find('sensor.camera.rgb')
        rgb_camera_bp.set_attribute('image_size_x', '1080')
        rgb_camera_bp.set_attribute('image_size_y', '720')
        rgb_camera_bp.set_attribute('fov', '110')
        transform = carla.Transform(carla.Location(z=3, x=-5))
        self.sensor = world.spawn_actor(rgb_camera_bp, transform, attach_to=vehicle)
        self.camera_data = {"image": np.zeros((720, 1080, 4))}
        self.sensor.listen(lambda event: self._rgb_camera_callback(self.camera_data, event))

    def destroy(self):
        """Destroys the sensor."""
        self.sensor.destroy()

    def get_image(self):
        """Returns the captured RGB image."""
        return self.camera_data['image']

    def get_processed_image(self):
        """Returns a processed version of the captured RGB image."""
        # Example processing: Convert to grayscale
        grayscale_image = np.dot(self.camera_data['image'][..., :3], [0.299, 0.587, 0.114])
        return grayscale_image

    def _rgb_camera_callback(self, camera_data, image):
        """Callback for processing camera images."""
        camera_data['image'] = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))[:, :, :3]
