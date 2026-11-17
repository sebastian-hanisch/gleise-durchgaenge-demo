"""Texte, die App und README gemeinsam führen (ein Test vergleicht beide Fassungen)."""

ASSUMPTIONS_MARKDOWN = """| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Modell:** k Gleise sind Warteschlangen, danach werden die Gleise hintereinander abgezogen; keine Gleislängen, keine Zeit, keine Kosten je Wagenbewegung | Mit Gleislängen, Bergzeit und Wagenbewegungen ändert sich die Frage: Dann zählt auch, wie viele Wagen jeder Durchgang bewegt, und der Aufwand je Durchgang kann die Wahl umdrehen. Gleise als Stapel (LIFO) sind ein anderes Modell. | [ablaufberg-demo](https://github.com/sebastian-hanisch/ablaufberg-demo) (Gruppieren, Wagenbewegungen, Bergzeit, exakte Lösung) |
| **Alle Wagen verschieden, feste Zielreihenfolge** (Experimente 1 bis 4) | Bei Wagen mit gleicher Zielgruppe gilt ⌈log_k R⌉ nicht mehr; in den geprüften Fällen gilt ⌈log_k L⌉ mit der Beschriftungszahl L (Experiment 5). Und wenn die Gruppen nur zusammenhängend stehen müssen, schlägt die exakte Lösung Radix bei kleinen Zügen oft (6 Gruppen, 3 Gleise: 93,8 % der Züge mit 8 Wagen), bei 30 Wagen 0,7 % und bei 40 Wagen 0,0 %; nicht überall: bei 8 Gruppen, 6 Gleisen und 40 Wagen in 60 von 60 Zügen noch. | Experiment 5 |
| **Ausgedachtes Ankunftsmodell** (Modell V) und gleichverteilte Folgen | Keine reale Ankunftsfolge; die Zahlen für Modell V gelten nur für dieses Modell mit seiner exponentialverteilten Verweilzeit. Andere Verteilungen sind nicht gemessen. | – |
| **Die Formel ⌈log_k R⌉** | Durch Aufzählung aller Folgen bestätigt bis n = 8 (k = 2) und n = 7 (k = 3 und 4), mit einer Beweisskizze im 📐-Expander, aber ohne vollständigen Beweis in dieser Demo; für größere n ist sie nicht aufgezählt. | – |
"""

LIMITS_NOTE = ("Die Grenzen der Messreihen: Gruppen nur bis 7 Gruppen live (m! Reihenfolgen), die vorgerechnete Tabelle bis 8; ungleich große Gruppen und die Fälle mit 12 und 16 Gruppen "
               "aus der Ablaufberg-Demo sind nicht gerechnet.")
