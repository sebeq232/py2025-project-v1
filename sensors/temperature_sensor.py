from .base_sensor import Sensor
import numpy as np
import math
from datetime import datetime

class TemperatureSensor(Sensor):
    def __init__(self, sensor_id, temp_range=None, unit="°C", frequency=1):
        if temp_range is None:
            predefined_ranges = [(-20, -5), (-5, 15), (15, 40)]
            temp_range = list(predefined_ranges[np.random.randint(0, len(predefined_ranges))])
        else:
            temp_range = list(temp_range)

        super().__init__(sensor_id, "Temperature Sensor", unit, temp_range[0], temp_range[1], frequency)
        self.temp_range = temp_range

        self.anomaly_active = False
        self.anomaly_range = None
        self.anomaly_offset = 0

        self.last_day = datetime.now().date()  # <-- Dodajemy datę startową
        self._generate_daily_anomaly()

    def _generate_daily_anomaly(self):
        if np.random.rand() < 0.9:
            start = np.random.randint(6, 16)  # np. 6:00 - 18:00
            self.anomaly_range = (start, start + 3)
            self.anomaly_offset = np.random.choice([-5, 5])
            self.anomaly_active = True
        else:
            self.anomaly_active = False
            self.anomaly_range = None
            self.anomaly_offset = 0

    def _update_range_if_new_day(self):
        today = datetime.now().date()
        if today != self.last_day:
            self.last_day = today
            shift = np.random.choice([0, +5, -5], p=[0.5, 0.25, 0.25])
            new_min = np.clip(self.temp_range[0] + shift, -20, 20)
            self.temp_range = [new_min, new_min + 20]
            self.min_value, self.max_value = self.temp_range
            self._generate_daily_anomaly()

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        self._update_range_if_new_day()

        now = datetime.now()
        second_in_day = now.hour + now.minute / 60 + now.second / 3600

        min_temp, max_temp = self.temp_range
        mid = (min_temp + max_temp) / 2
        amplitude = (max_temp - min_temp) / 2

        omega = 2 * math.pi / 24
        phase_shift = -3 * math.pi / 4  # szczyt o 15:00

        base_value = mid + amplitude * math.sin(omega * second_in_day + phase_shift)
        noise = np.random.normal(loc=0.0, scale=0.5)
        value = base_value + noise

        # Anomalia jeśli aktywna
        if self.anomaly_active:
            start, end = self.anomaly_range
            if start <= now.hour < end:
                value += self.anomaly_offset
        self._notify_callbacks()
        self.last_value = round(value, 2)
        return self.last_value

#Działanie:
#Losuje 1 z 3 przedziałów początkowych,"predefined_ranges = [(-20, -5), (-5, 15), (15, 40)]"
#następnie losuje tempereature z przebiegu sinusoidalnego na podstawie zakresu wartosci przedzialu
#kontrlowanego przez zegar systemowy.Sinusoida ma szczyt o 15:00:00,
#Do tego po północy zaczyna się następny dzień co sprawia,że jest 50% szans na zostanie w tym
#samym przedziale pogodowym i po 25% szans,ze poczatek i koniec przedziału zostanie zwiekszony lub zmniejszony o 5*C
#Do tego moze wystpaic anomalia pogodowa(szanse mozna edytowac w kodzie) czyli +/-5*C do temperatury na 3 godziny
#pomiedzy 6 a 16.