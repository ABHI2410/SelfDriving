import os
import cv2
import math
import carla
import numpy as np
import gymnasium as gym
import xml.etree.ElementTree as ET

from Actors.Vehicle import Vehicle

from srunner.scenariomanager.scenario_manager import ScenarioManager
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.tools.scenario_parser import ScenarioConfigurationParser

class Environemnt(gym.Env):
    def __init__(self) -> None:
        super().__init__()

    def load_scenarios_from_xml(self,path):
        tree = ET.parse(path)
        root = tree.getroot()
        scenarios = []
        for scenario in root.findall('scenario'):
            details = {
                'name': scenario.get('name'),
                'type': scenario.get('type'),
                'town': scenario.get('town'),
                'actors': []
            }
            # Extract ego vehicle and other actors
            ego = None
            for actor in scenario:
                actor_details = {
                    'x': float(actor.get('x')),
                    'y': float(actor.get('y')),
                    'z': float(actor.get('z')),
                    'yaw': float(actor.get('yaw')),
                    'model': actor.get('model'),
                    'is_ego': actor.tag == 'ego_vehicle'
                }
                details['actors'].append(actor_details)
            scenarios.append(details)
        return scenarios
    
    def setup_scenario(self,client, scenario):
        actors = []
        for actor_info in scenario['actors']:
            transform = carla.Transform(
                carla.Location(x=actor_info['x'], y=actor_info['y'], z=actor_info['z']),
                carla.Rotation(yaw=actor_info['yaw'])
            )
            vehicle = Vehicle(client, transform, actor_info['model'],is_ego=actor_info['is_ego'])
            actors.append(vehicle)
        return actors
    
    def run_scenario(self,scenario):
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        world = client.load_world(scenario['town'])
        try:
            actors = self.setup_scenario(client, scenario)
            vehicle = next((actor for actor in actors if actor.is_ego))
            print(vehicle)
            if vehicle is None:
                raise ValueError("No vehicle found in the scenario actors.")

            while True:
                world.tick()
                # Example of breaking the loop with a keyboard event in a non-blocking way
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Example sensor data retrieval
                image = vehicle.semanticSegmentationSensor.get_image()
                rgb_camera = vehicle.rgbCameraSensor.get_image()
                vehicle.trafficLightSensor.update()
                Traffic_light = vehicle.trafficLightSensor.get_traffic_light_state()
                lane_invasion = vehicle.laneInvasionSensor.get_data()
                v = vehicle.get_velocity()
                speed = round(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2), 0)
                estimate_throttle = vehicle.maintain_speed(speed, 20)
                vehicle.control(estimate_throttle, 0)

                # Visualization
                segmented = cv2.resize(image.get('Front').get('image'), (640, 480))
                rgb_camera = cv2.resize(rgb_camera, (640, 480))
                new_img = np.concatenate((segmented, rgb_camera), axis=1)
                cv2.imshow('Carla', new_img)

        finally:
            # Clean up all actors
            for actor in actors:
                actor.destroy()
            cv2.destroyAllWindows()

    def run(self):
        scenarios = self.load_scenarios_from_xml(os.path.join(os.getcwd(), "examples/NoSignalJunction.xml"))
        # Run a specific scenario
        for scenario in scenarios:
            if scenario['name'] == 'NoSignalJunctionCrossing':

                self.run_scenario(scenario)
                break



# obj = Environemnt()
# obj.run()


class AdvancedEnvironment(gym.Env):
    def __init__(self, carla_host='localhost', carla_port=2000):
        super().__init__()
        self.client = carla.Client(carla_host, carla_port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        # Initialize scenario manager without debug_mode in constructor
        self.scenario_manager = ScenarioManager(self.world)
        # Assuming there's a method to set debug mode, use it here if available
        self.scenario_manager.set_debug_mode(True)

    def load_and_run_scenario(self, config_path):
        scenario_configurations = ScenarioConfigurationParser.parse_scenario_configuration(config_path, self.world)
        for config in scenario_configurations:
            self.scenario_manager.load_scenario(config)
            self.scenario_manager.start_scenario()
            while not self.scenario_manager.scenario_completed():
                self.world.tick()
            self.scenario_manager.stop_scenario()
            self.scenario_manager.cleanup()

    def run(self):
        config_path = os.path.join(os.getcwd(), "scenario_configurations.xml")
        self.load_and_run_scenario(config_path)

# Usage
env = AdvancedEnvironment()
env.run()