from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor
from sensors.pressure_sensor import PressureSensor
from sensors.light_sensor import LightSensor
from logger.logger import Logger
from network.client import NetworkClient
import time

def main():
    # Inicjalizacja klienta sieciowego
    client = NetworkClient("../configs/client_config.yaml")
    client.connect()

    # Logger z klientem
    logger = Logger("config.json", client=client)
    logger.start()

    # Czujniki z frequency na 10 sekund (8 + ~2 sek obsuwy)
    temp_sensor = TemperatureSensor("T-001", frequency=8)
    humidity_sensor = HumiditySensor("H-001", temperature_sensor=temp_sensor, frequency=8)
    pressure_sensor = PressureSensor("P-001", frequency=8)
    light_sensor = LightSensor("L-001", frequency=8)

    sensors = [temp_sensor, humidity_sensor, pressure_sensor, light_sensor]

    # Start czujników
    for sensor in sensors:
        sensor.register_callback(logger.log_reading)
        sensor.start()

    print(" Czujniki pracują. Naciśnij Ctrl+C, aby zatrzymać...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Przerwano przez użytkownika.")
    finally:
        for sensor in sensors:
            sensor.stop()
        logger.stop()
        client.close()
        print(" Zakonczono. Zajrzyj do folderu 'logs/'.")

if __name__ == "__main__":
    main()
