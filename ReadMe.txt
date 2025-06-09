Instrukcja uruchomienia systemu symulacji czujników

Instalacja zależności
Zainstaluj wymagane biblioteki za pomocą polecenia:

pip install -r requirements.txt
Opis systemu
System symuluje pracę czujników w środowisku monitoringu. Obsługiwane są następujące czujniki:

temperatura,

wilgotność,

ciśnienie,

światło.

Szczegóły działania czujników:

Temperatura i światło generowane są na podstawie funkcji sinusoidalnej (szczyt przypada na godzinę 15:00) z losowym szumem.

Na początku wybierany jest jeden z trzech predefiniowanych przedziałów temperatury (predefined_ranges).

Anomalie temperatury: między 6:00 a 15:00 możliwe jest wystąpienie anomalii (+/-5°C przez 3 godziny) z 90% prawdopodobieństwem.

Anomalie światła: podobnie jak w przypadku temperatury – 90% szans na zmianę wartości o +/-3500 lumenów w przedziale godzin 6:00–15:00 przez 3 godziny.

Wilgotność zależy od temperatury. Każda wartość temperatury odpowiada konkretnemu zakresowi wilgotności, z którego losowana jest wartość.

Ciśnienie generowane jest również na podstawie ograniczonej funkcji sinusoidalnej z losowym szumem.

Zmiana rytmu pogodowego po północy (00:00):

50% szans na utrzymanie tego samego przedziału temperatury,

25% szans na jego rozszerzenie lub zawężenie o ±5°C (np. z [-5, 15] na [0, 20]).
*Uwaga, nowa sesja moze wybrac nowy przedzial temperatury i jego dane rowniez beda wysylane do
tego samego pliku csv(do pliku csv z tego samego dnia),wiec jezeli chcesz miec ten sam przedzial niezaleznie od sesji
zakomentuj odpowiednie linie w pliku temperature_sensor (są tam wskazane, kilka lini)
**anomalie dla temperatur i swiatla da sie łatwo edytowac (szanse na anomalie) w lini  "if np.random.rand() < 0.9:" <--teraz wynoszą 90%
=========================Uruchamianie programu================================

Najwygodniejszy sposób testowania systemu to użycie GUI i terminala:

W pierwszym terminalu uruchom GUI:

python run_gui.py
Następnie kliknij przycisk Start w interfejsie graficznym.

W drugim terminalu uruchom silnik symulacji:
python main.py (main.py jest w tym przypadku klientem aplikacyjnym)

Aby zakończyć działanie programu, użyj skrótu klawiszowego Ctrl + C.W obu terminalach. Może to potrwać chwilę – poczekaj na komunikat:
"Zakończono. Zajrzyj do folderu 'logs/'". tam gdzie zostal odpalony main.py
**mozesz tez użyć run_all.py(w jednym terminalu) ale jest to mniej przyjazne w rozpoznawaniu błędów
Dodatkowe informacje:

Możesz zatrzymać i ponownie wystartować GUI (w ramach tej samej sesji).

Odczyty są pobierane co ok. 10 sekund (dokładnie: frequency = 8 + ~2 sekundy opóźnienia).

Na ich podstawie obliczane są średnie wartości:

co godzinę – wyświetlana jest ostatnia średnia godzinowa,

co 12 godzin – wyświetlana jest ostatnia średnia z 12 godzin.



 