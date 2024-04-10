import carla
import numpy as np
import cv2 
import colorsys

class VehicleCameras:
    def __init__(self, world, vehicle):
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

    def mask_specific_colors(self, image_array, colors_to_keep):
        # Create an empty mask
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        mask = np.zeros(image_array.shape[:2], dtype=np.uint8)

        # For each color, add it to the mask
        for color in colors_to_keep:
            color_mask = cv2.inRange(image_array, color, color)
            mask = cv2.bitwise_or(mask, color_mask)

        # mask = 255-mask    

        # Create a colored mask
        colored_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        # Apply the mask to the image
        masked_image = cv2.bitwise_and(image_array, colored_mask)
        return masked_image

    def process_image(self, image, name):
        # Convert the semantic segmentation image to a NumPy array
        image.convert(carla.ColorConverter.CityScapesPalette)
        image_array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        image_array = np.reshape(image_array, (image.height, image.width, 4))
        
        image_array = image_array[:, :, :3]  # Remove alpha channel
        colors_to_keep = [
            # np.array([128, 64, 128]),  # Road
            np.array([250, 170, 30]),  # Traffic light
            np.array([220, 220, 0]),   # Traffic sign
            np.array([220, 20, 60]),   # Pedestrian
            np.array([255, 0, 0]),     # Rider
            np.array([0, 0, 142]),     # Car
            np.array([0, 0, 70]),      # Truck
            np.array([0, 60, 100]),    # Bus
            np.array([0, 80, 100]),    # Train
            np.array([0, 0, 230]),     # Motorcycle
            np.array([119, 11, 32]),   # Bicycle
            np.array([45, 60, 150]),   # Water
            np.array([157, 234, 50]),  # RoadLine
            np.array([81, 0, 81]),     # Ground
        ]

        res = self.mask_specific_colors(image_array,colors_to_keep)

        self.cameras[name]['image'] = res

    def get_image(self):
        """Returns the semantic segmentation image for the specified camera position."""
        # if position in self.cameras:
        return self.cameras
        # else:
        #     return None

    def destroy(self):
        # Destroy all camera actors
        for camera_info in self.cameras.values():
            camera_info['camera'].destroy()
        self.cameras.clear()
