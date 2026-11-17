# Gleise und Durchgänge: wie oft muss ein Zug über den Berg? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-gleise-durchgaenge-demo.streamlit.app/)** -->

Konzept-Demo für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, eine von mehreren Demos über **Maschinen, die Folgen sortieren** (Stapel, Warteschlangen, Gleise). Hier sind es **Gleise als
Warteschlangen am Ablaufberg**: Ein Zug rollt auf k Gleise, die Gleise werden hintereinander abgezogen (ein **Durchgang**), und die Demo zählt, **wie viele Durchgänge** ein Zug mindestens braucht, bis er aufsteigend
sortiert steht. Sie nimmt gegenüber der Frage „sortiert die Maschine diesen Zug, ja oder nein?“ zwei Annahmen heraus: Die Zielgröße ist die **Zahl der Durchgänge** (nicht ja oder nein), und im letzten Experiment
dürfen **mehrere Wagen dieselbe Zielgruppe** haben (Gruppieren statt Sortieren). Nachbarn: [`ablaufberg-demo`](https://github.com/sebastian-hanisch/ablaufberg-demo) (Fall-Demo zur Zugbildung: Gruppieren, Wagenbewegungen, Bergzeit,
exakte Lösung mit CP-SAT), [`maschinen-vergleich-demo`](https://github.com/sebastian-hanisch/maschinen-vergleich-demo) (zehn Maschinen in einer Tabelle; die Zahlen der parallelen Warteschlangen stehen dort),
[`mehrere-durchlaeufe-demo`](https://github.com/sebastian-hanisch/mehrere-durchlaeufe-demo) (zählt umgekehrt, **wie viele Folgen** k Durchläufe durch einen Behälter schaffen),
[`zwei-stapel-serie-demo`](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo) (andere Maschine, ein Lauf), [`patience-stapel-demo`](https://github.com/sebastian-hanisch/patience-stapel-demo) (Platz einer Folge, längste Teilfolge),
[`tableaux-rsk-demo`](https://github.com/sebastian-hanisch/tableaux-rsk-demo) und [`zufallsfolgen-lis-demo`](https://github.com/sebastian-hanisch/zufallsfolgen-lis-demo) (Teilfolgen und ihre Länge bei Zufallsfolgen).

**Das Ankunftsmodell ist ausgedacht** (Modell V und alle Folgen gleich wahrscheinlich) und ein **Modell, kein Fall**: Es ist keine reale Ankunftsfolge, und keine gelesene Quelle liefert eine.

## Kernfrage

Wie viele Durchgänge braucht ein Zug mit k Gleisen mindestens, und was sagt die Radix-Zahl ⌈log_k n⌉ darüber? **Die Antwort hängt an einer einzigen Zahl des Zuges: der Zahl R seiner steigenden Folgen**, und die Radix-Zahl ist
der schlimmste Fall (der umgekehrte Zug); wie weit ein typischer Zug darunter liegt, hängt an n und k. Das Radix-Verfahren (Radix-Sortierung nach den Ziffern des Rangs zur Basis k, niedrigste Ziffer zuerst) und die Frage
(mehrstufiges Sortieren von Güterzügen) stammen aus der Literatur über Zugbildung (Jacob, Márton, Maue, Nunkesser; siehe „Quellen“); **die Gleichheit ⌈log_k n⌉ und die Formel ⌈log_k R⌉ dieser Demo sind nachgerechnet,
nicht aus einer gelesenen Quelle belegt**. Neuheit wird nicht behauptet; neu ist nur die Vorführbarkeit mit Zähleinheit.

## Warum dieses Problem

Naheliegend ist, ⌈log_k n⌉ als die Zahl der Durchgänge zu lesen. Das ist die Zahl für den schlimmsten Zug. Im ausgedachten Ankunftsmodell mit n = 10 Wagen und k = 2 Gleisen braucht ein gleichverteilter Zug im Mittel
2,861 Durchgänge gegen Radix 4, und nur 1 014 von 3 628 800 Folgen brauchen 4. Aber „Radix ist meist zu hoch“ gilt **nicht allgemein**: Der Anteil der Folgen unter Radix ist bei k = 2 genau 1/2 bei n = 2^r (geprüft für n = 4 bis 128) und sonst
zwischen 1/2 und 1 (n = 20 bis 200), bei k = 3 und mehr dagegen ein Sägezahn bis auf 0 (k = 3: 0,12 % bei n = 27; k = 6: praktisch 0 in 121 von 181 Werten von n zwischen 20 und 200). Mit Gleichständen (Gruppen)
ersetzt die Beschriftungszahl L das R, und bei freier Reihenfolge der Gruppen unterbietet die exakte Lösung Radix bei kleinen Zügen oft, bei großen nicht mehr (6 Gruppen, 3 Gleise: 93,8 % der Züge mit 8 Wagen, 0,0 % bei 40 Wagen; Zufallsproben aus 3 000 Zügen, als Bänder von etwa ± 1 bis 2 Prozentpunkten zu lesen; bei 8 Gruppen und 6 Gleisen dagegen noch bei 40 Wagen, B12). Alles gilt in diesem Modell (k Warteschlangen, Abziehen
hintereinander, keine Gleislängen), bei den genannten n und k; die Zähleinheit steht je Aussage dabei (Zug, Folge, Wort, Zug mit Gruppen).

## Modell

- **Anlage:** k Gleise sind k Warteschlangen (wer zuerst rollt, steht vorn). **Ein Durchgang:** Jeder Wagen rollt auf ein Gleis seiner Wahl; danach werden die Gleise 1, 2, …, k nacheinander ganz abgezogen und ergeben den Zug
  für den nächsten Durchgang. Keine Gleislängen, keine Zeit, keine Kosten je Wagenbewegung. t Durchgänge sind dieser Vorgang t-mal.
- **Zug und Ziel:** Ein Zug ist die Folge der Abfahrtsränge 1 bis n in Ankunftsreihenfolge. **Sortiert** heißt aufsteigend 1, 2, …, n (kleinster Rang zuerst). **Gruppiert** (nur Experiment 5) heißt: jede Zielgruppe steht
  zusammenhängend, die Reihenfolge der Gruppen ist frei. Die beiden Ziele sind verschieden.
- **Steigende Folge:** maximale Reihe aufeinanderfolgender Ränge v, v+1, …, w, die im Zug in dieser Reihenfolge stehen. **R** ist ihre Zahl, R = 1 + Zahl der v, bei denen v+1 vor v steht.
- **Radix** ist ⌈log_k n⌉ (bei Gruppen ⌈log_k g⌉ mit g, der Zahl der vorhandenen Gruppen, wie in der Ablaufberg-Demo).
- **Beschriftungszahl L** (nur Gleichstände): die kleinste Zahl L von Beschriftungen 0 bis L − 1 der Wagen, so dass Sortieren nach (Beschriftung, Stelle im Zug) die Gruppen nichtfallend ordnet; bei lauter verschiedenen
  Wagen ist L = R.
- **Ankunftsmodell (ausgedacht):** *Alle Folgen gleich wahrscheinlich* oder *Modell V*: Wagen i kommt zur Zeit i an, bleibt eine exponentialverteilte Verweilzeit mit Mittel D (in Ankunftsabständen) und fährt zur Zeit i + Verweilzeit ab; der
  Abfahrtsrang ist die Stelle in der Reihenfolge der Abfahrtszeiten (Gleichstand: kleinerer Index zuerst). **Nur diese Rangfolge geht in die Rechnung ein.** Kleines D heißt fast sortiert, D → ∞ heißt gleichverteilt.
  Andere Verteilungen der Verweilzeit sind nicht gemessen. Die Züge mit Gruppen in Experiment 5 sind kein Modell V: Jeder Wagen gehört unabhängig und gleichverteilt zu einer von m Gruppen.

## Methodik

- **Formel (eigene Rechnung):** Die Mindestzahl Durchgänge ist ⌈log_k R⌉ (0 für R = 1). Beweisskizze im 📐-Expander der App: Ein Durchgang sortiert genau dann, wenn R ≤ k; t Durchgänge sind eine Radix-Sortierung mit frei
  wählbaren Ziffern. Die Formel ist durch Vorwärtssimulation aller Folgen bestätigt (Tabelle unten, Befund B2), **nicht bewiesen**.
- **Plan** (`gdg_model.plan`): Beschriftung = Nummer der steigenden Folge, Durchgang j sortiert nach der j-ten Ziffer zur Basis k (niedrigste zuerst). Ein **unabhängiger Prüfer** (`gdg_model.play`, kennt weder R noch die
  Beschriftung) spielt nur die Gleiswahl ab, in der App und in den Tests.
- **Vorwärtssuche** (Experiment 1, nur n ≤ 7 und höchstens 300 000 Zuweisungen): alle k^n Zuweisungen eines Durchgangs ausführen und zählen, wie viele den Zug sortieren.
- **Exakte Verteilung** (Experimente 2 und 3): Die Zahl der Folgen mit R steigenden Folgen ist die Eulersche Zahl A(n, R − 1), Ganzzahlarithmetik bis n = 500, Mittel von R exakt (n + 1)/2. Aus den Zahlen folgen Verteilung,
  Mittel und Anteil unter Radix für alle n! Folgen, ohne Aufzählung; für n ≤ 8 zählt die App zur Gegenprobe alle Folgen einzeln.
- **Gruppen** (Experiment 5): Beschriftungszahl L als längster gewichteter Pfad (O(n²)); bei freier Reihenfolge das Minimum über alle m! Reihenfolgen der Gruppen (vektorisiert, m ≤ 7 live, m = 8 vorgerechnet).
- **Zufall:** nur ganzzahliger SplitMix64 (`gdg_rng.py`, `exact_log` ohne C-Bibliothek): gleiche Zufalls-Seeds geben auf jeder Plattform dieselben Folgen. Alle Durchgangszahlen sind Ganzzahlen.
- **Vorgerechnet** (`tools/gdg_make_tables.py` → `data/gdg_tables.json`, `--check` rechnet neu und vergleicht, etwa 1,5 Minuten): die Aufzählung aller Folgen bis n = 9 nach der längsten fallenden Teilfolge, die Gruppen-Tabelle
  (3 000 Züge je Zelle, bei 8 Gruppen 60) und die Modell-V-Tabelle (4 000 Folgen je Zelle). In App und README steht „vorgerechnet“ dabei.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen gelten im beschriebenen Modell; die Spalte „Test“ nennt den Anfang des Testnamens in `tests/test_claims.py` (jede Zahl wird dort gerechnet **und** in dieser README gesucht) oder die Datei des Orakels.
Zähleinheit: Folge (alle n! gleich wahrscheinlich), Wort (alle Wörter einer Mehrfachmenge), Zug (Zufallszug mit Gruppen).

| Nr | Befund (Voraussetzung) | Test |
|---|---|---|
| B1 | Handbeispiel, Zug (2, 4, 6, 1, 3, 5) (ein Zug): R = 4 steigende Folgen {1}, {2, 3}, {4, 5}, {6}; mit 2 und mit 3 Gleisen 2 Durchgänge (Radix 3 bzw. 2), mit 4 Gleisen 1 Durchgang; Gleiswahl mit 2 Gleisen: (4, 1, 5 / 2, 6, 3) → (4, 1, 5, 2, 6, 3) → (1, 2, 3, 4, 5, 6); keine der 64 Zuweisungen mit 2 Gleisen und keine der 729 mit 3 Gleisen sortiert in einem Durchgang | `test_b1` |
| B2 | Mindestzahl durch Vorwärtssimulation aller k^n Zuweisungen = ⌈log_k R⌉ für **alle** Folgen in 13 Fällen (k = 2: n = 3 bis 8; k = 3: n = 4 bis 7; k = 4: n = 5 bis 7), 0 Abweichungen. Stufen (Folgen mit 0, 1, 2, … Durchgängen): n = 6, k = 2: 1, 57, 604, 58 (Mittel 1439/720); n = 8, k = 2: 1, 247, 19 912, 20 160; n = 7, k = 3: 1, 1 311, 3 728. Zweite, rückwärts gerechnete Suche stimmt bis n = 6 (k = 2) und n = 5 (k = 3) | `tests/test_oracle_gleise_durchgaenge.py`, `test_b2` |
| B3 | Zahl der Folgen mit R steigenden Folgen = Eulersche Zahl A(n, R − 1) (Aufzählung n = 4 bis 8, n = 9 im langsamen Test); Mittel von R exakt (n + 1)/2 für n = 10, 20, 50, 100, 200 und 500 | `test_b3` |
| B4 | n = 10, k = 2: Radix 4, mittlere Zahl Durchgänge 2,861; 1 Folge braucht 0, 1 013 brauchen 1, 503 032 brauchen 2, 3 123 740 brauchen 3 und 1 014 brauchen 4 Durchgänge (0,03 % der 3 628 800 Folgen); mehr als 99,95 % der Folgen brauchen weniger als Radix | `test_b4` |
| B5 | Schlimmster Fall = Radix ⌈log_k n⌉ (die Umkehrfolge hat R = n) in allen 1 791 Paaren n = 2 bis 200, k = 2 bis 10 (aus den Verteilungen gezählt) | `test_b5` |
| B6 | Anteil der Folgen mit weniger Durchgängen als Radix, exakt: n = 10, k = 4: 13,89 %; n = 10, k = 6: 86,11 %; n = 20, k = 3: 22,07 %; n = 27, k = 3: 0,12 %; n = 40, k = 4: 1,40 %; n = 64, k = 2: 50 %; n = 10, k = 3: alle bis auf genau 1 Folge | `test_b6` |
| B7 | k = 2: Der Anteil unter Radix ist genau 1/2 bei n = 4, 8, 16, 32, 64, 128 (die Eulerschen Zahlen sind symmetrisch); bei n = 9: 362 879/362 880 (alle außer der Umkehrfolge) | `test_b7` |
| B8 | Sägezahn, n = 20 bis 200 (181 Werte): k = 2: Anteil unter Radix zwischen 0,5 (n = 32) und 1,0 (n = 33), in 0 von 181 Werten unter 0,00005; k = 3: 15, k = 4: 62, k = 6: 121, k = 10: 68 von 181 Werten unter 0,00005. Bei n = 9, 27, 81 und k = 3: 0,0416, 0,0012 und weniger als 0,0001; bei n = 16 und k = 4: 0,0002 | `test_b8` |
| B9 | Ein Durchgang, Folgen aller n!, k = 3: Gleise hintereinander / frei ausgelesen: n = 5: 93 gegen 103; n = 6: 360 gegen 513; n = 9: 15 111 gegen 94 359. k = 2: Gleise 2^n − n (n = 3 bis 9), frei die Catalan-Zahlen (n = 4: 12 gegen 14; n = 9: 503 gegen 4 862). Vorgerechnet; „frei“ wird für n ≤ 6 und k = 2, 3 von einer Maschinensimulation bestätigt | `test_b9`, `tests/test_tables.py` |
| B10 | Modell V (ausgedacht; 4 000 Folgen je Zelle, vorgerechnet, k = 2, Mittel Durchgänge gegen Radix): n = 20 (Radix 5): D = 1: 2,40, D = 16: 3,80, gleichverteilt 3,94 (exakt 3,939); n = 40 (Radix 6): D = 0,5: 2,01, gleichverteilt 4,98 (Stichprobe; exakt 4,986). Mittel von R bei n = 20: 4,46 (D = 1) und 10,53 (gleichverteilt, exakt 10,5); das Mittel von R wird mit D nicht kleiner, in allen drei Zeilen n = 10, 20, 40 der vorgerechneten Tabelle (für n = 10 stehen die Werte nur dort, nicht hier). k = 4: n = 20 braucht ab D = 4 im Mittel 2,00 gegen Radix 3, n = 40 gleichverteilt 2,98 gegen Radix 3 (Stichprobe; exakt 2,986). Alle Werte außer den ausdrücklich exakten sind Stichprobenmittel aus 4 000 Folgen mit Standardfehlern von etwa 0,005 bis 0,02; eine unabhängige Stichprobe mit 20 000 Folgen gab für das Mittel von R bei D = 1 den Wert 4,50 (Standardfehler 0,01) | `test_b10` |
| B11 | Gruppen (Zug mit m = 6 Gruppen, k = 3, vorgerechnet, 3 000 Züge je Zelle, Radix aus den vorhandenen Gruppen): bei freier Reihenfolge unterbietet die exakte Mindestzahl Radix in 93,8 / 98,7 / 35,3 / 0,7 / 0,0 % der Züge mit 8 / 12 / 20 / 30 / 40 Wagen, bei fester Reihenfolge (Sortieren) in 56,5 / 23,4 / 0,7 / 0,0 / 0,0 %. Mit 15 000 Zügen und zwei anderen Zufalls-Seeds sind es bei 8 Wagen 92,9 % und 93,0 % frei, 57,3 % und 57,5 % fest. Alle Zellen mit 3 000 Zügen sind Bänder von etwa ± 1 bis 2 Prozentpunkten: die Stellen hinter dem Komma sind nicht belastbar (eine unabhängige Stichprobe gab bei 20 Wagen frei 37,7 % statt 35,3 %) | `test_b11` |
| B12 | Gruppen, 8 Gruppen und 40 Wagen (60 Züge je Zelle, vorgerechnet): k = 4: gleich Radix in 60 von 60 Zügen; k = 6: exakt 1 gegen Radix 2 in 60 von 60; k = 2: gleich Radix 3 in 60 von 60 | `test_b12` |
| B13 | Gleichstände, feste Zielreihenfolge: ⌈log_k L⌉ gleich der Vorwärtssimulation für alle Wörter in 11 von 11 geprüften Fällen (Mehrfachmenge und k, n ≤ 8); bei freier Reihenfolge das Minimum über die Gruppenreihenfolgen in 8 von 8. (2, 2, 2), k = 2: fest 1, 42, 47 Wörter mit 0, 1, 2 Durchgängen, frei 6 und 84. Zug (2, 1, 2, 1, 3, 3), k = 2: L = 2, 1 Durchgang, Radix 2. Zug (3, 3, 2, 2, 1, 1), k = 2: fest 2 Durchgänge, frei 0 | `tests/test_oracle_gleise_durchgaenge.py`, `test_b13` |
| B14 | L ist gleich R für alle Folgen n ≤ 6; die längste fallende Teilfolge ist höchstens R für alle Folgen n ≤ 7 (Tarjan, nach Quellenbericht: k parallele Warteschlangen sortieren genau die Folgen mit längster fallender Teilfolge höchstens k) | `tests/test_oracle_gleise_durchgaenge.py`, `tests/test_eigenschaften_gleise_durchgaenge.py` |

### Zahl → Test

Exakt (Ganzzahlen, Brüche, Zählung aller Folgen bzw. Wörter): B1 bis B9, B13, B14; die Zahlen der Zufallsproben B10 bis B12 sind ganzzahlige Zähler aus dem SplitMix64 und auf jeder Plattform **gleich** (Zufalls-Seeds der Tabellen: Modell V in B10 gleich 4 600 000 + 1 000 · n + Index von D, gezählt ab 0 in der Reihenfolge D = 0,5; 1; 2; 4; 8; 16; 32; gleichverteilt; Gruppen in B11 und B12 gleich 4 100 000 + 1 000 · m + 100 · k + n mit m Gruppen, k Gleisen und n Wagen; die beiden Wiederholungen mit 15 000 Zügen in B11 nutzen die Zufalls-Seeds 999 und 1 234; die unabhängigen Stichproben mit 20 000 Folgen bzw. Zügen in B10 und B11 sind nicht im Test, ihre Zufalls-Seeds stehen hier nicht), die Tests rechnen die ersten 100 Züge
bzw. Folgen jeder Zelle neu und vergleichen sie exakt (`tests/test_tables.py`); die volle Neuberechnung ist `tools/gdg_make_tables.py --check` und ein langsamer Test (`GDG_SLOW=1`). Anteile als Prozent sind auf die genannten Stellen
gerundet. **Nicht im Test:** die Rechenzeiten (siehe „Ehrliche Grenzen“) und die Aussage „mit 15 000 Zügen 92,9 % und 93,0 %“ (steht als langsamer Test `test_b11_stability`, `GDG_SLOW=1`).

## Befunde und Korrekturen gegenüber dem Plan

Eine frühere Messung (andere Zufallsströme, numpy statt SplitMix64) diente als Erwartung; die Zahlen dieser Demo gelten, wo sie abweichen:

- **„Mit Gleichständen gibt es keine Formel“ war zu eng.** ⌈log_k R⌉ gilt für Wörter nicht, aber ⌈log_k L⌉ gilt in den 11 geprüften Fällen (B13). Kein Beweis, nur Orakel.
- **„Radix ist im Mittel oft einen Durchgang zu hoch“ gilt nur mit n und k** (B4 gegen B6 und B8): bei n = 10 und k = 2 ja, bei n = 27 und k = 3 für 0,12 % der Folgen.
- **Ablaufberg-Demo:** Ihre README nennt für 6 Gruppen und 3 Gleise 95 / 100 / 30 / 0 / 0 % (exakt unter Radix, 20 Züge je Zelle, 8 / 12 / 20 / 30 / 40 Wagen). Mit freier Reihenfolge und Radix aus den vorhandenen Gruppen
  misst diese Demo 93,8 / 98,7 / 35,3 / 0,7 / 0,0 % (B11, 3 000 Züge); die Zahlen sind **vereinbar** (mit 20 Zügen je Zelle ist der Unterschied Stichprobenrauschen), nicht „bestätigt“ (anderer Zufallsstrom, Zufalls-Seeds nicht
  nachgespielt). Mit Radix aus allen 6 Gruppen statt aus den vorhandenen sind es bei 8 Wagen 100,0 % (3 000 von 3 000 Zügen) und bei 12 Wagen 99,1 %: Ein Teil des Vorsprungs bei kleinen Zügen kommt von Zügen, in denen weniger als 6 Gruppen vorkommen. Der Kern, ein Vorsprung bei kleinen Zügen und praktisch keiner mehr ab 30 Wagen (6 Gruppen, 3 Gleise: 0,7 % bei 30, 0,0 % bei 40 Wagen), stimmt für diesen Fall; bei 8 Gruppen und 6 Gleisen bleibt der Vorsprung bei 40 Wagen (B12).
- **Zahlen der früheren Messung verschieben sich durch den anderen Zufallsstrom:** Gruppen bei 8 Wagen 93,8 % statt 92,3 % (3 000 Züge); die Wiederholung mit 15 000 Zügen und zwei weiteren Zufalls-Seeds gibt 92,9 % und 93,0 %, die
  Zahl der Tabelle liegt also etwa zwei Standardfehler über dem Mittel mehrerer Läufe: **als Band „etwa 93 % ± 1 Prozentpunkt“ lesen**. Modell V bei n = 40, k = 2, D = 0,5: 2,01 statt 1,97.
- **Der Verbindungsfaden „sofort gegen verzögert“ gilt für Warteschlangen nicht:** Das Aufschieben der Ausgabe ändert bei parallelen Warteschlangen nichts (alle Folgen n ≤ 6, k = 2, 3, Maschinensimulation); der Unterschied ist
  **Abziehen hintereinander gegen freies Auslesen** (B9).
- **Zahl der Folgen im Modell V:** Die App rechnet 100 bis 1 000 Folgen live (nicht bis 5 000): Jede Verweilzeit kostet einen Logarithmus ohne C-Bibliothek (rund 36 Mikrosekunden); die 4 000 Folgen je Zelle der README stehen vorgerechnet.
- **Gruppen live bis m = 7** (5 040 Reihenfolgen, höchstens 150 Züge bei 7 Gruppen, sonst bis 300); m = 8 nur vorgerechnet (60 Züge). Die README-Fälle der Ablaufberg-Demo mit 12 und 16 Gruppen und ungleich große Gruppen sind **nicht gerechnet**.
- **Gleise als Stapel (LIFO)** gehören nicht in diese Demo (Warteschlangen); der Verweis auf Patience und Stapel steht bei den Nachbarn.

## Ehrliche Grenzen

- **Formel nur bis n = 8 aufgezählt** (13 Fälle: k = 2 bis n = 8, k = 3 bis n = 7, k = 4 bis n = 7); darüber gilt die Beweisskizze im Expander, kein vollständiger Beweis. Für ⌈log_k L⌉ gibt es **keinen** Beweis, nur die 11 + 8 Fälle.
- **Keine gelesene Quelle** bestätigt die Radix-Gleichheit ⌈log_k n⌉ oder die Formel ⌈log_k R⌉; sie sind hier nachgerechnet. Der Bezug von R zu den Riffle-Mischungen (Bayer und Diaconis) ist **nicht gelesen** und wird nicht behauptet.
- **Modell V ist ausgedacht** (exponentialverteilte Verweilzeit); keine echte Ankunftsfolge. Je Zelle 4 000 Folgen; andere Verteilungen nicht gemessen. Die Zahlen aus Zufallsproben sind Bänder, nicht Konstanten (siehe B11).
- **Große n:** Die Verteilung ist exakt bis n = 500 (Ganzzahlen); über das Verhalten für n → ∞ macht die Demo keine Aussage.
- **Gleislängen, mehrere Züge, Wagenbewegungen und Bergzeit** sind nicht modelliert (Ablaufberg-Demo). **Gruppen:** nur gleichverteilte Gruppenzugehörigkeit.
- **Rechenzeit** (einmal gemessen unter Windows, Python 3.14, nicht im Test): Experiment 4 mit 1 000 Folgen und n = 60 etwa 2,3 s (Standard 0,4 s), Experiment 5 mit 7 Gruppen, 40 Wagen und 150 Zügen etwa 1,9 s (6 Gruppen, 300 Züge 0,4 s),
  Verteilung für n = 500 und der Sägezahn unter 0,1 s. Die App meldet Spinner mit Zeitangabe.
- **Plattform:** Zahlen unter Windows entwickelt; der Linux-Lauf (Docker) steht unter „Verifikation“.

### Wo die Annahmen enden

(Derselbe Text steht in der App; ein Test vergleicht beide Fassungen.)

| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Modell:** k Gleise sind Warteschlangen, danach werden die Gleise hintereinander abgezogen; keine Gleislängen, keine Zeit, keine Kosten je Wagenbewegung | Mit Gleislängen, Bergzeit und Wagenbewegungen ändert sich die Frage: Dann zählt auch, wie viele Wagen jeder Durchgang bewegt, und der Aufwand je Durchgang kann die Wahl umdrehen. Gleise als Stapel (LIFO) sind ein anderes Modell. | [ablaufberg-demo](https://github.com/sebastian-hanisch/ablaufberg-demo) (Gruppieren, Wagenbewegungen, Bergzeit, exakte Lösung) |
| **Alle Wagen verschieden, feste Zielreihenfolge** (Experimente 1 bis 4) | Bei Wagen mit gleicher Zielgruppe gilt ⌈log_k R⌉ nicht mehr; in den geprüften Fällen gilt ⌈log_k L⌉ mit der Beschriftungszahl L (Experiment 5). Und wenn die Gruppen nur zusammenhängend stehen müssen, schlägt die exakte Lösung Radix bei kleinen Zügen oft (6 Gruppen, 3 Gleise: 93,8 % der Züge mit 8 Wagen), bei 30 Wagen 0,7 % und bei 40 Wagen 0,0 %; nicht überall: bei 8 Gruppen, 6 Gleisen und 40 Wagen in 60 von 60 Zügen noch. | Experiment 5 |
| **Ausgedachtes Ankunftsmodell** (Modell V) und gleichverteilte Folgen | Keine reale Ankunftsfolge; die Zahlen für Modell V gelten nur für dieses Modell mit seiner exponentialverteilten Verweilzeit. Andere Verteilungen sind nicht gemessen. | – |
| **Die Formel ⌈log_k R⌉** | Durch Aufzählung aller Folgen bestätigt bis n = 8 (k = 2) und n = 7 (k = 3 und 4), mit einer Beweisskizze im 📐-Expander, aber ohne vollständigen Beweis in dieser Demo; für größere n ist sie nicht aufgezählt. | – |

## Quellen

Gelesen (nach den Quellenberichten der Vorarbeit, Stufen: Wortlaut gelesen oder nur Abstract): Jacob, Márton, Maue, Nunkesser, *Multistage Methods for Freight Train Classification*, ATMOS 2007 (Fassung von 2007 im Wortlaut: mehrstufiges
Sortieren am Ablaufberg, bei **begrenzter** Gleiskapazität NP-schwer; die erweiterte Fassung in Networks 57(1), 2011 **nicht gelesen**). Tarjan, *The Switchyard Problem: Sorting Using Networks of Queues and Stacks*, Stanford CS-TR-71-213,
1971 (Vorfassung des Aufsatzes im J. ACM 1972; Lemma 2: k parallele Warteschlangen sortieren genau die Folgen mit längster fallender Teilfolge höchstens k; **der Aufsatz selbst ist nicht gelesen**). Die Tabelle „frei ausgelesen“ (B9)
stimmt mit der Folge der OEIS-Zahlen für drei parallele Warteschlangen (A005802: 6, 23, 103, 513, 2 761, 15 767, 94 359) und mit den Catalan-Zahlen überein (nach dem Quellenbericht, hier nachgerechnet).
Train Marshalling (Gruppieren gleicher Ziele mit Mindestzahl Gleisen, NP-vollständig; Dahlhaus u. a. 2000) ist ein **anderes** Problem und nur ein Verweis. Die Originale von Knuth, Greene, Bayer und Diaconis sind nicht gelesen.

## Verifikation

- **Kern:** Mindestzahl gegen Handrechnung (Handbeispiel B1) und gegen die Vorwärtssimulation aller Zuweisungen sowie eine Rückwärts-Breitensuche (`tests/test_oracle_gleise_durchgaenge.py`); der Plan wird von einem unabhängigen Prüfer
  abgespielt (alle Folgen n ≤ 7, k = 2 bis 4); Verteilung, Mittel und Tabellen gegen die Aufzählung aller Folgen (n ≤ 8, n = 9 im langsamen Test); Gleichstände gegen die Vorwärtssimulation aller Wörter (feste und freie Reihenfolge).
- **Eigenschaften** (`tests/test_eigenschaften_gleise_durchgaenge.py`): R = 1 + Abstiege der Inversen, Spiegeln und Komplementieren ändert R nicht, nie mehr als Radix, mehr Gleise nie mehr Durchgänge, nach dem ersten Durchgang des Plans höchstens t − 1 weitere,
  längste fallende Teilfolge höchstens R, frei höchstens fest, Umbenennen der Gruppen ändert bei freier Reihenfolge nichts (je 40 bis 200 Zufallsinstanzen mit festem Zufalls-Seed; „nie mehr als Radix“ zusätzlich über alle Folgen bis n = 8).
- **Verdikte und Presets:** jedes Verdikt eine reine Funktion (`tests/test_verdicts.py`), je Preset die erwartete Verdikt-Zeile (`tests/test_presets.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an seinen Grenzen, jeder Auswahlwert, ungültige Eingaben), Layout (Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers
  hebt die Markierung auf), Footer, Laufzeit-Importe, Eigenständigkeit (kein Import aus anderen Demos).
- **Testzahl:** 294 Tests (`pytest --collect-only -q tests`).
- **Linux-Lauf (Docker, Python 3.12, frische Installation der ungepinnten Pakete):** grün (290 bestanden, 3 langsame übersprungen; die drei laufen mit `GDG_SLOW=1` unter Windows und sind dort grün), einschließlich der exakt verglichenen Zufallszähler.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Kopf, Kernfragen, fünf Experimente, Grenzen, Formelblock |
| `gdg_model.py` | Kern: Zug, Durchgang, steigende Folgen, Plan, unabhängiger Prüfer, Vorwärtssuche |
| `gdg_exact.py` | Eulersche Zahlen, exakte Verteilung, Sägezahn, Aufzählung bis n = 9 |
| `gdg_words.py` | Gleichstände: Beschriftungszahl L, feste und freie Gruppenreihenfolge |
| `gdg_arrival.py` | Zufallszug, Modell V (ausgedacht), Zufallswörter |
| `gdg_tables.py` | vorgerechnete Tabellen: Laden, Neuberechnung, Auswertung |
| `gdg_evaluation.py` | Analysen und Verdikte der Experimente als reine Funktionen |
| `gdg_constants.py`, `gdg_presets.py`, `gdg_layout.py`, `gdg_visualization.py`, `gdg_texts.py` | Regler-Grenzen und Presets, Permalink, fester Kopf, Plotly-Abbildungen, gemeinsamer Text |
| `gdg_rng.py` | SplitMix64 (Vorlage des Portfolios, `exact_log` und `exact_cos` ohne C-Bibliothek) |
| `data/gdg_tables.json` | vorgerechnete Messreihen |
| `tools/gdg_make_tables.py` | rechnet die Tabellen neu (`--check` vergleicht) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Orakel, Eigenschaften, Claims, Verdikte, Presets, Layout, Smoke, Footer, Laufzeit-Importe, Eigenständigkeit |

## Bewusst nicht umgesetzt

- **Gleislängen, Bergzeit, Wagenbewegungen, exakter Löser (CP-SAT), PDF-Rangierplan, ungleich große Gruppen:** gehören zur Ablaufberg-Demo.
- **Gleise als Stapel (LIFO), mehrere Züge, andere Verweilzeit-Verteilungen:** nicht gerechnet.
- **Mehr als 7 Gruppen live:** 8! = 40 320 Reihenfolgen je Zug sind live zu teuer; vorgerechnet nur eine kleine Tabelle.
- **Beweis der Formel ⌈log_k R⌉ und ⌈log_k L⌉:** nur Skizze und Orakel.
- **Eine Aussage über das Verhalten für n → ∞** und über echte Ankunftsfolgen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
GDG_SLOW=1 pytest tests/ -v       # dazu die langsamen Läufe (n = 9, volle Neuberechnung der Tabellen, Stabilität der Gruppen-Anteile)
```

Gebaut mit Streamlit, Plotly, pandas und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
