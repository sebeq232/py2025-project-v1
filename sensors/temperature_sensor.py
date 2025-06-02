from .base_sensor import Sensor
import numpy as np
import math

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
        self.anomaly_range = None  # (start_second, end_second)
        self.anomaly_offset = 0

        self._generate_daily_anomaly()

    def _generate_daily_anomaly(self):
        """
        Na początku każdego dnia losujemy, czy wystąpi lokalna anomalia i kiedy.
        """
        if np.random.rand() < 0.3:  # 30% szansy na anomalię
            start = np.random.randint(6, 16)  # od 6 do 15 -> anomalia obejmie do 18
            self.anomaly_range = (start, start + 3)
            self.anomaly_offset = np.random.choice([-5, 5])
            self.anomaly_active = True
        else:
            self.anomaly_active = False
            self.anomaly_range = None
            self.anomaly_offset = 0

    def update_range_for_next_day(self):
        """
        Zmiana dziennego zakresu temperatury oraz nowa potencjalna anomalia.
        """
        shift = np.random.choice([0, +5, -5], p=[0.5, 0.25, 0.25])
        new_min = self.temp_range[0] + shift
        new_min = np.clip(new_min, -20, 20)
        self.temp_range = [new_min, new_min + 20]
        self.min_value, self.max_value = self.temp_range

        self._generate_daily_anomaly()  # ważne: nowy dzień, nowe anomalie

    def read_value(self, second_in_day=None):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        min_temp, max_temp = self.temp_range
        mid = (min_temp + max_temp) / 2
        amplitude = (max_temp - min_temp) / 2

        # Sinusoida z przesunięciem szczytu na 15:00
        omega = 2 * math.pi / 24
        phase_shift = -3 * math.pi / 4
        base_value = mid + amplitude * math.sin(omega * second_in_day + phase_shift)

        # Dodajemy szum
        noise = np.random.normal(loc=0.0, scale=0.5)
        value = base_value + noise

        # Jeśli trwa lokalna anomalia, dodajemy offset
        if self.anomaly_active:
            start, end = self.anomaly_range
            if start <= second_in_day < end:
                value += self.anomaly_offset

        self.last_value = round(value, 2)
        return self.last_value
