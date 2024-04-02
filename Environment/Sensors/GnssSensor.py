import carla as carla
import weakref

class GnssSensor(object):
    def __init__(self, world,vehicle,blueprints):
        self.parent = vehicle
        self.lat = 0.0
        self.lon = 0.0
        world = world
        gnssBlueprint = blueprints.find('sensor.other.gnss')
        self.sensor = world.spawn_actor(gnssBlueprint, carla.Transform(carla.Location(x=1.0, z=2.8)), attach_to=self.parent)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: GnssSensor._gnss_callback(weak_self, event))

    def get_location(self):
        return (self.lat,self.lon)
    
    def destroy(self):
        self.sensor.destroy()
        
    @staticmethod
    def _gnss_callback(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude