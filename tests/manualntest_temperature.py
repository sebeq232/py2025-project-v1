from sensors.temperature_sensor import TemperatureSensor
from datetime import datetime
import time

print("=== Test 10h: TemperatureSensor (czas systemowy) ===")

sensor = TemperatureSensor("T-001")
sensor.start()
with open("log_temp_10h.txt", "w") as f:
    for i in range(36000):  # 10 godzin * 3600 sekund
        now = datetime.now().strftime("%H:%M:%S")
        value = sensor.read_value()
        log_line = f"Odczyt {i+1} ({now}): {value} {sensor.unit}"
        print(log_line)
        f.write(log_line + "\n")
        time.sleep(1)  # Realny czas – 1 sekunda

sensor.stop()
print("Sensor zatrzymany. Próba odczytu...")

try:
    sensor.read_value()
except Exception as e:
    print("Oczekiwany wyjątek:", e)
