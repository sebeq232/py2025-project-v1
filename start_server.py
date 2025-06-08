# tests/start_server.py

import sys
import os

# Dodaj katalog główny projektu do ścieżki importu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.server import NetworkServer

if __name__ == "__main__":
    server = NetworkServer()
    server.start()
