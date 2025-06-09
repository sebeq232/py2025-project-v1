import threading
import subprocess
import time

def run_gui():
    subprocess.run(["python", "run_gui.py"])

def run_main():
    time.sleep(2)  # Poczekaj 2 sekundy, żeby GUI zdążyło uruchomić serwer
    subprocess.run(["python", "main.py"])

if __name__ == "__main__":
    # Tworzy dwa wątki
    gui_thread = threading.Thread(target=run_gui)
    main_thread = threading.Thread(target=run_main)

    # Startuj oba
    gui_thread.start()
    main_thread.start()

    # Czekamy na zakończenie GUI (zamyka się tylko gdy GUI się zamknie)
    gui_thread.join()
    main_thread.join()
