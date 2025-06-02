from .base_sensor import Sensor
import numpy as np

class LightSensor(Sensor):
    def __init__(self, sensor_id, unit="lx", frequency=1):
        super().__init__(sensor_id, name="Light Sensor", unit=unit, min_value=0, max_value=10000, frequency=frequency)
        self.anomaly_active = False
        self.anomaly_range = None
        self.anomaly_offset = 0
        self._generate_daily_anomaly()

    def _generate_daily_anomaly(self):
        """
        Generuje pojedynczą anomalię trwającą 3 godziny między 6:00 a 21:00.
        """
        if np.random.rand() < 0.5:  # 50% szans na anomalię np zachmurzenie lub mało zachmurzone niebo
            start = np.random.randint(6, 20)  # maksymalnie do 19, żeby mieściło się 3h
            self.anomaly_range = (start, start + 3)
            self.anomaly_offset = np.random.choice([-3500, 3500])
            self.anomaly_active = True
        else:
            self.anomaly_active = False
            self.anomaly_range = None
            self.anomaly_offset = 0

    def update_for_next_day(self):
        self._generate_daily_anomaly()

    def read_value(self, second_in_day=None):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        # Domyślne światło (0 lx nocą)
        if 6 <= second_in_day < 22:
            # Normalizacja do zakresu [0, 1] w ciągu dnia
            sunrise = 6
            duration = 16
            normalized_time = (second_in_day - sunrise) / duration

            base_light = 10000 * np.sin(np.pi * normalized_time)
        else:
            base_light = 0

        # Anomalia
        if self.anomaly_active:
            start, end = self.anomaly_range
            if start <= second_in_day < end:
                base_light += self.anomaly_offset

        # Szum
        noise = np.random.normal(loc=0.0, scale=0.05 * base_light)
        value = base_light + noise

        # Zapis i zwrot wartości
        self.last_value = round(max(value, 0), 2)
        return self.last_value
