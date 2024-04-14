
from datetime import datetime
import numpy as np
from matplotlib import cm
import open3d as o3d
import carla
import matplotlib.pyplot as plt


'''
0	Unlabeled	(0, 0, 0)
1	Roads	(128, 64, 128)
2	SideWalks	(244, 35, 232)
3	Building	(70, 70, 70)
4	Wall	(102, 102, 156)
5	Fence	(190, 153, 153)
6	Pole	(153, 153, 153)
7	TrafficLight	(250, 170, 30)
8	TrafficSign	(220, 220, 0)
9	Vegetation	(107, 142, 35)
10	Terrain	(152, 251, 152)
11	Sky	(70, 130, 180)
12	Pedestrian	(220, 20, 60)
13	Rider	(255, 0, 0)
14	Car	(0, 0, 142)
15	Truck	(0, 0, 70)
16	Bus	(0, 60, 100)
17	Train	(0, 60, 100)
18	Motorcycle	(0, 0, 230)
19	Bicycle	(119, 11, 32)
20	Static	(110, 190, 160)
21	Dynamic	(170, 120, 50)
22	Other	(55, 90, 80)
23	Water	(45, 60, 150)
24	RoadLine	(157, 234, 50)
25	Ground	(81, 0, 81)
26	Bridge	(150, 100, 100)
27	RailTrack	(230, 150, 140)
28	GuardRail	(180, 165, 180)

'''

class SemanticLidarSensor:
    def __init__(self, world, vehicle, blueprints):
        self.parent = vehicle
        self.world = world
        self.semantic_lidar_bp = blueprints.find('sensor.lidar.ray_cast_semantic')
        self.semantic_lidar_bp.set_attribute('channels', '32')
        self.semantic_lidar_bp.set_attribute('points_per_second', '100000')
        self.semantic_lidar_bp.set_attribute('range', '100')
        self.semantic_lidar_bp.set_attribute('rotation_frequency', '20')
        self.semantic_lidar_bp.set_attribute('upper_fov', '15.0')
        self.semantic_lidar_bp.set_attribute('lower_fov', '-25.0')
        
        lidar_transform = carla.Transform(carla.Location(z=2.5))
        self.sensor = self.world.spawn_actor(self.semantic_lidar_bp, lidar_transform, attach_to=self.parent)
        self.sensor.listen(self._semantic_lidar_callback)
        self.vehicle_positions = {}
        self.semantic_colors = {
            0: (0, 0, 0), 1: (128, 64, 128), 2: (244, 35, 232), 3: (70, 70, 70),
            4: (102, 102, 156), 5: (190, 153, 153), 6: (153, 153, 153), 7: (250, 170, 30),
            8: (220, 220, 0), 9: (107, 142, 35), 10: (152, 251, 152), 11: (70, 130, 180),
            12: (220, 20, 60), 13: (255, 0, 0), 14: (0, 0, 142), 15: (0, 0, 70),
            16: (0, 60, 100), 17: (0, 60, 100), 18: (0, 0, 230), 19: (119, 11, 32),
            20: (110, 190, 160), 21: (170, 120, 50), 22: (55, 90, 80), 23: (45, 60, 150),
            24: (157, 234, 50), 25: (81, 0, 81), 26: (150, 100, 100), 27: (230, 150, 140),
            28: (180, 165, 180)
        }

    def destroy(self):
        self.sensor.stop()
        self.sensor.destroy()
 
    def _semantic_lidar_callback(self, point_cloud):
        data = np.frombuffer(point_cloud.raw_data, dtype=np.dtype([
            ('x', np.float32), ('y', np.float32), ('z', np.float32),
            ('CosAngle', np.float32), ('ObjIdx', np.uint32), ('ObjTag', np.uint32)]))

        points = np.array([data['x'], -data['y'], data['z']]).T
        labels = data['ObjTag']

        colors = np.array([self.semantic_colors.get(tag, (0, 0, 0)) for tag in labels]) / 255.0  # Normalize colors for Open3D

        # Create point cloud object
        self.pcd = o3d.geometry.PointCloud()
        self.pcd.points = o3d.utility.Vector3dVector(points)
        self.pcd.colors = o3d.utility.Vector3dVector(colors)

        ego_location = self.parent.get_location()
        ego_position = np.array([ego_location.x, ego_location.y, ego_location.z])
        distances = np.linalg.norm(points - ego_position, axis=1)

        # Reset the distances dictionary for fresh data
        self.last_object_distances = {}

        # Store only the last recorded distances for each object type
        for label, distance in zip(labels, distances):
            self.last_object_distances[label] = distance


    def get_vehicle_distances(self):
        return self.last_object_distances
    
    def _get_point_cloud(self):
        return self.pcd
        
