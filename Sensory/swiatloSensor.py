from .podstawowySensor import Sensor
import time
import math


class LightSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        hour = time.localtime().tm_hour
        current_time = time.strftime("%H:%M")  # godzina pomiaru w formacie HH:MM

        if 6 <= hour <= 18:
            value = self.max_value * math.sin(math.pi * (hour - 6) / 12)
        else:
            value = 0

        self.last_value = round(value, 2)
        self.history.append((self.last_value, current_time))  # zapis z godziną
        return f"{self.last_value} ({current_time})"
    # Sensor światła odzwierciedla natężenie światła dziennego,
    # które rośnie i maleje zgodnie z godziną dnia, osiągając maksimum w południe,
    # a nocą wartość spada do zera, symulując brak światła.