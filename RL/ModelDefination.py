import cv2
import torch
import numpy as np

class ProcessData():
    def __init__(self,scemantic_camers,lane_invasion,collisons,nearby_vehicle,traffic_light,speed,waypoints):
        self.scemantic_camers = scemantic_camers
        self.lane_invasion = lane_invasion
        self.collisons = collisons
        self.nearby_objects = nearby_vehicle 
        self.traffic_light = traffic_light
        self.speed = speed
        self.waypoints = waypoints
        self.convert_to_np_array()
    
    def normalized_image(self,image):
        # Convert image to float for calculations
        image = image.astype('float32')
        if np.min(image) >= 0.0 - 1e-5 and np.max(image) <= 1.0 + 1e-5:
            return cv2.resize(image, (480,640))
        else:
            return cv2.resize(image/255.00, (480,640))

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
    
    def convert_to_np_array(self):
        self.rgb_array = np.array(self.normalized_image(self.rgb_img))
        self.lane_invasion_array = np.array(self.lane_data(self.lane_invasion))
        self.collisons_array = np.array([self.collisons])
        self.nearby_objects_array =  torch.stack((np.array(list(self.nearby_objects.keys())), np.array(list(self.nearby_objects.values()))), dim=1)
        self.traffic_light_array = np.array(self.traffic_light_encoder(self.traffic_light))
        self.speed_array = np.array([self.speed])
        self.scemantic_camera_front_left_array = np.array(self.normalized_image(self.scemantic_camers.get("Front Left").get("image")))
        self.scemantic_camera_front_array = np.array(self.normalized_image(self.scemantic_camers.get("Front").get("image")))
        self.scemantic_camera_front_right_array = np.array(self.normalized_image(self.scemantic_camers.get("Front Right").get("image")))
        self.scemantic_camera_left_array = np.array(self.normalized_image(self.scemantic_camers.get("Left").get("image")))
        self.scemantic_camera_right_array = np.array(self.normalized_image(self.scemantic_camers.get("Right").get("image")))
        self.scemantic_camera_back_left_array = np.array(self.normalized_image(self.scemantic_camers.get("Back Left").get("image")))
        self.scemantic_camera_back_array = np.array(self.normalized_image(self.scemantic_camers.get("Back").get("image")))
        self.scemantic_camera_back_right_array = np.array(self.normalized_image(self.scemantic_camers.get("Back Right").get("image")))
        self.waypoints = np.array(self.waypoints.location,self.waypoints.transform,self.waypoints.road_id,self.waypoints.lane_id,
                    self.waypoints.lane_change, self.waypoints.lane_type)
    def _get_data(self):
        return [
            np.array(self.lane_invasion_array).reshape(1,),
            np.array(self.collisons_array).reshape(1,),
            np.pad(self.nearby_objects_array[:10],(0, 10 - len(self.nearby_objects)), mode='constant'),
            np.array(self.traffic_light_array).reshape(1,),
            np.array(self.speed_array).reshape(1,),
            cv2.resize(self.scemantic_camera_front_array, (480, 360)),
            cv2.resize(self.scemantic_camera_front_left_array, (480, 360)),
            cv2.resize(self.scemantic_camera_front_right_array, (480, 360)),
            cv2.resize( self.scemantic_camera_left_array, (480, 360)),
            cv2.resize(self.scemantic_camera_right_array, (480, 360)),
            cv2.resize(self.scemantic_camera_back_left_array, (480, 360)),
            cv2.resize(self.scemantic_camera_back_array, (480, 360)),
            cv2.resize(self.scemantic_camera_back_right_array, (480, 360)),
            np.array(self.waypoints).reshape(1,)
        ]