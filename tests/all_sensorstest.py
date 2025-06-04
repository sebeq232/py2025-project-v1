from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor
from sensors.light_sensor import LightSensor
from sensors.pressure_sensor import PressureSensor
from datetime import datetime
import time

print("=== Test 10h: Wszystkie czujniki (czas systemowy) ===")

# Tworzymy czujniki – uwaga: wilgotność zależy od temperatury, więc przekazujemy ten sam sensor
temp_sensor = TemperatureSensor("T-001")
humidity_sensor = HumiditySensor("H-001", temperature_sensor=temp_sensor)
light_sensor = LightSensor("L-001")
pressure_sensor = PressureSensor("P-001")

with open("log_all_sensors_10h.txt", "w") as f:
    for i in range(36000):  # 10 godzin * 3600 sekund
        now = datetime.now().strftime("%H:%M:%S")

        temp = temp_sensor.read_value()
        humidity = humidity_sensor.read_value()
        light = light_sensor.read_value()
        pressure = pressure_sensor.read_value()

        log_line = (
            f"Odczyt {i+1} ({now}): "
            f"Temp={temp}°C | Hum={humidity}% | Light={light}lx | Press={pressure}hPa"
        )

        print(log_line)
        f.write(log_line + "\n")

        time.sleep(1)

# Zatrzymujemy czujniki
temp_sensor.stop()
humidity_sensor.stop()
light_sensor.stop()
pressure_sensor.stop()

print("Czujniki zatrzymane. Próby odczytu po zatrzymaniu:")

for sensor in [temp_sensor, humidity_sensor, light_sensor, pressure_sensor]:
    try:
        sensor.read_value()
    except Exception as e:
        print(f"Oczekiwany wyjątek dla {sensor.name}: {e}")
