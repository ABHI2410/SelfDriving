import math
import cv2 
import time
import py_trees
import carla
import sys
sys.path.append("/home/carla/Desktop/Carla/scenario_runner/")
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenariomanager.scenario_manager import ScenarioManager
from srunner.scenariomanager.timer import GameTime
from srunner.scenariomanager.watchdog import Watchdog

class CustomScenarioManager(ScenarioManager):

    def maintain_speed(self, speed, preferred_speed):
        if speed >= preferred_speed:
            return 0
        elif speed < preferred_speed - 2:
            return 0.8
        else:
            return 0.4
        
    def _game(self,world,sensors):
        spectator = world.get_spectator()
        rgb_image = sensors.get("RGB Sensor").get_image()
        steering_angle = 0
        v = self.ego_vehicles[0].get_velocity()
        speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2),0)
        rgb_image = cv2.putText(rgb_image, f"Speed: {str(int(speed))} kmh", (30,50),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1,cv2.LINE_AA)
        
        estimate_throttle = self.maintain_speed(speed,20)
        self.ego_vehicles[0].apply_control(carla.VehicleControl(throttle=estimate_throttle, steer=0))
        vehicle_location = self.ego_vehicles[0].get_transform()
        spectator.set_transform(carla.Transform(carla.Location(vehicle_location.location.x-5,vehicle_location.location.y,vehicle_location.location.z+40) , carla.Rotation(pitch=-90)))

        # Adjust throttle based on speed limit and traffic light state
        # if traffic_light_state == carla.TrafficLightState.Red or speed > speed_limit:
        #     estimate_throttle = 0
        # else:
        #     estimate_throttle = self.scene.vehicle.maintain_speed(speed, 20)

        # self.scene.vehicle.control(estimate_throttle, steering_angle)

        # Display sensor data
        # cv2.imshow('Carla', rgb_image)

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
                self._tick_scenario(timestamp)

        self.cleanup()

        self.end_system_time = time.time()
        end_game_time = GameTime.get_time()

        self.scenario_duration_system = self.end_system_time - \
            self.start_system_time
        self.scenario_duration_game = end_game_time - start_game_time

        if self.scenario_tree.status == py_trees.common.Status.FAILURE:
            print("ScenarioManager: Terminated due to failure")