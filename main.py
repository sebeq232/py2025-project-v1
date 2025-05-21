from Sensory.temperaturaSezonowaSensor import SeasonalTemperatureSensor
from Sensory.wilgotnoscSensor import HumiditySensor
from Sensory.cisnienieSensor import PressureSensor
from Sensory.swiatloSensor import LightSensor
from datetime import datetime, timedelta
from Logger.logger import Logger
from utils import get_season_from_date

def czy_aktywny(nazwa_czujnika):
    odp = input(f"Czy chcesz aktywować czujnik {nazwa_czujnika}? (tak/nie): ").strip().lower()
    return odp == "tak"

def main():
    date_str = input("Podaj datę startową (YYYY-MM-DD): ").strip()
    try:
        start_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Niepoprawny format daty. Użyj YYYY-MM-DD.")
        return

    # Tworzenie loggera i rozpoczęcie sesji
    logger = Logger("config.json")
    logger.start()

    # Czujniki
    temp_sensor = SeasonalTemperatureSensor(sensor_id="temp_sensor", name="TempSensor", unit="°C", season="lato")
    humidity_sensor = HumiditySensor(sensor_id="humidity_sensor", name="HumiditySensor", unit="%", min_value=20, max_value=100, season="lato")
    pressure_sensor = PressureSensor(sensor_id="pressure_sensor", name="PressureSensor", unit="hPa", min_value=980, max_value=1050)
    light_sensor = LightSensor(sensor_id="light_sensor", name="LightSensor", unit="lx", season="lato")

    sensors = [temp_sensor, humidity_sensor, pressure_sensor, light_sensor]
    active_sensors = []

    for sensor in sensors:
        sensor.active = czy_aktywny(sensor.name)
        if sensor.active:
            sensor.register_callback(logger.log_reading)
            active_sensors.append(sensor)

    wilgotnosc_sezonowe_zakresy = {
        "wiosna": (30, 90),
        "lato": (20, 80),
        "jesień": (35, 95),
        "zima": (35, 95)
    }

    try:
        print("\nSymulacja odczytów:")
        hours = int(input("Podaj liczbę godzin do symulacji: "))
        timestamps = [start_date + timedelta(hours=i) for i in range(hours)]

        for current_time in timestamps:
            current_season = get_season_from_date(current_time.year, current_time.month, current_time.day)

            # Aktualizacja sezonowych zakresów
            temp_sensor.season = current_season
            temp_sensor.min_value, temp_sensor.max_value = temp_sensor.SEASON_ZAKRESY[current_season]
            temp_sensor.T_srednia = (temp_sensor.min_value + temp_sensor.max_value) / 2
            temp_sensor.amplituda = (temp_sensor.max_value - temp_sensor.min_value) / 2

            humidity_sensor.season = current_season
            humidity_sensor.min_value, humidity_sensor.max_value = wilgotnosc_sezonowe_zakresy[current_season]

            light_sensor.season = current_season
            light_sensor.max_value = 6000 if current_season == "zima" else 10000

            # Odczyt i logowanie
            results = {}
            for sensor in active_sensors:
                if isinstance(sensor, HumiditySensor):
                    value = sensor.read_value(current_time)
                elif isinstance(sensor, LightSensor):
                    value = sensor.read_value(hour=current_time.hour)
                else:
                    value = sensor.read_value()
                results[sensor.name] = value

            print(f"{current_time.isoformat()} " + ", ".join(
                f"{name}: {val:.2f}{next(s.unit for s in active_sensors if s.name == name)}"
                for name, val in results.items()))

    finally:
        logger.stop()
        print("Logger zatrzymany i dane zapisane.")

if __name__ == "__main__":
    main()