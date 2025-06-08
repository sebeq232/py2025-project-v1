from .base_sensor import Sensor
import numpy as np
from datetime import datetime

class PressureSensor(Sensor):
    def __init__(self, sensor_id, unit="hPa", frequency=1):
        super().__init__(sensor_id, "Pressure Sensor", unit, 950, 1050, frequency)
        self.base_pressure = np.random.uniform(980, 1030)

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        now = datetime.now()
        hour = now.hour + now.minute / 60 + now.second / 3600

        fluctuation = 2 * np.sin(2 * np.pi * hour / 24)
        noise = np.random.normal(0, 0.5)
        value = self.base_pressure + fluctuation + noise
        self.last_value = round(value, 2)
        self._notify_callbacks()

        #self.last_value = round(value, 2)
        return self.last_value
#Generuje typowe dla polski wartosci cisnienia za pomoca fluktuacji losujac najpierw liczbe do fluktuacji(base pressure)
#i robi lekkie skoki i spadki: f(x)=sinx, generuje wartosci z pomoca zegara systemowego.