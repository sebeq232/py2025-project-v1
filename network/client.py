import socket
import json
from network.config import load_config
import os
from typing import Optional
from datetime import datetime


class NetworkClient:
    def __init__(self, config_path="../configs/client_config.yaml"):
        # absolutna sciezka na podstawie lokalizacji pliku
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), config_path))
        config = load_config(config_path)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 9000)
        self.timeout = config.get("timeout", 5.0)
        self.retries = config.get("retries", 3)
        self.sock = None

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self._send_event("started connection")

    def send(self, data: dict) -> bool:
        message = json.dumps(data) + '\n'
        for attempt in range(1, self.retries + 1):
            try:
                with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                    sock.sendall(message.encode('utf-8'))
                    ack = b""
                    while not ack.endswith(b'\n'):
                        chunk = sock.recv(1024)
                        if not chunk:
                            break
                        ack += chunk

                    if ack.strip() == b"ACK":
                        return True
                    else:
                        print(f"[Client] Oczekiwano ACK, otrzymano: {ack}")
            except (ConnectionRefusedError, socket.timeout, OSError) as e:
                print(f"[Client] Próba {attempt}/{self.retries} nieudana: {e}")
        return False

    def close(self):
        if self.sock:
            self._send_event("closed connection")
            self.sock.close()

    def _send_event(self, event: str, details: Optional[dict] = None):
        message = {
            "type": "client_event",
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        try:
            self.send(message)
        except Exception as e:
            print(f"[Logger] Błąd wysyłania eventu '{event}': {e}")
