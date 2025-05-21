import math
import numpy as np
from datetime import datetime
from .podstawowySensor import Sensor

class SeasonalTemperatureSensor(Sensor):
    SEASON_ZAKRESY = {
        "wiosna": (0, 20),
        "lato": (5, 40),
        "jesień": (-10, 10),
        "zima": (-20, 5)
    }

    def __init__(self, sensor_id, name, unit="°C", season="lato", frequency=1):
        if season not in self.SEASON_ZAKRESY:
            raise ValueError("Niepoprawna pora roku. Wybierz: wiosna, lato, jesień, zima.")
        self.season = season
        self.min_value, self.max_value = self.SEASON_ZAKRESY[season]
        super().__init__(sensor_id, name, unit, self.min_value, self.max_value, frequency)
        self.current_hour = 0
        self.T_srednia = (self.min_value + self.max_value) / 2
        self.amplituda = (self.max_value - self.min_value) / 2
        self.przesuniecie_fazowe = 15

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        angle = 2 * math.pi * (self.current_hour - 15) / 24
        temp = self.T_srednia + self.amplituda * math.cos(angle)
        temp += np.random.uniform(-0.5, 0.5)
        temp = round(temp, 2)

        self.last_value = temp
        self.history.append(self.last_value)
        self.current_hour = (self.current_hour + 1) % 24

        # 🔔 Powiadom zarejestrowane callbacki (np. Logger)
        self.notify_observers(timestamp=datetime.now(), value=temp)

        return self.last_value

    def read_values_vectorized(self, hours: int):
        """Wygeneruj tablicę temperatur dla podanej liczby godzin (wektorowo)."""
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        h = np.arange(self.current_hour, self.current_hour + hours) % 24
        angles = 2 * np.pi * (h - 15) / 24
        temps = self.T_srednia + self.amplituda * np.cos(angles)
        temps += np.random.uniform(-0.5, 0.5, size=hours)
        temps = np.round(temps, 2)

        self.history.extend(temps.tolist())
        self.current_hour = (self.current_hour + hours) % 24
        self.last_value = temps[-1]

        # 🔔 Powiadom tylko o ostatnim odczycie
        self.notify_observers(timestamp=datetime.now(), value=self.last_value)

        return temps