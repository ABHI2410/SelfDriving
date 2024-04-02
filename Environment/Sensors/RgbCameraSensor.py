import carla as carla
import collections as collections
import math as math
import numpy as np

class RgbCameraSensor:
    def __init__(self,world,vehicle,blueprints) -> None:
        self.parent = vehicle
        self.world = world
        self.cameraData = {"image": np.zeros((1080, 720, 4))}
        self.RgbCameraSensor = blueprints.find('sensor.camera.rgb')
        self.RgbCameraSensor.set_attribute('image_size_x', '1080')
        self.RgbCameraSensor.set_attribute('image_size_y', '720')
        self.RgbCameraSensor.set_attribute('fov', '110')
        transform = carla.Transform(carla.Location(z=3, x=-5))
        self.sensor = self.world.spawn_actor(self.RgbCameraSensor, transform, attach_to=self.parent)
        self.camera_data = {"image": np.zeros((480, 640, 4))}
        self.sensor.listen(lambda event: self._rgbCamera_callback(self.camera_data, event))
    
    def destroy(self):
        self.sensor.destroy()
        
    def get_image(self):
        return self.camera_data['image']

    def _rgbCamera_callback(self,camera_data, image):
        self.camera_data['image'] = np.reshape(np.copy(image.raw_data), (image.height, image.width, 4))
