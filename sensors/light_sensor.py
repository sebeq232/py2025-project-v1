from .base_sensor import Sensor
import numpy as np
from datetime import datetime

class LightSensor(Sensor):
    def __init__(self, sensor_id, unit="lx", frequency=1):
        super().__init__(sensor_id, "Light Sensor", unit, 0, 10000, frequency)
        self.anomaly_active = False
        self.anomaly_range = None
        self.anomaly_offset = 0
        self.last_day = datetime.now().date()
        self._generate_daily_anomaly()

    def _generate_daily_anomaly(self):
        if np.random.rand() < 0.9:
            start = np.random.randint(6, 20)
            self.anomaly_range = (start, start + 3)
            self.anomaly_offset = np.random.choice([-3500, 3500])
            self.anomaly_active = True
        else:
            self.anomaly_active = False
            self.anomaly_range = None
            self.anomaly_offset = 0

    def _update_if_new_day(self):
        today = datetime.now().date()
        if today != self.last_day:
            self.last_day = today
            self._generate_daily_anomaly()

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        self._update_if_new_day()

        now = datetime.now()
        hour = now.hour + now.minute / 60 + now.second / 3600

        if 6 <= hour < 22:
            normalized_time = (hour - 6) / 16
            base_light = 10000 * np.sin(np.pi * normalized_time)
        else:
            base_light = 0

        if self.anomaly_active:
            start, end = self.anomaly_range
            if start <= now.hour < end:
                base_light += self.anomaly_offset

        noise = np.random.normal(0, 0.05 * base_light)
        value = base_light + noise
        self.last_value = round(max(value, 0), 2)
        return self.last_value
#Działanie:
#Od 0:00 do 6:00 swiatlo jest zerowe, jak równiez od 22:00 do 23:59:59
# zastosowana zostala tu sinusoida o szczycie o godzinie 15:00(najwiecej swiatla)
#Do tego szum aby dodac naturalnosci w odczytach.Mozliwosc wystapienia anomali(naglego zachmurzenia lub natezenia swiatla)
#Wykrywa nastepny dzien i znowu zaczyna od 0lx.
#odczytuje sinusoide na podstawie zegara systemowego
