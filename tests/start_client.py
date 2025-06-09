import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# tests/start_client.py
import asyncio
import unittest
import os
from datetime import datetime
from logger.logger import Logger
from network.client import NetworkClient






# Absolutne ścieżki
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLIENT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../configs/client_config.yaml"))
LOGGER_CONFIG_PATH = os.path.join(BASE_DIR, "config.json")


async def main():
    client = NetworkClient(config_path=CLIENT_CONFIG_PATH)
    client.connect()

    logger = Logger(LOGGER_CONFIG_PATH, client=client)
    logger.start()



    # Tymczasowy test odczytu:
    for i in range(3):
        logger.log_reading(sensor_id="T-001", timestamp=datetime.now(), value=20.5 + i, unit="°C")
        await asyncio.sleep(1)

    logger.stop()
    client.close()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover('.', pattern='test_*.py'))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n Wszystkie testy przeszły pomyślnie!\n")
    else:
        print("\n Niektóre testy zakończyły się niepowodzeniem.\n")
        exit()

    asyncio.run(main())
