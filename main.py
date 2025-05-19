from Sensory.temperaturaSezonowaSensor import SeasonalTemperatureSensor
from Sensory.wilgotnoscSensor import HumiditySensor
from Sensory.cisnienieSensor import PressureSensor
from Sensory.swiatloSensor import LightSensor

def main():
    #Pobieranie pory roku od użytkownika
    season = input("Podaj porę roku do pomiaru temperatury (wiosna/lato/jesień/zima): ").strip().lower()

    #Dostepne czujniki
    temp_sensor = SeasonalTemperatureSensor(sensor_id=1, name="TempSensor", unit="°C", season=season)
    humidity_sensor = HumiditySensor(sensor_id=2, name="HumiditySensor", unit="%", min_value=20, max_value=80)
    pressure_sensor = PressureSensor(sensor_id=3, name="PressureSensor", unit="hPa", min_value=980, max_value=1050)
    light_sensor = LightSensor(sensor_id=4, name="LightSensor", unit="lx", min_value=0, max_value=1000)

    #Odczyt wartosci
    print("\nOdczyty ze wszystkich aktywnych czujników:")
    print(f"Temperatura: {temp_sensor.read_value()} {temp_sensor.unit}")
    print(f"Wilgotność: {humidity_sensor.read_value()} {humidity_sensor.unit}")
    print(f"Ciśnienie: {pressure_sensor.read_value()} {pressure_sensor.unit}")
    print(f"Światło: {light_sensor.read_value()} {light_sensor.unit}")

    #Test wyłączania i włączania czujników:
    print("\nWyłączam czujnik światła i próbuję odczytać jego wartość:")
    light_sensor.stop()
    try:
        print("Światło:", light_sensor.read_value())
    except Exception as e:
        print("Błąd:", e)

    # Ponowne włączenie i odczyt
    print("\nWłączam czujnik światła ponownie i odczytuję:")
    light_sensor.start()
    print(f"Światło: {light_sensor.read_value()} {light_sensor.unit}")

if __name__ == "__main__":
    main()