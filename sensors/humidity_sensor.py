from .base_sensor import Sensor
import numpy as np

class HumiditySensor(Sensor):
    def __init__(self, sensor_id, temperature_sensor, unit="%", frequency=1):
        super().__init__(sensor_id, "Humidity Sensor", unit, 0, 100, frequency)
        self.temperature_sensor = temperature_sensor

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        temperature = self.temperature_sensor.get_last_value()

        if temperature < -10:
            base_range = (90, 99)
        elif -10 <= temperature < 0:
            base_range = (80, 90)
        elif 0 <= temperature < 10:
            base_range = (70, 80)
        elif 10 <= temperature < 20:
            base_range = (60, 70)
        elif 20 <= temperature < 30:
            base_range = (50, 60)
        else:
            base_range = (20, 50)

        base_value = np.random.uniform(*base_range)
        noise = np.random.normal(0, 1.5)
        value = base_value + noise
        self.last_value = round(np.clip(value, 0, 100), 2)
        self._notify_callbacks()
        #self.last_value = round(np.clip(value, 0, 100), 2)
        return self.last_value

#czynnik wilgotnosci zalezny od wylosowanej temperatury,odczyty przydzielane na podstawie
#przedziałow temperatury, do tego szum aby dodac wiekszą naturalnosc danych