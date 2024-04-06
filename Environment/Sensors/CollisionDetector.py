import carla
import collections
import math


class CollisionDetector:
    def __init__(self, world, vehicle, blueprints):
        print(type(vehicle))
        self.parent = vehicle
        self.world = world
        self.history = []
        self.collisionSensor = blueprints.find('sensor.other.collision')
        self.sensor = self.world.spawn_actor(self.collisionSensor, carla.Transform(), attach_to=self.parent)
        self.sensor.listen(lambda event: self._collision_callback(event))

    def get_collision_history(self):
        """Returns the total intensity of collisions in the latest tick."""
        if self.history:
            latest_frame, intensity = self.history[-1]
            return intensity
        return 0

    def has_collided(self):
        """Returns True if a collision has occurred, False otherwise."""
        return bool(self.history)

    def destroy(self):
        """Destroys the sensor."""
        self.sensor.destroy()

    def _collision_callback(self, event):
        """Callback for processing collision events."""
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x ** 2 + impulse.y ** 2 + impulse.z ** 2)
        self.history.append((event.frame, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)
