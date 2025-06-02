from .base_sensor import Sensor
import numpy as np

class PressureSensor(Sensor):
    def __init__(self, sensor_id, unit="hPa", frequency=1):
        super().__init__(sensor_id, "Pressure Sensor", unit, 950, 1050, frequency)
        self.base_pressure = np.random.uniform(980, 1030)  # startowa wartość w typowym zakresie

    def read_value(self, second_in_day=None):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        # Dodaj lekką fluktuację sinusoidalną + losowy szum
        fluctuation = 2 * np.sin(2 * np.pi * (second_in_day / 24))  # łagodny dzienny cykl
        noise = np.random.normal(0, 0.5)  # drobny szum
        value = self.base_pressure + fluctuation + noise

        # Zapisz i zwróć zaokrągloną wartość
        self.last_value = round(value, 2)
        return self.last_value