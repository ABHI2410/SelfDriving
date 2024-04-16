import cv2
import torch
import numpy as np

class ProcessData():
    def __init__(self, rgb_img,scemantic_camers,lane_invasion,collisons,gnss_sensor,imu_sensor,scemantic_lidar,nearby_vehicle,traffic_light,speed,waypoints):
        self.rgb_img = rgb_img
        self.scemantic_camers = scemantic_camers
        self.lane_invasion = lane_invasion
        self.collisons = collisons
        self.gnss_sensor = gnss_sensor
        self.imu_sensor= imu_sensor
        self.scemantic_lidar= scemantic_camers
        self.nearby_objects = nearby_vehicle 
        self.traffic_light = traffic_light
        self.speed = speed
        self.waypoints = waypoints
    
    def normalized_image(self,image):
        # Convert image to float for calculations
        image = image.astype('float32')
        if np.min(image) >= 0.0 - 1e-5 and np.max(image) <= 1.0 + 1e-5:
            return image
        else:
            return image/255.00

    def lane_data(self,lane):
        lane_invade = 1 if lane[0] else 0
        lane_change = {'NONE': 0,'Right': 1,'Left' : 2,'Both' : 3}
        color = {'White' : 0,'Blue' : 1,'Green' : 2,'Red' : 3,'White' : 4,'Yellow' : 5,'Other' : 6}
        crossed_type = {'NONE' : 0,'Other' : 1,'Broken' : 2,'Solid' : 3,'SolidSolid' : 4,'SolidBroken' : 5,
                        'BrokenSolid' : 6,'BrokenBroken' : 7,'BottsDots' : 8,'Grass' : 9,'Curb' : 10}
        return [lane_invade,lane_change.get(lane[1].get('lane_change')),color.get(lane[1].get('mark_color')),crossed_type.get(lane[1].get('crossed_lane_types'))]
    def traffic_light_encoder(self,traffic_light):
        tl = {'Red': 0, "Yellow" :1, "Green" : 2 }
        return [tl.get(str(traffic_light))]
    def convert_to_tensors(self):
        self.rgb_tensor = torch.tensor(self.normalized_image(self.rgb_img))
        self.lane_invasion_tensor = torch.tensor(self.lane_data(self.lane_invasion))
        self.collisons_tensor = torch.tensor([self.collisons])
        self.nearby_objects_tensor =  torch.stack((torch.tensor(list(self.nearby_objects.keys())), torch.tensor(list(self.nearby_objects.values()))), dim=1)
        self.traffic_light_tensor = torch.tensor(self.traffic_light_encoder(self.traffic_light))
        self.speed_tensor = torch.tensor([self.speed])
        