import carla as carla
import collections as collections
import math as math

class CollisionDetector:
    def __init__(self,world,vehicle,blueprints) -> None:
        self.parent = vehicle
        self.world = world
        self.history = []
        self.collisionSensor = blueprints.find('sensor.other.collision')
        self.sensor = self.world.spawn_actor(self.collisionSensor, carla.Transform(), attach_to=self.parent)
        self.sensor.listen(lambda event: self._collision_callback(event))
    
    def get_collision_history(self):
        history = collections.defaultdict(int)
        for frame, intensity in self.history:
            history[frame] += intensity
        return history

    def destroy(self):
        self.sensor.destroy()


    def _collision_callback(self, event):
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x**2 + impulse.y**2 + impulse.z**2)
        self.history.append((event.frame, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)
    

