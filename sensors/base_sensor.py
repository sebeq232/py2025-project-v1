import numpy as np
import time
from datetime import datetime
import threading

class Sensor:
    def __init__(self, sensor_id, name, unit, min_value, max_value, frequency=1):
        self.sensor_id = sensor_id
        self.name = name
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.frequency = frequency
        self.active = False
        self.last_value = None
        self._thread = None
        self._callbacks = []

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        value = np.random.uniform(self.min_value, self.max_value)
        self.last_value = round(value, 2)
        self._notify_callbacks()
        return self.last_value

    def get_last_value(self):
        if self.last_value is None:
            return self.read_value()
        return self.last_value

    def start(self):
        if not self.active:
            self.active = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self.active = False

    def _run(self):
        while self.active:
            self.read_value()
            time.sleep(self.frequency)

    def register_callback(self, callback):
        self._callbacks.append(callback)

    def _notify_callbacks(self):
        for callback in self._callbacks:
            callback(
                self.sensor_id,
                datetime.now(),
                self.last_value,
                self.unit
            )

    def __str__(self):
        return f"Sensor(id={self.sensor_id}, name={self.name}, unit={self.unit})"
