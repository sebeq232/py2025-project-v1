from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor
from sensors.pressure_sensor import PressureSensor
from sensors.light_sensor import LightSensor
from logger.logger import Logger
from network.client import NetworkClient  # <-- dodaj to
import time

def main():
    # Inicjalizacja klienta sieciowego
    client = NetworkClient("../configs/client_config.yaml")
    client.connect()

    # Inicjalizacja loggera z klientem
    logger = Logger("config.json", client=client)  # <-- przekaz klienta
    logger.start()

    # Inicjalizacja czujników
    temp_sensor = TemperatureSensor("T-001")
    humidity_sensor = HumiditySensor("H-001", temperature_sensor=temp_sensor)
    pressure_sensor = PressureSensor("P-001")
    light_sensor = LightSensor("L-001")

    # Rejestracja loggera jako callbacku
    for sensor in [temp_sensor, humidity_sensor, pressure_sensor, light_sensor]:
        sensor.register_callback(logger.log_reading)

    print(" Zbieranie danych przez x sekund...")

    try:
        for i in range(3):  # 15 sekund
            temp_sensor.read_value()
            humidity_sensor.read_value()
            pressure_sensor.read_value()
            light_sensor.read_value()

            print(f"[{i+1}/30] Odczyty zapisane.")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n Przerwano przez uzytkownika.")

    finally:
        # Zatrzymanie loggera i czujników
        logger.stop()
        client.close()  # <-- zamknij połączenie
        for sensor in [temp_sensor, humidity_sensor, pressure_sensor, light_sensor]:
            sensor.stop()

        print(" Zakończono. Otwórz katalog 'logs/'.")

if __name__ == "__main__":
    main()
