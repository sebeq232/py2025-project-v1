from .podstawowySensor import Sensor
import numpy as np
from datetime import datetime

class PressureSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        base = (self.max_value + self.min_value) / 2
        fluctuation = np.random.uniform(-3, 3)
        value = base + fluctuation
        value = np.clip(value, self.min_value, self.max_value)

        self.last_value = round(value, 2)
        self.history.append(self.last_value)

        self.notify_observers(timestamp=datetime.now(), value=self.last_value)
        return self.last_value

    def read_values_vectorized(self, n: int):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        base = (self.max_value + self.min_value) / 2
        fluctuations = np.random.uniform(-3, 3, size=n)
        values = base + fluctuations
        values = np.clip(values, self.min_value, self.max_value)
        values = np.round(values, 2)

        self.history.extend(values.tolist())
        self.last_value = values[-1]

        self.notify_observers(timestamp=datetime.now(), value=self.last_value)
        return values
