import carla
import weakref

class GnssSensor:
    def __init__(self, world, vehicle, blueprints):
        self.parent = vehicle
        self.world = world
        gnss_blueprint = blueprints.find('sensor.other.gnss')
        self.sensor = world.spawn_actor(gnss_blueprint, carla.Transform(carla.Location(x=1.0, z=2.8)), attach_to=vehicle)
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: GnssSensor._gnss_callback(weak_self, event))
        self.location = {"latitude": 0.0, "longitude": 0.0}  # Store location as a dictionary

    def get_location(self):
        """Returns the current location as a dictionary."""
        return self.location

    def destroy(self):
        """Destroys the sensor."""
        self.sensor.destroy()

    @staticmethod
    def _gnss_callback(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.location["latitude"] = event.latitude
        self.location["longitude"] = event.longitude
