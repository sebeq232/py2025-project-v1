from logger.logger import Logger
from datetime import datetime
import os

import os
config_path = r"C:\Users\Sebastian\Desktop\SensoryPython\config.json"
logger = Logger(config_path)

# Nadpisany log_dir na rzecz testu
logger.log_dir = r"C:\Users\Sebastian\Desktop\SensoryPython\logs"
logger.archive_dir = os.path.join(logger.log_dir, "archive")

print(" Katalog roboczy:", os.getcwd())
print(" log_dir:", logger.log_dir)
print(" archive_dir:", logger.archive_dir)

print("\n Pliki CSV w katalogu logów:")
log_files = [f for f in os.listdir(logger.log_dir) if f.endswith(".csv")]
for f in log_files:
    print(" -", f)

print("\n Pliki CSV w archiwum:")
archive_files = [f for f in os.listdir(logger.archive_dir) if f.endswith(".csv")]
for f in archive_files:
    print(" -", f)

print("\n pruba odczytania logow")
start = datetime.min
end = datetime.now()

found = False
for i, entry in enumerate(logger.read_logs(start=start, end=end)):
    print(f"{i+1}. {entry['timestamp']} | {entry['sensor_id']} = {entry['value']} {entry['unit']}")
    found = True
    if i >= 99:
        break  # max x wpisów na test

if not found:
    print("Nie znaleziono żadnych wpisów.")
else:
    print("Sukces — logi odczytane.")
