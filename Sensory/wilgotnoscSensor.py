from .podstawowySensor import Sensor
import numpy as np
from datetime import datetime

class HumiditySensor(Sensor):
    MIN_HUMIDITY = 30
    MAX_HOUR_DIFF = 12

    SEASONAL_PEAK_HUMIDITY = {
        "wiosna": 90,
        "lato": 80,
        "jesień": 95,
        "zima": 95
    }

    def __init__(self, *args, season="wiosna", **kwargs):
        super().__init__(*args, **kwargs)
        if season not in self.SEASONAL_PEAK_HUMIDITY:
            raise ValueError(f"Nieznana pora roku: {season}")
        self.season = season

    def _humidity_for_hour(self, hour: int) -> float:
        b = self.SEASONAL_PEAK_HUMIDITY[self.season]
        a = -(b - self.MIN_HUMIDITY) / (self.MAX_HOUR_DIFF ** 2)
        x = hour if hour <= 12 else 24 - hour
        humidity = a * (x ** 2) + b
        return float(np.clip(humidity, self.MIN_HUMIDITY, 100))

    def read_value(self, current_time: datetime = None):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        if current_time is None:
            current_time = datetime.now()
        hour = current_time.hour

        base_humidity = self._humidity_for_hour(hour)
        noise = np.random.normal(loc=0, scale=2)
        value = base_humidity + noise
        value = np.clip(value, self.min_value, self.max_value)

        self.last_value = round(value, 2)
        self.history.append(self.last_value)

        self.notify_observers(timestamp=current_time, value=self.last_value)
        return self.last_value

    def read_values_vectorized(self, n: int, start_hour: int = 0):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        hours = [(start_hour + i) % 24 for i in range(n)]
        base_values = np.array([self._humidity_for_hour(h) for h in hours])
        noise = np.random.normal(loc=0, scale=2, size=n)
        values = base_values + noise
        values = np.clip(values, self.min_value, self.max_value)
        values = np.round(values, 2)

        self.history.extend(values.tolist())
        self.last_value = values[-1]

        self.notify_observers(timestamp=datetime.now(), value=self.last_value)
        return values