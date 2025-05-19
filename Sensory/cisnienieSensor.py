from .podstawowySensor import Sensor
import random

class PressureSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        base = (self.max_value + self.min_value) / 2
        fluctuation = random.uniform(-3, 3)
        value = base + fluctuation
        value = max(self.min_value, min(self.max_value, value))
        self.last_value = round(value, 2)
        self.history.append(self.last_value)
        return self.last_value
# Sensor ciśnienia bazuje na średniej wartości w zakresie z losową niewielką fluktuacją,
# która imituje zmienne warunki atmosferyczne w krótkim czasie.