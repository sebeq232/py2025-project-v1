from .podstawowySensor import Sensor
import numpy as np
from datetime import datetime

class LightSensor(Sensor):
    SEASONAL_MAX_VALUES = {
        "wiosna": 8000,
        "lato": 10000,
        "jesień": 7000,
        "zima": 6000
    }

    def __init__(self, sensor_id, name, unit="lux", season="lato", frequency=1):
        if season not in self.SEASONAL_MAX_VALUES:
            raise ValueError(f"Nieznana pora roku: {season}")
        max_value = self.SEASONAL_MAX_VALUES[season]
        super().__init__(sensor_id, name, unit, min_value=0, max_value=max_value, frequency=frequency)
        self.cloud_duration_remaining = 0
        self.season = season

    def _check_and_apply_cloud_cover(self, value):
        if self.cloud_duration_remaining > 0:
            zaciemnienie = np.random.uniform(0.3, 0.7)
            self.cloud_duration_remaining -= 1
            return value * (1 - zaciemnienie)
        elif np.random.rand() < 0.1:
            self.cloud_duration_remaining = np.random.randint(1, 5) - 1
            zaciemnienie = np.random.uniform(0.3, 0.7)
            return value * (1 - zaciemnienie)
        return value

    def read_value(self, hour=None):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        if hour is None:
            from time import localtime
            hour = localtime().tm_hour

        if 5 <= hour < 21:
            scaled_hour = (hour - 5) * (np.pi / 16)
            base = np.sin(scaled_hour)
            noise = np.random.uniform(0.8, 1.2)
            value = self.max_value * base * noise
            value = self._check_and_apply_cloud_cover(value)
        else:
            value = 0
            self.cloud_duration_remaining = 0

        self.last_value = round(value, 2)
        self.history.append(self.last_value)

        self.notify_observers(timestamp=datetime.now(), value=self.last_value)
        return self.last_value

    def read_values_vectorized(self, hours: int):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        h = np.arange(hours) % 24
        values = np.zeros(hours)

        for i in range(hours):
            hour = h[i]
            if 5 <= hour < 21:
                scaled_hour = (hour - 5) * (np.pi / 16)
                base = np.sin(scaled_hour)
                noise = np.random.uniform(0.8, 1.2)
                value = self.max_value * base * noise
                value = self._check_and_apply_cloud_cover(value)
            else:
                value = 0
                self.cloud_duration_remaining = 0
            values[i] = round(value, 2)

        self.history.extend(values.tolist())
        self.last_value = values[-1]

        self.notify_observers(timestamp=datetime.now(), value=self.last_value)
        return values