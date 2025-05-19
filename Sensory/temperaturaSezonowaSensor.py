import random
from .podstawowySensor import Sensor


class SeasonalTemperatureSensor(Sensor):
    SEASON_ZAKRESY = {
        "wiosna": (0, 20),
        "lato": (5, 40),
        "jesien": (-10, 10),
        "zima": (-30, 5)
    }

    def __init__(self, sensor_id, name, unit="°C", season="lato", frequency=1):
        if season not in self.SEASON_ZAKRESY:
            raise ValueError("Niepoprawna pora roku. Wybierz: wiosna, lato, jesien, zima.")

        min_value, max_value = self.SEASON_ZAKRESY[season]
        super().__init__(sensor_id, name, unit, min_value, max_value, frequency)
        self.season = season

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        value = random.uniform(self.min_value, self.max_value)
        self.last_value = round(value, 2)
        self.history.append(self.last_value)
        return self.last_value
    #temperatura losowana z typowych dla pór roku zakresów z porą do wyboru przez użytkownika.