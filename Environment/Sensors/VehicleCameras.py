import carla
import numpy as np

class VehicleCameras:
    def __init__(self, vehicle, world):
        self.vehicle = vehicle
        self.world = world
        self.cameras = {}
        self.attach_cameras()

    def attach_cameras(self):
        bounding_box = self.vehicle.bounding_box
        vehicle_size = bounding_box.extent.x, bounding_box.extent.y, bounding_box.extent.z

        # Camera positions and orientations
        camera_positions = {
            'Front': carla.Transform(carla.Location(x=vehicle_size[0], z=vehicle_size[2])),
            'Front Left': carla.Transform(carla.Location(x=vehicle_size[0], y=-vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=45)),
            'Front Right': carla.Transform(carla.Location(x=vehicle_size[0], y=vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=-45)),
            'Left': carla.Transform(carla.Location(y=-vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=90)),
            'Right': carla.Transform(carla.Location(y=vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=-90)),
            'Back Left': carla.Transform(carla.Location(x=-vehicle_size[0], y=-vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=135)),
            'Back Right': carla.Transform(carla.Location(x=-vehicle_size[0], y=vehicle_size[1], z=vehicle_size[2]), carla.Rotation(yaw=-135)),
            'Back': carla.Transform(carla.Location(x=-vehicle_size[0], z=vehicle_size[2]), carla.Rotation(yaw=180)),
        }

        # Camera blueprint and settings
        camera_bp = self.world.get_blueprint_library().find('sensor.camera.semantic_segmentation')
        camera_bp.set_attribute('image_size_x', '1280')
        camera_bp.set_attribute('image_size_y', '720')
        camera_bp.set_attribute('fov', '110')

        # Attach cameras and assign names based on positions
        for position, transform in camera_positions.items():
            camera = self.world.spawn_actor(camera_bp, transform, attach_to=self.vehicle)
            camera.listen(lambda image, name=position: self.process_image(image, name))
            self.cameras[position] = {'camera': camera, 'image': None}

    def process_image(self, image, name):
        # Convert the semantic segmentation image to a NumPy array
        image_array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        image_array = np.reshape(image_array, (image.height, image.width, 4))
        image_array = image_array[:, :, :3]  # Remove alpha channel
        self.cameras[name]['image'] = image_array

    def get_image(self, position):
        """Returns the semantic segmentation image for the specified camera position."""
        if position in self.cameras:
            return self.cameras[position]['image']
        else:
            return None

    def destroy(self):
        # Destroy all camera actors
        for camera_info in self.cameras.values():
            camera_info['camera'].destroy()
        self.cameras.clear()
