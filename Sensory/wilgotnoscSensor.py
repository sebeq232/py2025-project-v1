from .podstawowySensor import Sensor
import random

class HumiditySensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        value = random.gauss((self.max_value + self.min_value)/2, 10)
        value = max(self.min_value, min(self.max_value, value))
        self.last_value = round(value, 2)
        self.history.append(self.last_value)
        return self.last_value
# Sensor wilgotności generuje wartości na podstawie rozkładu normalnego (Gaussa),
# z średnią na poziomie połowy zakresu wartości, co symuluje naturalne fluktuacje wilgotności powietrza