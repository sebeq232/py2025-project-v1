import os
import json
import csv
from datetime import datetime, timedelta
from typing import Optional, Iterator, Dict

class Logger:
    def __init__(self, config_path: str, client: Optional[object] = None):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Konfiguracja
        self.log_dir = config.get("log_dir", "./logs")
        self.filename_pattern = config.get("filename_pattern", "sensors_%Y%m%d.csv")
        self.buffer_size = config.get("buffer_size", 100)
        self.rotate_every_hours = config.get("rotate_every_hours", 24)
        self.max_size_mb = config.get("max_size_mb", 10)
        self.rotate_after_lines = config.get("rotate_after_lines", 10000)
        self.retention_days = config.get("retention_days", 30)

        # Bufor danych
        self.buffer = []
        self.current_file = None
        self.current_writer = None
        self.current_filename = ""
        self.last_rotation_time = datetime.now()
        self.line_count = 0

        # Katalogi logów
        self.archive_dir = os.path.join(self.log_dir, "archive")
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)

        # Klient sieciowy (opcjonalnie)
        self.client = client

    def start(self) -> None:
        self._rotate(force=True)

    def stop(self) -> None:
        self._flush()
        if self.current_file:
            self.current_file.close()
            self.current_file = None
            self.current_writer = None

    def log_reading(self, sensor_id: str, timestamp: datetime, value: float, unit: str) -> None:
        row = [timestamp.isoformat(), sensor_id, value, unit]
        self.buffer.append(row)

        # Wysyłanie do klienta sieciowego (jeśli dostępny)
        if self.client:
            try:
                payload = {
                    "sensor_id": sensor_id,
                    "timestamp": timestamp.isoformat(),
                    "value": value,
                    "unit": unit
                }
                self.client.send(payload)
            except Exception as e:
                print(f"[Logger] Błąd wysyłania do klienta sieciowego: {e}")

        if len(self.buffer) >= self.buffer_size:
            self._flush()

        self._rotate()

    def _flush(self):
        if not self.current_writer:
            return

        for row in self.buffer:
            self.current_writer.writerow(row)
            self.line_count += 1

        self.buffer.clear()
        if self.current_file:
            self.current_file.flush()

    def _rotate(self, force=False):
        now = datetime.now()
        filename = now.strftime(self.filename_pattern)
        filepath = os.path.join(self.log_dir, filename)

        rotate_by_time = (now - self.last_rotation_time).total_seconds() >= self.rotate_every_hours * 3600
        rotate_by_size = os.path.exists(filepath) and os.path.getsize(filepath) > self.max_size_mb * 1024 * 1024
        rotate_by_lines = self.line_count >= self.rotate_after_lines

        if force or rotate_by_time or rotate_by_size or rotate_by_lines or self.current_filename != filename:
            if self.current_file:
                self._flush()
                self.current_file.close()

                old_path = os.path.join(self.log_dir, self.current_filename)
                archived_path = self._get_next_available_filename(self.archive_dir, self.current_filename)
                if os.path.exists(old_path):
                    os.rename(old_path, archived_path)

            self.last_rotation_time = now
            self.line_count = 0
            self.current_filename = filename
            self.current_file = open(filepath, "a", newline="", encoding="utf-8-sig")
            self.current_writer = csv.writer(self.current_file)

            if os.stat(filepath).st_size == 0:
                self.current_writer.writerow(["timestamp", "sensor_id", "value", "unit"])

            self._cleanup_archives()

    def _cleanup_archives(self):
        now = datetime.now()
        cutoff_time = now - timedelta(days=self.retention_days)

        for fname in os.listdir(self.archive_dir):
            fpath = os.path.join(self.archive_dir, fname)
            if not os.path.isfile(fpath):
                continue
            try:
                mod_time = datetime.fromtimestamp(os.path.getmtime(fpath))
                if mod_time < cutoff_time:
                    os.remove(fpath)
                    print(f"[Logger] Usunięto archiwalny plik: {fname}")
            except Exception as e:
                print(f"[Logger] Błąd podczas usuwania pliku {fname}: {e}")

    def read_logs(self, start: datetime, end: datetime, sensor_id: Optional[str] = None) -> Iterator[Dict]:
        def process_file(filepath: str):
            try:
                with open(filepath, newline="", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            ts = datetime.fromisoformat(row["timestamp"])
                            if start <= ts <= end and (sensor_id is None or row["sensor_id"] == sensor_id):
                                yield {
                                    "timestamp": ts,
                                    "sensor_id": row["sensor_id"],
                                    "value": float(row["value"]),
                                    "unit": row["unit"]
                                }
                        except Exception:
                            continue
            except Exception:
                pass

        for filename in os.listdir(self.log_dir):
            filepath = os.path.join(self.log_dir, filename)
            if os.path.isfile(filepath) and filename.endswith(".csv"):
                yield from process_file(filepath)

        for filename in os.listdir(self.archive_dir):
            filepath = os.path.join(self.archive_dir, filename)
            if os.path.isfile(filepath) and filename.endswith(".csv"):
                yield from process_file(filepath)

    def _get_next_available_filename(self, directory: str, base_name: str) -> str:
        name, ext = os.path.splitext(base_name)
        counter = 1
        new_name = base_name

        while os.path.exists(os.path.join(directory, new_name)):
            new_name = f"{name}_{counter}{ext}"
            counter += 1

        return os.path.join(directory, new_name)
