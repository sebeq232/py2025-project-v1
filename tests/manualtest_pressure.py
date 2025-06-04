from sensors.pressure_sensor import PressureSensor
from datetime import datetime
import time

print("=== Test 10h: PressureSensor (czas systemowy) ===")

sensor = PressureSensor("P-001")

with open("log_pressure_10h.txt", "w") as f:
    for i in range(10):  # 10 godzin
        now = datetime.now().strftime("%H:%M:%S")
        value = sensor.read_value()
        log_line = f"Odczyt {i+1} ({now}): {value} {sensor.unit}"
        print(log_line)
        f.write(log_line + "\n")
        time.sleep(1)

sensor.stop()
print("Sensor zatrzymany. Próba odczytu...")

try:
    sensor.read_value()
except Exception as e:
    print("Oczekiwany wyjątek:", e)
