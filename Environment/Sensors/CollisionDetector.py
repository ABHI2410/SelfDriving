import carla as carla
import weakref as weakref
import collections as collections
import math as math

class CollisionDetector:
    def __init__(self,world,vehicle,blueprints) -> None:
        self.parent = vehicle
        self.world = world
        self.collisionSensor = blueprints.find('sensor.other.collision')
        self.sensor = self.world.spawn_actor(self.collisionSensor, carla.Transform(), attach_to=self.parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: CollisionDetector._collision_callback(weak_self, event))
    
    def get_collision_history(self):
        history = collections.defaultdict(int)
        for frame, intensity in self.history:
            history[frame] += intensity
        return history

    def destroy(self):
        self.sensor.destroy()

    @staticmethod
    def _collision_callback(weak_self, event):
        self = weak_self()
        if not self:
            return
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x**2 + impulse.y**2 + impulse.z**2)
        self.history.append((event.frame, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)
    

