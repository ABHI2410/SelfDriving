
from datetime import datetime
import numpy as np
from matplotlib import cm
import open3d as o3d
import carla
import matplotlib.pyplot as plt


class SemanticLidarSensor:
    def __init__(self, world, vehicle, blueprints):
        self.parent = vehicle
        self.world = world
        self.semantic_lidar_bp = blueprints.find('sensor.lidar.ray_cast_semantic')
        

        self.VIRIDIS = np.array(cm.get_cmap('plasma').colors)
        self.VID_RANGE = np.linspace(0.0, 1.0, self.VIRIDIS.shape[0])
        self.LABEL_COLORS = np.array([
            (255, 255, 255), # None
            (70, 70, 70),    # Building
            (100, 40, 40),   # Fences
            (55, 90, 80),    # Other
            (220, 20, 60),   # Pedestrian
            (153, 153, 153), # Pole
            (157, 234, 50),  # RoadLines
            (128, 64, 128),  # Road
            (244, 35, 232),  # Sidewalk
            (107, 142, 35),  # Vegetation
            (0, 0, 142),     # Vehicle
            (102, 102, 156), # Wall
            (220, 220, 0),   # TrafficSign
            (70, 130, 180),  # Sky
            (81, 0, 81),     # Ground
            (150, 100, 100), # Bridge
            (230, 150, 140), # RailTrack
            (180, 165, 180), # GuardRail
            (250, 170, 30),  # TrafficLight
            (110, 190, 160), # Static
            (170, 120, 50),  # Dynamic
            (45, 60, 150),   # Water
            (145, 170, 100), # Terrain
            (68, 100, 18), # Traversable
            (80, 80, 0), #NonDrivable 
            (221, 35, 106),#Extra
            (0, 0, 0) #unkown
        ]) / 255.0 # normalize each channel [0-1] since is what Open3D uses


        # Set lidar attributes as needed
        self.semantic_lidar_bp.set_attribute('channels', '64')
        self.semantic_lidar_bp.set_attribute('points_per_second', '100000')
        self.semantic_lidar_bp.set_attribute('range', '100')
        self.semantic_lidar_bp.set_attribute('rotation_frequency','20')
        # self.semantic_lidar_bp.set_attribute('noise_stddev','0.20')

        # self.semantic_lidar_bp.set_attribute('upper_fov', 15.0)
        # self.semantic_lidar_bp.set_attribute('lower_fov', -25.0)

        # Define lidar sensor location and rotation
        lidar_transform = carla.Transform(carla.Location(z=1.8, x=-0.5, y=0.0))
        # Spawn lidar sensor
        self.sensor = self.world.spawn_actor(self.semantic_lidar_bp, lidar_transform, attach_to=self.parent)
        self.point_list = o3d.geometry.PointCloud()
        self.sensor.listen(lambda image: self._semantic_lidar_callback(image))

        


    def destroy(self):
        self.sensor.destroy()


    def get_image(self):
        # Listen to lidar data
        ## Semantic Lidar Sensor Still broken 
            # vis = o3d.visualization.Visualizer()
            # vis.create_window(visible = False)

            # vis.add_geometry(self.point_list)
            # # vis.update_geometry(self.point_list)
            # vis.poll_events()
            # vis.update_renderer()
            # vis.capture_screen_image("semantic_lidar_image.png")
        xyz_data = np.asarray(self.point_list.points)
        color_data = np.asarray(self.point_list.colors)
        # print(color_data)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xyz_data[:,  0], xyz_data[:,  1], xyz_data[:,  2], c=color_data ,s=1)
        # Convert the plot to a numpy array
        fig.canvas.draw()
        image_array = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image_array = image_array.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        # Close the plot to free resources
        plt.close(fig)

        # Return the image array
        return image_array

    def get_semantic_summary(self):
        """
        Returns a summary of the semantic point cloud data.
        """
        # Count the number of points belonging to each semantic category
        categories = np.unique(np.asarray(self.point_list.colors), axis=0)
        summary = {}
        for category in categories:
            count = np.sum(np.all(np.asarray(self.point_list.colors) == category, axis=1))
            summary[tuple(category)] = count
        return summary
    def _semantic_lidar_callback(self,point_cloud):
        """Prepares a point cloud with semantic segmentation
        colors ready to be consumed by Open3D"""
        data = np.frombuffer(point_cloud.raw_data, dtype=np.dtype([
            ('x', np.float32), ('y', np.float32), ('z', np.float32),
            ('CosAngle', np.float32), ('ObjIdx', np.uint32), ('ObjTag', np.uint32)]))
        # We're negating the y to correclty visualize a world that matches
        # what we see in Unreal since Open3D uses a right-handed coordinate system
        points = np.array([data['x'], -data['y'], data['z']]).T
        # # An example of adding some noise to our data if needed:
        # points += np.random.uniform(-0.05, 0.05, size=points.shape)

        # Colorize the pointcloud based on the CityScapes color palette
        labels = np.array(data['ObjTag'])
        int_color = self.LABEL_COLORS[np.clip(labels, 0, len(self.LABEL_COLORS) - 1)]


        # # In case you want to make the color intensity depending
        # # of the incident ray angle, you can use:
        int_color *= np.array(data['CosAngle'])[:, None]
        self.point_list.points = o3d.utility.Vector3dVector(points)
        self.point_list.colors = o3d.utility.Vector3dVector(int_color)
