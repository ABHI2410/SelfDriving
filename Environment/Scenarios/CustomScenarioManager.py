import math
import cv2 
import time
import py_trees
import carla
import sys
import numpy as np
import open3d as o3d


from Constants import SCENARIO_RUNNER_PATH
sys.path.append(SCENARIO_RUNNER_PATH)
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenariomanager.scenario_manager import ScenarioManager
from srunner.scenariomanager.timer import GameTime
from srunner.scenariomanager.watchdog import Watchdog
from Environment.Sensors.CollisionDetector import CollisionDetector
from Environment.Sensors.RgbCameraSensor import RgbCameraSensor
from Environment.Sensors.GnssSensor import GnssSensor
from Environment.Sensors.ImuSensor import ImuSensor
from Environment.Sensors.SemanticLidarSensor import SemanticLidarSensor
from Environment.Sensors.DepthCameraSensor import DepthCameraSensor
from Environment.Sensors.TrafficLightSensor import TrafficLightSensor
from Environment.Sensors.TrafficSignSensor import TrafficSignSensor
from Environment.Sensors.RadarSensor import RadarSensor
from Environment.Sensors.LaneInvasionSensor import LaneInvasionSensor
from Environment.Sensors.WeatherSensor import WeatherSensor
from Environment.Sensors.VehicleCameras import VehicleCameras


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
        # self.start_visualization()
        spectator = world.get_spectator()
        rgb_img = sensors.get("RGB Sensor").get_image()
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
        img_to_show = scemantic_camers.get("Front").get("image")
        spectator.set_transform(carla.Transform(carla.Location(vehicle_location.location.x-5,vehicle_location.location.y,vehicle_location.location.z+40) , carla.Rotation(pitch=-90)))
        return (rgb_img,img_to_show)
    
    def attach_sensors(self,vehicle,world,blueprints):   
        collisionSensor = CollisionDetector(world, vehicle, blueprints)
        rgbCameraSensor = RgbCameraSensor(world, vehicle, blueprints)
        gnssSensor = GnssSensor(world, vehicle, blueprints)
        imuSensor = ImuSensor(world, vehicle, blueprints)
        semanticLidarSensor = SemanticLidarSensor(world, vehicle, blueprints)
        depthCameraSensor = DepthCameraSensor(world, vehicle, blueprints)
        trafficLightSensor = TrafficLightSensor(world, vehicle, blueprints)
        trafficSignSensor = TrafficSignSensor(world, vehicle, blueprints)
        radarSensor = RadarSensor(world, vehicle, blueprints)
        laneInvasionSensor = LaneInvasionSensor(world, vehicle,blueprints)
        weatherSensor = WeatherSensor(world)
        semanticSegmentationSensor = VehicleCameras(world, vehicle)
        return {
            "Collision_Sensor": collisionSensor,
            "Scemantic_Camera": semanticSegmentationSensor,
            "RGB Sensor" : rgbCameraSensor,
            "GNSS Sensor" : gnssSensor,
            "IMU Sensor" : imuSensor,
            "Semantic Lidar Sensor" : semanticLidarSensor,
            "Depth Camera Sensor" : depthCameraSensor,
            "Traffic Light Sensor" : trafficLightSensor,
            "Traffic Sign Sensor" : trafficSignSensor,
            "Radar Sensor" : radarSensor,
            "Lane Invsion Sensor" : laneInvasionSensor,
            "Weather Sensor" : weatherSensor
        }

    def load_scenario(self, scenario, agent=None):
        """
        Load a new scenario
        """
        self._reset()
        self.scenario = scenario
        self.scenario_tree = self.scenario.scenario_tree
        self.ego_vehicles = scenario.ego_vehicles
        self.other_actors = scenario.other_actors

        # To print the scenario tree uncomment the next line
        # py_trees.display.render_dot_tree(self.scenario_tree)
        world = CarlaDataProvider.get_world()
        blueprints = world.get_blueprint_library()
        self.sensors = self.attach_sensors(self.ego_vehicles[0], world,blueprints)

    def cleanup(self):
        """
        This function triggers a proper termination of a scenario
        """

        if self._watchdog is not None:
            self._watchdog.stop()
            self._watchdog = None

        if self.scenario is not None:
            self.scenario.terminate()

        if self.sensors is not None:
            for name,sensor in self.sensors.items():
                sensor.destroy()

        CarlaDataProvider.cleanup()

    def run_scenario(self):
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
                images = self._game(world,self.sensors)
                combined_image = np.concatenate((cv2.resize(images[0], (620, 480)),cv2.resize(images[1], (620, 480))),axis=1)
                cv2.imshow("carla", combined_image)
                cv2.waitKey(1)
                # self.vis.destroy_window()
                self._tick_scenario(timestamp)

        self.cleanup()

        self.end_system_time = time.time()
        end_game_time = GameTime.get_time()

        self.scenario_duration_system = self.end_system_time - \
            self.start_system_time
        self.scenario_duration_game = end_game_time - start_game_time

        if self.scenario_tree.status == py_trees.common.Status.FAILURE:
            print("ScenarioManager: Terminated due to failure")