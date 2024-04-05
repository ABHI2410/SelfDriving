import carla

class WeatherSensor:
    def __init__(self, world):
        self.world = world
        self.weather = self.world.get_weather()

    def update_weather(self):
        self.weather = self.world.get_weather()

    def get_weather(self):
        return self.weather

    def destroy(self):
        pass  # No specific destruction needed for this sensor
