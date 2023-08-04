SIO2Jail OIEJQ
==============

OI's Experiment for Judging Quickly
to narzędzie OI do pomiaru czasu działania programów.

Intrukcja użytkowania:
----------------------

W katalogu /home/zawodnik/rozw/
Należy wpisać:
$ ./oiejq program_do_uruchomienia

Możesz też przekierować standardowe wejście/wyjście, albo przekazać
dodatkowe argumenty do programu.

$ ./oiejq program_do_uruchomienia <dane.in >wynik.out

Narzędziem powinno dać się uruchomić dowolny program,
np. interpreter pythona:

$ ./oiejq.sh python3

Licencja
--------

Skrypt wykorzystuje program SIO2Jail, którego źródła są dostępne
na licencji MIT pod adresem: 

https://github.com/sio2project/sio2jail

Szczegóły licencji znajdują się w pliku LICENSE.txt
