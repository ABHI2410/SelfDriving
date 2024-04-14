import math
import cv2 
import time
import py_trees
import carla
import sys
import open3d as o3d

from Constants import SCENARIO_RUNNER_PATH
sys.path.append(SCENARIO_RUNNER_PATH)
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenariomanager.scenario_manager import ScenarioManager
from srunner.scenariomanager.timer import GameTime
from srunner.scenariomanager.watchdog import Watchdog

class CustomScenarioManager(ScenarioManager):


    def __init__(self,debug, sync, timeout):
        super().__init__()
        self.vis = None
        self.pcd = None

    def visualize_point_cloud(self, pcd):
        if pcd is not None and not pcd.is_empty():
            self.vis.clear_geometries()  # Clear previous geometries
            self.vis.add_geometry(pcd)  # Add new or updated point cloud
            self.vis.poll_events()
            self.vis.update_renderer()
        else:
            print("No points to display in the point cloud.")

    def start_visualization(self):
        if self.vis is None:
            self.vis = o3d.visualization.Visualizer()
            self.vis.create_window()

    def stop_visualization(self):
        if self.vis is not None:
            self.vis.destroy_window()
            self.vis = None

    def maintain_speed(self, speed, preferred_speed):
        if speed >= preferred_speed:
            return 0
        elif speed < preferred_speed - 2:
            return 0.8
        else:
            return 0.4
        
    def _game(self,world,sensors):
        self.start_visualization()
        spectator = world.get_spectator()
        scemantic_camers = sensors.get("Scemantic_Camera").get_image()
        lane_invasion = sensors.get("Lane Invsion Sensor").get_data()
        collisons = sensors.get("Collision_Sensor").get_collision_history()
        gnss_sensor = sensors.get("GNSS Sensor").get_location()
        imu_sensor = sensors.get("IMU Sensor").get_data()
        scemantic_lidar = sensors.get("Semantic Lidar Sensor")._get_point_cloud()
        nearby_vehicle = sensors.get("Semantic Lidar Sensor").get_vehicle_distances()
        traffic_light = sensors.get("Traffic Light Sensor").get_traffic_light_state()
        # self.visualize_point_cloud(scemantic_lidar)
        # self.update_point_cloud(self.vis,scemantic_lidar,scemantic_lidar)
        v = self.ego_vehicles[0].get_velocity()
        speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2),0)
        estimate_throttle = self.maintain_speed(speed,40)
        self.ego_vehicles[0].apply_control(carla.VehicleControl(throttle=estimate_throttle, steer=0))
        vehicle_location = self.ego_vehicles[0].get_transform()
        spectator.set_transform(carla.Transform(carla.Location(vehicle_location.location.x-5,vehicle_location.location.y,vehicle_location.location.z+40) , carla.Rotation(pitch=-90)))


    def run_scenario(self,sensors):
        """
        Trigger the start of the scenario and wait for it to finish/fail
        """
        print("ScenarioManager: Running scenario {}".format(self.scenario_tree.name))
        self.start_system_time = time.time()
        start_game_time = GameTime.get_time()

        self._watchdog = Watchdog(float(self._timeout))
        self._watchdog.start()
        self._running = True

        while self._running:
            timestamp = None
            world = CarlaDataProvider.get_world()
            if world:
                snapshot = world.get_snapshot()
                if snapshot:
                    timestamp = snapshot.timestamp
            if timestamp:
                self._game(world,sensors)
                self.vis.destroy_window()
                self._tick_scenario(timestamp)

        self.cleanup()

        self.end_system_time = time.time()
        end_game_time = GameTime.get_time()

        self.scenario_duration_system = self.end_system_time - \
            self.start_system_time
        self.scenario_duration_game = end_game_time - start_game_time

        if self.scenario_tree.status == py_trees.common.Status.FAILURE:
            print("ScenarioManager: Terminated due to failure")