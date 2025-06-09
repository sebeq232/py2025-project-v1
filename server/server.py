import socket
import threading
import json
import os
import logging
from network.config import load_config

class NetworkServer:
    def __init__(self, port=None):
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "configs", "server_config.yaml"))
        config = load_config(config_path)
        self.port = port if port is not None else config.get("port", 9000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1.0)
        self.logger = logging.getLogger('NetworkServer')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.running = False

        # lista funkcji wywoływanych przy odbiorze danych
        self._data_callbacks = []
        self._error_callback = None
    def register_callback(self, callback):
        self._data_callbacks.append(callback)
    def register_error_callback(self,callback):
        self._error_callback = callback
    def start(self):
        try:
            self.sock.bind(("0.0.0.0", self.port))
            self.sock.listen()
            self.running = True
            self.logger.info(f"Serwer nasłuchuje na porcie {self.port}")

            while self.running:
                try:
                    client_socket, addr = self.sock.accept()
                    threading.Thread(target=self._handle_client, args=(client_socket, addr), daemon=True).start()
                except socket.timeout:
                    continue
        except Exception as e:
            self.logger.error(f"Błąd serwera: {e}")
            if self._error_callback:
                self._error_callback(e)
        finally:
            self.sock.close()
            self.logger.info("Serwer zatrzymany")

    def stop(self):
        self.running = False

    def _handle_client(self, client_socket, addr):
        with client_socket:
            try:
                data = b""
                while not data.endswith(b"\n"):
                    part = client_socket.recv(1024)
                    if not part:
                        return
                    data += part

                message = json.loads(data.decode())
                print(f"[RECEIVED from {addr}]: {message}")

                # 🔔 powiadom GUI o nowych danych
                for callback in self._data_callbacks:
                    callback(message)

                client_socket.sendall(b"ACK\n")
            except Exception as e:
                self.logger.error(f"[ERROR] Błąd klienta {addr}: {e}")
