import time
from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor
from sensors.pressure_sensor import PressureSensor
from sensors.light_sensor import LightSensor

# Parametry symulacji
days = 3  # Liczba dni do zasymulowania
seconds_per_day = 24  # każda sekunda = 1 godzina

# Inicjalizacja czujników
temp_sensor = TemperatureSensor("T-001")
humidity_sensor = HumiditySensor("H-001", temp_sensor)
pressure_sensor = PressureSensor("P-001")
light_sensor = LightSensor("L-001", temp_sensor)

print(f"Symulacja danych z 4 czujników przez {days} dni:\n")

for day in range(1, days + 1):
    print(f"--- Dzień {day} ---")
    for second in range(seconds_per_day):
        temp = temp_sensor.read_value(second)
        humid = humidity_sensor.read_value()
        pressure = pressure_sensor.read_value(second)
        light = light_sensor.read_value(second)

        print(f"Godzina {second:02d}:00 -> Temp: {temp} °C | "
              f"Wilgotność: {humid} % | "
              f"Ciśnienie: {pressure} hPa | "
              f"Światło: {light} lx")

        time.sleep(temp_sensor.frequency)

    # Przejście do kolejnego dnia – aktualizacja czujników
    temp_sensor.update_range_for_next_day()
    light_sensor.update_for_next_day()

print("\nSymulacja zakończona.")
