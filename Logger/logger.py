import os
import json
import csv
import logging
import zipfile
from datetime import datetime, timedelta
from typing import Optional, Iterator, Dict

class Logger:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            config = json.load(f)

        self.log_dir = config.get("log_dir", "./logs")
        self.filename_pattern = config.get("filename_pattern", "sensors_%Y%m%d.csv")
        self.buffer_size = config.get("buffer_size", 200)
        self.rotate_every_hours = config.get("rotate_every_hours", 24)
        self.max_size_mb = config.get("max_size_mb", 5)
        self.rotate_after_lines = config.get("rotate_after_lines", 100000)
        self.retention_days = config.get("retention_days", 30)

        self.buffer = []
        self.current_file = None
        self.current_writer = None
        self.current_file_path = None
        self.current_start_time = None
        self.current_line_count = 0

        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(os.path.join(self.log_dir, "archive"), exist_ok=True)

    def start(self) -> None:
        now = datetime.now()
        filename = now.strftime(self.filename_pattern)
        self.current_file_path = os.path.join(self.log_dir, filename)
        is_new_file = not os.path.exists(self.current_file_path)

        self.current_file = open(self.current_file_path, "a", newline="")
        self.current_writer = csv.writer(self.current_file)

        if is_new_file:
            self.current_writer.writerow(["timestamp", "sensor_id", "value", "unit"])

        self.current_start_time = now
        self.current_line_count = 0

    def stop(self) -> None:
        self._flush()
        if self.current_file:
            self.current_file.close()
            self.current_file = None

    def log_reading(self, sensor_id: str, timestamp: datetime, value: float, unit: str) -> None:
        self.buffer.append([timestamp.isoformat(), sensor_id, value, unit])
        if len(self.buffer) >= self.buffer_size:
            self._flush()
        if self._should_rotate():
            self._rotate()

    def read_logs(self, start: datetime, end: datetime, sensor_id: Optional[str] = None) -> Iterator[Dict]:
        for filename in os.listdir(self.log_dir):
            if not filename.endswith(".csv"):
                continue
            path = os.path.join(self.log_dir, filename)
            yield from self._read_file(path, start, end, sensor_id)

        archive_dir = os.path.join(self.log_dir, "archive")
        for filename in os.listdir(archive_dir):
            if not filename.endswith(".zip"):
                continue
            path = os.path.join(archive_dir, filename)
            with zipfile.ZipFile(path, 'r') as zf:
                for inner_name in zf.namelist():
                    with zf.open(inner_name) as f:
                        lines = f.read().decode("utf-8").splitlines()
                        reader = csv.DictReader(lines)
                        for row in reader:
                            ts = datetime.fromisoformat(row["timestamp"])
                            if start <= ts <= end and (sensor_id is None or row["sensor_id"] == sensor_id):
                                yield {
                                    "timestamp": ts,
                                    "sensor_id": row["sensor_id"],
                                    "value": float(row["value"]),
                                    "unit": row["unit"]
                                }

    def _flush(self):
        if self.buffer:
            for row in self.buffer:
                self.current_writer.writerow(row)
            self.current_file.flush()
            os.fsync(self.current_file.fileno())
            self.current_line_count += len(self.buffer)
            self.buffer.clear()

    def _should_rotate(self) -> bool:
        if not self.current_start_time:
            return False
        if (datetime.now() - self.current_start_time).total_seconds() / 3600 >= self.rotate_every_hours:
            return True
        if self.current_line_count >= self.rotate_after_lines:
            return True
        try:
            size_mb = os.path.getsize(self.current_file_path) / (1024 * 1024)
            if size_mb >= self.max_size_mb:
                return True
        except Exception as e:
            logging.warning(f"Nie można sprawdzić rozmiaru pliku: {e}")
        return False

    def _rotate(self):
        self._flush()
        if self.current_file:
            self.current_file.close()

        # Archiwizacja (ZIP)
        base = os.path.basename(self.current_file_path)
        archive_name = os.path.splitext(base)[0] + ".zip"
        archive_path = os.path.join(self.log_dir, "archive", archive_name)

        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self.current_file_path, arcname=base)

        os.remove(self.current_file_path)

        self._clean_old_archives()
        self.start()

    def _clean_old_archives(self):
        archive_dir = os.path.join(self.log_dir, "archive")
        now = datetime.now()
        for fname in os.listdir(archive_dir):
            path = os.path.join(archive_dir, fname)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                if (now - mtime).days > self.retention_days:
                    os.remove(path)
            except Exception as e:
                logging.warning(f"Nie można usunąć archiwum: {e}")

    def _read_file(self, path: str, start: datetime, end: datetime, sensor_id: Optional[str]) -> Iterator[Dict]:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ts = datetime.fromisoformat(row["timestamp"])
                if start <= ts <= end and (sensor_id is None or row["sensor_id"] == sensor_id):
                    yield {
                        "timestamp": ts,
                        "sensor_id": row["sensor_id"],
                        "value": float(row["value"]),
                        "unit": row["unit"]
                    }