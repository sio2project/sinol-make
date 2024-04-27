<!-- Czytelny widok tego dokumentu można znaleźć pod tym linkiem. -->
<!-- https://github.com/Stowarzyszenie-Talent/st-make/tree/main/example_package -->

# **Szablon paczki**

- [**Ogólne informacje**](#ogólne-informacje)
- [**doc**](#doc)
  - [**talentTex.cls**](#talenttexcls)
- [**prog**](#prog)
  - [**Rozwiązania**](#rozwiązania)
  - [**ingen**](#ingen)
  - [**inwer**](#inwer)
  - [**checkerka**](#checkerka)
  - [**oi.h**](#oih)
    - [**Scanner (Wczytywanie)**](#scanner-wczytywanie)
      - [Są 3 tryby wczytywania danych](#są-3-tryby-wczytywania-danych)
      - [**Najważniejszą funkcją jest wczytywanie** i realizuje ją w następujący sposób](#najważniejszą-funkcją-jest-wczytywanie-i-realizuje-ją-w-następujący-sposób)
    - [**CheckerVerdict**](#checkerverdict)
    - [**checker\_test**](#checker_test)
    - [**InwerVerdict**](#inwerverdict)
    - [**bug**](#bug)
    - [**oi\_assert**](#oi_assert)
    - [**Random**](#random)
- [in i out](#in-i-out)
  - [Testy ocen](#testy-ocen)
  - [Generowanie](#generowanie)
- [dlazaw](#dlazaw)
- [attachment](#attachment)
- [**config.yml**](#configyml)
  - [Interactive tasks](#interactive-tasks)
  - [Time](#time)
  - [Memory](#memory)
  - [Title](#title)
  - [Scores](#scores)
  - [Task ID](#task-id)
  - [Contest type](#contest-type)
  - [Expected scores](#expected-scores)

## **Ogólne informacje**

Jest to przykładowy szablon paczki, który zaleca się używać.
Jedynie dla zadań interaktywnych jest on inny i jeszcze nie został przygotowany.

Aktualna wersja paczki znajduje się na [GitHubie](https://github.com/Stowarzyszenie-Talent/st-make/tree/main/example_package).
Można ją pobrać używając komendy `st-make init ID`, gdzie ID to 3-literowy skrót zadania.

Do kompilacji paczki i innych czynności używamy skryptu `st-make`.
Jest on dostępny na [GitHubie](https://github.com/Stowarzyszenie-Talent/st-make).
Można go pobrać komendą `pip3 install st-make`.

## **doc**

Ten folder zawiera wszystkie dokumenty i pliki potrzebne do ich wygenerowania (pdf, tex, doc, img, ...).

- `{ID}zad.tex` - treść zadania.
- `{ID}opr.tex` - dokument z opracowaniem zadania.
Posiada wszelkie informacje techniczne o zadaniu.
- `{ID}opi.tex` - dokument z opisem rozwiązania.

Do kompilacji dokumentów latexowych służy `st-make doc`.

### **talentTex.cls**

Jest to klasa używana w plikach `.tex`.
Nadaje ona odpowiedni wygląd dokumentom.
Automatycznie tworzy ona nagłówki i stopki.
Wystarczy że stworzymy treść dokumentu pomiędzy znacznikami `\start` i `\finish`.
Dodatkowo udostępnia następujące funkcje:

- `\tc{n}` - Stylizuje podany tekst na talentowy kolor.
- `\plainimg{img1.jpg}` - Wstawia obrazek o podanej ścieżce.
- `\img{img1.jpg}{opis}{t/b}` - Wstawia obrazek o podanej ścieżce z opisem u góry lub na dole.
Można też `\timg{img1.jpg}{opis}`, `\bimg{img1.jpg}{opis}`.
- `\start{}` - Rozpoczyna treść, musi być na samym początku treści dokumentu.
- `\finish{}` - Kończy treść, musi być na samym końcu treści dokumentu.
- `\tSection{text}` - Nagłówek w stylu talentu.
- `\tCustomSection{text}{0pt}` - Nagłówek w stylu talentu, z możliwością ustawienia odstępu od poprzedniego akapitu.
- `\tSmallSection{text}` - Mały nagłówek w stylu talentu.
- `\makecompactexample{id}` - dodaje automatycznie test "abc0{id}" z paczki, wejście i wyjście będą obok siebie.
- `\makestandardexample{id}` - dodaje automatycznie test "abc0{id}" z paczki, wejście i wyjście będą pod sobą.

Przy kompilacji testy są automatycznie czytane z folderów ./in i ./out.
Należy się upewnić, że są one wygenerowane w momencie kompilacji treści.
Te polecenia również tworzą nagłówek "Wejście" i "Wyjście".

- `\ocen{\testOcen{}{} ...}` - Lista wszystkich testów ocen.
- `\testOcen{nazwa_testu}{opis_testu}` - Pojedynczy test ocen z opisem.
- `\ocenTable{}` - Tworzy tabelę z podzadaniami. Automatycznie tworzy nagłówek (Nr & Ograniczenia & Punkty).
- `\ocenRow{nr & opis & punkty}` - Pojedynczy wiersz tabeli: kolejne komórki powinny być rozdzielone znakiem &.
  Jeśli chcesz mieć 2 linie w pojedynczej komórce tabeli użyj `\ocenElement{text}`.

## **prog**

W tym katalogu znajdują się wszystkie programy.
Ważną rzeczą jest aby programy **kompilowały się bez warningów** przy użyciu `st-make`.

### **Rozwiązania**

Nazewnictwo:

- `{ID}.` - **Rozwiązanie wzorcowe**, np. `abc.cpp`.
Ten program jest wzorcowym i to on generuje poprawne odpowiedzi.
- `{ID}{cyfra}{suffix}.` - Rozwiązania poprawne, na przykład: `abc.cpp`, `abc.cpp`, `abc.cpp`, `abc104.py`,
- `{ID}s{cyfra}{suffix}.` - Rozwiązania wolne, na przykład: `abcs1.cpp`, `abcs3_brute_n_kwadrat.cpp`, `abcs13.py`,
- `{ID}b{cyfra}{suffix}.` - Rozwiązania niepoprawne, na przykład: `abcb1.cpp`, `abcb3_heura.cpp`, `abcb10.py`,

Każdy program musi mieć inną nazwę po usunięciu rozszerzeń.

Zalecamy nazywać programy kolejnymi cyframi. `abc.cpp`, `abc2.cpp`, `abc3.py`, `abcs1.cpp`, `abcs2.cpp`, `abcb1.cpp`, ...

Rozwiązania poprawne to takie które działają w odpowiedniej złożoności i dają dobre wyniki (wolny Python też tu należy).
Programy wolne to takie co mają gorszą złożoność czasową i dają dobre wyniki.
Programy błędne to takie co dają złe wyniki.
Na przykład jak mamy wolny program co daje złe wyniki to damy go do grupy błędnych.

Każdy kod w pierwszych liniach powinien mieć komentarz opisujący: autora kodu, nazwę zadania, złożoność czasową i pamięciową oraz opis jakie to jest rozwiązanie.
Dodatkowo kody powinny być czytelne, najlepiej zaopatrzone w komentarze i nie zawierające makr oraz define-ów itp. co utrudnia ich czytanie.

### **ingen**

`{ID}ingen.cpp`

Generuje pliki `.in`.
Dzięki temu, że generator jest w paczce, łatwiej będzie w przyszłości zedytować testy.

Ingen powinien:

- Po uruchomieniu (bez żadnych argumentów) wygenerować w bieżącym katalogu odpowiednie pliki z danymi wejściowymi.
- Generować liczby losowe za pomocą `oi.h`.
- Każdy test (lub grupa testów) powinna mieć osobnego seeda.
- Być w pełni deterministyczny, czyli za każdym razem ma generować dokładnie te same testy.
  Na przykład można inicjować ziarno generatora liczb losowych stałą wartością.
- Idealnie odzwierciedlać format testu, podanego w treści zadania.
- Na końcu pliku wypisać znak końca linii, a na końcu wierszy **nie** wypisywać białych znaków.

### **inwer**

`{ID}inwer.cpp`

Służy do sprawdzenia czy pliki `.in` spełniają założenia z treści.
Jednocześnie pokazuje przydatne informacje o testach.

Inwer powinien:

- Wczytywać plik wejściowy za pomocą pakietu `oi.h`.
- Zawierać ograniczenia z treści zadania w formie stałych.
  Duże stałe podajemy w sposób czytelny, np. jako iloczyny innych stałych lub w notacji naukowej.
- W przypadku poprawnej weryfikacji ma wypisać w jednej linii krótką charakterystykę testu
  (wartości najważniejszych parametrów) i skończyć działanie kodem 0.
  Wypisany komentarz ma na celu upewnienie się, że test należy do odpowiedniej grupy oraz, że każda grupa testów zawiera testy z wartościami brzegowymi
  (na przykład minimalne i maksymalne ograniczenia na `n`, drzewa w postaci ścieżki i gwiazdy, itd).
- Wypisać również numery podzadań, które pasują do tego testu,
  lub nazwy testów ocen, które pasują do tego testu.
  (należy inwerem się upewnić, że testy przykładowe i ocen są dokładnie takie, jak w treści).
- W przypadku błędnej weryfikacji wypisać informację o błędzie i skończyć działanie kodem niezerowym.
  Można używać funkcji `assert` a najlepiej `oi_asert` z `oi.h`.
- Sprawdzać, czy dane wejściowe są idealnie zgodne z opisem treści zadania, **z dokładnością do każdego białego znaku**.
  Nie mogą pojawić się żadne zbędne białe znaki.

### **checkerka**

`abcchk.cpp`

W przypadku zadań z jednoznaczną odpowiedzią nie dodajemy tego programu. System SIO ma domyślną chekierkę, która porównuje odpowiedź z wzorcową.

W przypadku zadań, w których istnieje wiele poprawnych odpowiedzi, paczka musi zawierać weryfikator danych wyjściowych.
Oprócz tego, do każdego komunikatu, który może wypisać weryfikator, powinno istnieć rozwiązanie błędne lub istnieć w programie test jednostkowy, który powoduje wypisanie tego komunikatu.

Checkerka powinna:

- Być **napisana wydajnie**, gdyż w trakcie zawodów jest on uruchamiany bardzo wiele razy.
- Być uruchamiana w następujący sposób: `./{ID}chk wejście wyjście_zawodnika wyjście_wzorcowe`.
- Wczytywać pliki za pomocą pakietu `oi.h`.
- Wypisać odpowiedź w następującym formacie:
  - Pierwszy wiersz powinien zawierać jedno słowo:
    - `OK` - jeśli odpowiedź jest poprawna, lub
    - `WRONG`-  w przeciwnym przypadku.
  - Drugi wiersz (opcjonalnie) powinien zawierać komentarz do
    odpowiedzi zawodnika (np. przyczyny uznania rozwiązania za niepoprawne).
  - Trzeci wiersz (opcjonalnie) powinien zawierać jedną liczbę całkowitą
    z przedziału [0, 100] oznaczającą (w procentach) liczbę punktów, którą należy przyznać zawodnikowi za test.
- Domyślnie za samo `OK` dostaje się 100 punktów, a za `WRONG` 0 punktów.
- Pozwala na zbędne białe znaki tylko i wyłącznie na końcu linii i na końcu wyjścia oraz na **brak końca linii na końcu wyjścia** (ważne!).
- Działał poprawnie nawet dla bardzo złośliwych danych (np. nie można nic zakładać o długości ciągów znaków znajdujących się w odpowiedzi zawodnika).

### **oi.h**

Jest to biblioteka ułatwiająca pisanie programów w paczce.
Jednocześnie pozawala uniknąć masy błędów.
Jest wymagane by wszędzie tam gdzie to możliwe jej używać.
Umożliwia ona nam następujące rzeczy.

#### **Scanner (Wczytywanie)**

Służy do wczytywania danych z plików.
Dzięki temu nie musimy martwić się co user dał na wejściu, tylko mówimy co oczekujemy.

##### Są 3 tryby wczytywania danych

| tryb       | eof              | nl           | destruktor   |
| ---------- | :--------------: | :----------: | :----------: |
| UserOutput | ignoruje nl i ws | ignoruje ws  | wczytuje eof |
| Lax        | ignoruje nl i ws | ignoruje ws  | -            |
| TestInput  | -                | -            | wczytuje eof |

Jak widać służą one do pomijania bądź nie, pustych linii na końcu pliku i białych znaków na końcu linii oraz czy zostanie na koniec jeszcze wczytany eof.
Nadal warto (i zalecamy) sprawdzać samemu czy nastąpił koniec pliku.

Aby móc korzystać z wczytywania trzeba zainicjować scanner:

- `scanner = oi::Scanner{stdin, oi::Scanner::Mode::[tryb], oi::Lang::[PL/EN]};`
- `scanner = oi::Scanner(argv[1], oi::Scanner::Mode::[tryb], [scanner_lang]);`

Teraz scanner możemy używać jak cin, czyli `scanner >>`.
Wersje językowe są dostępne tylko te 2, w tych językach będą wypisywane komunikaty związane z błędami wczytywania.

Do wywoływania błędów scanner używa funkcji error(Msg&&... msg), która, wypisuje błędy podczas wczytywania.
W schemacie: ```[mode]Wiersz [last_char_pos.line], [pozycja] [last_char_pos.pos]: [msg]...```

##### **Najważniejszą funkcją jest wczytywanie** i realizuje ją w następujący sposób

- pojedynczy znak - `>> 'x' >> ' '` -
Pozwala wczytać pojedynczy, konkretny znak.
- EOF (koniec pliku) - `>> oi::eof` -
Wczytuje koniec pliku zgodnie z trybem pracy.
- EOL (koniec linii) - `>> oi::nl` -
Wczytuje koniec linii zgodnie z trybem pracy.
- ignorowanie znaków białych - `>> oi::ignore_ws` -
Pomija wszystkie znaki białe do następnego znaku lub końca linii.
- linia - `>> oi::Line(a, b)` -
Wczytuje cały wiersz (łacznie z białymi znakami) do zmiennej `a`, która jest stringiem. Długość linii ma być nie dłuższy niż `size_t b`.
- string - `>> oi::Str(a, b)` -
Wczytuje string (słowo do pierwszego białego znaku) do zmiennej `a` o maksymalnej długości `b`.
- char - `>> oi::Char(a, b)` -
Wczytuje znak do `char a` z podanej puli dozwolonych charów `b` gdzie `b` to `std::string` lub `char*`.
- liczba - `>> oi::Num(a, b, c)` -
Wczytuje liczbę `a` (int, float, ...) która ma być w podanym zakresie od `b` do `c`.

Podawanie zakresu może wydawać się żmudne, ale pozwala zapobiec, że ktoś poda nieskończenie długie słowo, albo że przegapimy sprawdzenie czy liczba jest w odpowiednim zakresie.

Wszystkie te funkcje w przypadku gdy wczytają coś, co nie pasuje do opisu, zgłoszą błąd i zakończą działanie programu z kodem niezerowym.

#### **CheckerVerdict**

oi.h udostępnia nam obiekt `checker_verdict` klasy CheckerVerdict.
Używamy go standardowo `oi::checker_verdict.[coś]`.
Udostępnia on nam poniższe funkcje:

- **exit_ok()** -
Kończy sprawdzanie z sukcesem dając 100 punktów.
Zwraca `OK\n\n100\n`.
- **exit_ok_with_score(int score, Msg&&... msg)** -
Kończy sprawdzanie z sukcesem z podanym wynikiem i wiadomością/ciami.
Zwraca `OK\n[msg]\n[score]\n`.
- **set_partial_score(int score, Msg&&... msg)** -
Ustawia wynik częściowy który zostanie zwrócony gdy nastąpi błąd.
Czyli zamiast 0 punktów otrzyma się tyle ile się przypisało z danym komentarzem.
- **exit_wrong(Msg&&... msg)** -
Kończ sprawdzanie z błędem i daje 0 punktów, chyba, że ustawiono partial_score.
Zwraca `WRONG\n[msg]\n0\n` albo `OK\n[partial_score_msg]; [msg]\n[partial_score]\n` albo `OK\n[msg]\n[partial_score]\n`.

Jeżeli w programie używamy `partial_score` to:

- Trzymajmy zmienną mówiącą jaki jest wynik częściowy.
- Trzymajmy zmienną mówiącą ile user może zdobyć punktów (do_zdobycia).
- Używamy `exit_ok_with_score(do_zdobycia)` zamiast `exit_ok()`.

#### **checker_test**

oi.h udostępnia możliwość pisania testów do chekerki.
Te testy są uruchamiane tylko lokalnie.
Istnieją 2 sposoby ich pisania.
Przykład obu z nich jest zaimplementowany w przykładowym `abcchk.cpp`.

#### **InwerVerdict**

oi.h udostępnia nam obiekt `inwer_verdict` klasy InwerVerdict.
Używamy go jako strumień wyjścia, a mianowicie:
`oi::inwer_verdict.[coś] << [msg]`.
Gdzie `msg` to wiadomość którą chcemy pokazać przed zakończeniem.
Natomiast `coś` to jedna z podanych opcji:

- **exit_ok()** - Kończy program pomyślnie.
- **exit_wrong()** - Kończy program z błędem.

My będziemy używać tylko `oi::inwer_verdict.exit_ok() << [msg]`.
Druga opcja jest używana systemowo i będziemy ją zgłaszać np. przez `oi_assert()` lub `oi::bug(Msg&&... msg)`.

#### **bug**

Wywołując `oi::bug(Msg&&... msg)`, program zakończy się niepowodzeniem.
Wyświetli on wtedy podaną wiadomość/ci, w formacie `BUG: [msg]` i zakończy działanie z kodem 2.

#### **oi_assert**

Działa podobnie do zwykłego asserta.
Wywołując `oi_assert(condition, msg...);`, sprawdzi założenie, a jak będzie błędne to poda dokładny komunikat co jest nie tak.
Wypisze on `[FILE]:[LINE]: [func]: Assertion '[condition]' failed.` lub
`[FILE]:[LINE]: [func]: Assertion '[condition]' failed: [msg]`

#### **Random**

Służy do losowania wartości i jest wymagane używać go zamiast zwykłego rand(), std::mt19937 lub innych mechanizmów losujących.
Zapewnia on uniwersalny sposób generowania liczb (pseudo) losowych.
Klasa `Random` udostępnia:

- **Random(uint_fast64_t seed = 5489)**
- **void shuffle(T begin, T end)**
- **void shuffle(T& container)**
- **operator()(T min, T max)**

Tak więc aby utworzyć obiekt robimy `oi::Random rng;` lub `oi::Random rng(seed);`.
Aby zmienić seed nadpisujemy `rng = oi::Random(new_seed);`.
Aby użyć robimy `rng(min, max);`.
Pod wartości min i max podstawiamy zakres z jakiego chcemy wylosować wartość.
Obsługiwane są wszystkie typy numeryczne (int, float, char, ...).
Możemy również pomieszać jakiś kontener Używając `rng.shuffle()`, podając mu albo kontener albo początek i koniec przedziału.

## in i out

Są to foldery, w których znajdują się testy.
Testy nazywamy `{ID}{grupa}{nr_testu}.{in/out}`.

Grupa:

- 0 - są to testy wstępne, nie liczą się do oceny i uczestnik ma do nich dostęp na zawodach.
- 1,2,... - zwyczajna grupa, punkty za nią dostaniemy jak przejdą wszystkie testy z danej grupy.

nr_testu to ciąg alfanumeryczny, zaczynający się od litery.
Przyjeło się, że są to kolejne litery alfabetu angielskiego.
A jak się skończą to stawiemy wiecej liter: a, ... z, aa, ab, ..., zz, aaa, ...

Przykładowe nazwy to: `abc0a.in`, `abc1a.in`, `abc1b.out`, `abc3z.in`, `abc3aa.in`.

Ciekawą formą nazywania jest też `{ID}{grupa}t{nr}`, np `abc1t1.in`, jednak nie chce się przyjąć.

### Testy ocen

Anomalią od powyższych reguł są testy ocen.
Testy opisane jako `{ID}{liczba}ocen.in` są zaliczane jako **testy wstępne** (grupa 0).
Na przykład `abc1ocen.in`, `abc2ocen.out`.
Obecnie można dawać po prostu `0a`, `0b`, ... `0e`, a w treści podać tylko np a i b.

### Generowanie

Pliki in generuje ingen, a pliki out generuje program wzorcowy.
Testy korzystające z ingen będą tworzone dopiero na systemie, więc folder in będzie najczęściej pusty.
To samo tyczy się plików out, one też są generowane na systemie.
Możemy jednak sami dodać ręcznie testy, które nie są tworzone przez ingena i one tu mają się znajdować.
Jednak, najlepiej by wszystko było generowane przez ingen.
W przypadku konfliktu nazwy ręcznego i automatycznego testu, ten automatyczny nadpisze ręczny.

## dlazaw

W tym folderze są trzymane pliki dla zawodników.
Między innymi przydaje się w zadaniach interaktywnych gdzie jest udostępniana jakaś biblioteczka.

**Uwaga** testów ocen tu nie dajemy, są one automatycznie dodawane podczas eksportu paczki przy użyciu `st-make export`.

## attachment

Pliki znajdujące się w tym folderze są udostępniane bezpośrednio użytkownikowi.
`st-make export` tworzy ten folder i dodaje do niego skompresowany folder `dlazaw` oraz skompresowany folder z testami wstępnymi i ocen.

## **config.yml**

Wszystkie informacje opisane tutaj są również opisane w configu.

For more options see: [link to github](https://github.com/sio2project/sinol-make/blob/main/example_package/config.yml).
Or here are some basic ones.

### Interactive tasks

Extra compilation arguments can be defined in `extra_compile_args` key.
Each language can have different extra arguments.
Additional files used in compilation can be defined in `extra_compilation_files` key.
They are copied to the directory where the source code is compiled.
All languages have the same additional files.

```text
extra_compilation_args:
   cpp: ['abclib.cpp']

extra_compilation_files: ['abclib.cpp', 'abclib.h']
```

### Time

```text
time_limit: 1000 # ms

time_limits:
  2: 2000
  5: 7000
```

More precise time limit for each group or test can be defined in `time_limits` key.
The more precise time limit has higher priority (first group, then global time limit).

### Memory

```text
memory_limit: 262144 # kB

memory_limits:
  3: 131072
  4: 131072
```

More precise memory limits can be defined in `memory_limits` key.
Same as with time limits, the more precise memory limit has higher priority.

### Title

```text
title: Przykładowy tytuł
```

Task title visible in the system.
If there are Polish characters, they should be written for better readability.

### Scores

```text
scores:
  1: 20
  2: 80
```

Number of points for each group can be defined in `scores` key.
If this key is not specified, then all groups have the same number of points.
(if number of groups doesn't divide 100, then the last groups will have the remaining points).
Group 0 always has zero points.

### Task ID

```text
sinol_task_id: abc
```

This key represents the short name (consisting of 3 letters) of the task.
The names of files in `prog/`, `doc/`, `in/` and `out/` directories have to start with this task id.
This key is only used by `st-make`: running `st-make export` creates
an archive with the proper name, which sio2 uses as the task id.

### Contest type

```text
sinol_contest_type: talent
```

sinol-make can behave differently depending on the value of `sinol_contest_type` key.
Mainly, it affects how points are calculated.
If the key is not specified, then (in st-make) `talent` is used. In sinol-make (OI version) is used 'default'.

### Expected scores

```text
sinol_expected_scores: {}
```

st-make can check if the solutions run as expected when using `run` command.
Key `sinol_expected_scores` defines expected scores for each solution on each tests.
There should be no reason to change this key manually.
It is automatically generated and managed by st-make.
