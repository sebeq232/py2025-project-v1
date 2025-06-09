import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import socket

from server.server import NetworkServer
from network.config import load_config


class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Network Server GUI")

        self.port_var = tk.StringVar(value="9000")
        self.status_var = tk.StringVar(value="Zatrzymany")

        self.server = None
        self.running = False
        self.sensor_data = {}
        self.sensor_history = defaultdict(lambda: deque(maxlen=10000)) #bufor serwera

        # Do srednich
        self.last_hour_updated = None
        self.last_12h_updated = None
        self.hourly_avg_var = tk.StringVar(value="")
        self.avg12h_var = tk.StringVar(value="")

        self._setup_ui()
        self._refresh_ui()
        self._refresh_hourly_summary()
        self._refresh_12h_summary()

    def _setup_ui(self):
        top_frame = tk.Frame(self.master)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top_frame, text="Port:").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(top_frame, textvariable=self.port_var, width=6)
        self.port_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Start", command=self.start_server).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Stop", command=self.stop_server).pack(side=tk.LEFT, padx=5)

        columns = ["Sensor", "Wartość", "Jednostka", "Timestamp", "Śr. 1h", "Śr. 12h"]
        self.tree = ttk.Treeview(self.master, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.status_label = tk.Label(self.master, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.hourly_avg_label = tk.Label(self.master, textvariable=self.hourly_avg_var, anchor="w", fg="gray")
        self.hourly_avg_label.pack(fill=tk.X, padx=10, pady=(0, 0))

        self.avg12h_label = tk.Label(self.master, textvariable=self.avg12h_var, anchor="w", fg="gray")
        self.avg12h_label.pack(fill=tk.X, padx=10, pady=(0, 5))

    def start_server(self):
        port_str = self.port_var.get()
        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError("Port musi być liczbą z zakresu 1–65535")

            # Blokada znanych/zarezerwowanych portów
            if port < 1024:
                raise PermissionError(f"Port {port} jest zarezerwowany i wymaga uprawnień administratora.")

            # Wczesna walidacja dostępności portu
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                test_sock.bind(("0.0.0.0", port))
            except OSError as e:
                raise RuntimeError(f"Port {port} jest niedostępny: {e}")
            finally:
                test_sock.close()

        except Exception as e:
            messagebox.showerror("Błąd konfiguracji portu", f"Nie można użyć portu {port_str}:\n{e}")
            self.status_var.set("Błąd uruchamiania")
            return

        def run():
            try:
                self.server = NetworkServer(port=port)
                self.server.register_callback(self.on_new_reading)
                self.server.register_error_callback(self.on_server_error)
                self.server.start()
            except Exception as e:
                self.master.after(0, lambda: self.on_server_error(e))

        threading.Thread(target=run, daemon=True).start()
        self.running = True
        self.status_var.set(f"Nasłuchiwanie na porcie {port}")

    def stop_server(self):
        if self.server:
            self.server.stop()
            self.status_var.set("Zatrzymany")
            self.running = False

    def on_server_error(self, error):
        self.status_var.set("Błąd uruchamiania")
        messagebox.showerror("Błąd serwera", f"Nie udało się uruchomić serwera:\n{error}")

    def on_new_reading(self, reading):
        sensor_id = reading["sensor_id"]
        value = float(reading["value"])
        unit = reading["unit"]
        timestamp = datetime.fromisoformat(reading["timestamp"])

        self.sensor_data[sensor_id] = (value, unit, timestamp)
        self.sensor_history[sensor_id].append((timestamp, value))

    def _refresh_ui(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        now = datetime.now()
        for sensor_id, (value, unit, ts) in self.sensor_data.items():
            hist = self.sensor_history[sensor_id]
            avg_1h = self._calc_avg(hist, now - timedelta(hours=1))
            avg_12h = self._calc_avg(hist, now - timedelta(hours=12))
            self.tree.insert("", "end", values=(
                sensor_id,
                round(value, 2),
                unit,
                ts.strftime("%Y-%m-%d %H:%M:%S"),
                round(avg_1h, 2) if avg_1h else "-",
                round(avg_12h, 2) if avg_12h else "-"
            ))

        self.master.after(3000, self._refresh_ui)

    def _refresh_hourly_summary(self):
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)

        if self.last_hour_updated is None or current_hour > self.last_hour_updated:
            self.last_hour_updated = current_hour
            one_hour_ago = current_hour - timedelta(hours=1)
            summary = []

            for sensor_id, hist in self.sensor_history.items():
                avg = self._calc_avg(hist, one_hour_ago)
                if avg is not None:
                    unit = self.sensor_data[sensor_id][1]
                    summary.append(f"{sensor_id}: {round(avg, 2)} {unit}")

            self.hourly_avg_var.set("Średnia z ostatniej godziny:\n" + "\n".join(summary) if summary else "")

        self.master.after(3600000, self._refresh_hourly_summary)

    def _refresh_12h_summary(self):
        now = datetime.now()
        current_period = now.replace(minute=0, second=0, microsecond=0)
        if self.last_12h_updated is None or (current_period - self.last_12h_updated) >= timedelta(hours=12):
            self.last_12h_updated = current_period
            start_time = current_period - timedelta(hours=12)
            summary = []

            for sensor_id, hist in self.sensor_history.items():
                avg = self._calc_avg(hist, start_time)
                if avg is not None:
                    unit = self.sensor_data[sensor_id][1]
                    summary.append(f"{sensor_id}: {round(avg, 2)} {unit}")

            self.avg12h_var.set("Średnia z ostatnich 12h:\n" + "\n".join(summary) if summary else "")

        self.master.after(12 * 3600000, self._refresh_12h_summary)

    def _calc_avg(self, history, since_time):
        vals = [v for (t, v) in history if t >= since_time]
        return sum(vals) / len(vals) if vals else None


def run_gui():
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
