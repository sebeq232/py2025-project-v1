from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor
from datetime import datetime
import time

print("=== Test 10h: HumiditySensor (czas systemowy) ===")

temp_sensor = TemperatureSensor("T-REF") #referencja,aby test dzialal, w zalozeniu czujnik wilgotnosci generuje dane na podstawie temperarury
humidity_sensor = HumiditySensor("H-001", temperature_sensor=temp_sensor)

with open("log_humidity_10h.txt", "w") as f:
    for i in range(10):  # 10 godzin
        now = datetime.now().strftime("%H:%M:%S")
        temp_value = temp_sensor.read_value()
        humidity_value = humidity_sensor.read_value()
        log_line = f"Odczyt {i+1} ({now}): Temp={temp_value}°C | Humidity={humidity_value}%"
        print(log_line)
        f.write(log_line + "\n")
        time.sleep(1)

humidity_sensor.stop()
print("Sensor zatrzymany. Próba odczytu...")

try:
    humidity_sensor.read_value()
except Exception as e:
    print("Oczekiwany wyjątek:", e)
