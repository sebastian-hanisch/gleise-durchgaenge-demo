"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets.

Ein Zug ist eine Folge der Abfahrtsränge 1..n in Ankunftsreihenfolge. Alle Zahlen der App sind Ganzzahlen oder Anteile aus Ganzzahlen;
der Zufall kommt nur aus dem SplitMix64 in `gdg_rng.py`."""

from gdg_arrival import random_train

SEED_MAX = 999999

# --- Experiment 1: ein Zug von Hand
E1_N_MIN, E1_N_MAX, E1_DEFAULT_N = 4, 12, 8
E1_K_MIN, E1_K_MAX, E1_DEFAULT_K = 2, 6, 2
E1_DEFAULT_SEED = 17
E1_DEFAULT_TEXT = "2, 4, 6, 1, 3, 5"
E1_TEXT_MAX_LEN = 80
FORWARD_N_MAX = 7                  # Vorwärtssuche über alle Zuweisungen nur bis n = 7 ...
FORWARD_ASSIGN_MAX = 300_000       # ... und höchstens so vielen Zuweisungen k^n

# --- Experiment 2: Verteilung der Durchgänge
E2_N_MIN, E2_N_MAX, E2_DEFAULT_N = 4, 500, 12
E2_K_MIN, E2_K_MAX, E2_DEFAULT_K = 2, 10, 3
ENUM_N_MAX = 8                     # Aufzählung aller n! Folgen als Gegenprobe bis n = 8 (40 320 Folgen)
TABLE_N = tuple(range(3, 10))      # eingefrorene Tabelle: Gleise hintereinander gegen frei auslesen
TABLE_K = (2, 3, 4, 5)

# --- Experiment 3: Sägezahn
E3_K_OPTIONS = (2, 3, 4, 6, 10)
E3_DEFAULT_K = 3
E3_N_FROM, E3_N_TO = 20, 200
E3_ZERO_EPS = 5e-5                 # Anteil unter dieser Grenze zählt als 0

# --- Experiment 4: Modell V
E4_D_OPTIONS = ("0.5", "1", "2", "4", "8", "16", "32", "gleichverteilt")
E4_DEFAULT_D = "4"
E4_N_MIN, E4_N_MAX, E4_DEFAULT_N = 10, 60, 20
E4_K_MIN, E4_K_MAX, E4_DEFAULT_K = 2, 6, 2
E4_TRIALS_MIN, E4_TRIALS_MAX, E4_DEFAULT_TRIALS = 100, 1000, 500   # 1000 Folgen mit n = 60: etwa 2 s (expovariate ohne C-Bibliothek)
E4_DEFAULT_SEED = 23

# --- Experiment 5: Gruppen
E5_M_MIN, E5_M_MAX, E5_DEFAULT_M = 2, 7, 4
E5_N_MIN, E5_N_MAX, E5_DEFAULT_N = 6, 40, 12
E5_K_MIN, E5_K_MAX, E5_DEFAULT_K = 2, 6, 2
E5_ORDER_FIXED, E5_ORDER_FREE = "fest", "frei"
E5_DEFAULT_ORDER = E5_ORDER_FREE
E5_TRIALS_MIN, E5_TRIALS_MAX, E5_DEFAULT_TRIALS = 20, 300, 100
E5_DEFAULT_SEED = 29
# Obergrenze der Züge je Gruppenzahl m (m! Reihenfolgen je Zug; gemessen: m = 6 etwa 1 ms, m = 7 etwa 10 ms je Zug mit 40 Wagen)
E5_TRIAL_CAP = {2: 300, 3: 300, 4: 300, 5: 300, 6: 300, 7: 150}

# --- eingefrorene Messreihen (tools/gdg_make_tables.py)
TABLES_FILE = "data/gdg_tables.json"
TABLE_SEED_BASE = 4_100_000
GROUP_TRIALS = 3000                 # Züge je Zelle der vorgerechneten Gruppen-Tabelle
GROUP_PREFIX_TRIALS = 100           # die ersten Züge, die die Tests schnell neu rechnen
MODEL_V_TRIALS = 4000               # Folgen je Zelle der vorgerechneten Modell-V-Tabelle

COLORS = ("#2F6B65", "#c0504d", "#4c78a8", "#d98e04", "#7a5195", "#5b8c3a", "#b0457a", "#8c6d31", "#3a8fb7", "#9a6324", "#6b6ecf", "#cc4c2a")
COLOR_BAR = "#4c78a8"
COLOR_RADIX = "#c0504d"
COLOR_MEAN = "#2F6B65"
COLOR_OTHER = "rgba(150,150,150,0.55)"

ZUFALLSZUG_10 = ", ".join(str(v) for v in random_train(10, E1_DEFAULT_SEED))   # der Zug, den „Zufallszug ziehen“ mit n = 10 und dem Standard-Zufalls-Seed liefert

PRESETS = {
    "Handbeispiel (2, 4, 6, 1, 3, 5), 2 Gleise": {"text": E1_DEFAULT_TEXT, "k1": 2},
    "Umkehrfolge n = 8: Radix ist scharf": {"text": "8, 7, 6, 5, 4, 3, 2, 1", "k1": 2, "n1": 8},
    "Zufallszug n = 10, 2 Gleise": {"text": ZUFALLSZUG_10, "n1": 10, "k1": 2, "seed1": E1_DEFAULT_SEED, "n2": 10, "k2": 2},
    "Radix zu hoch: n = 10, 2 Gleise": {"n2": 10, "k2": 2},
    "Radix passt: n = 27, 3 Gleise": {"n2": 27, "k2": 3, "k3": 3},
    "Fast sortiert (D = 1)": {"d4": "1", "n4": 20, "k4": 2},
    "Gleichverteilt (D = ∞)": {"d4": "gleichverteilt", "n4": 20, "k4": 2},
    "Gruppen: 6 Gruppen, 3 Gleise, 8 Wagen": {"m5": 6, "n5": 8, "k5": 3, "order5": E5_ORDER_FREE},
    "Gruppen: 40 Wagen": {"m5": 6, "n5": 40, "k5": 3, "order5": E5_ORDER_FREE},
    "Sortieren ≠ Gruppieren": {"m5": 3, "n5": 6, "k5": 2, "order5": E5_ORDER_FIXED, "text5": "3, 3, 2, 2, 1, 1"},
}
STANDARD_PRESET = "Handbeispiel (2, 4, 6, 1, 3, 5), 2 Gleise"
PRESET_HELP = {
    "Handbeispiel (2, 4, 6, 1, 3, 5), 2 Gleise": "Der Zug (2, 4, 6, 1, 3, 5) hat 4 steigende Folgen: mit 2 Gleisen genügen 2 Durchgänge, Radix würde 3 nennen. Experiment 1.",
    "Umkehrfolge n = 8: Radix ist scharf": "Der umgekehrte Zug (8, 7, …, 1) ist der schlimmste Fall: Er braucht genau so viele Durchgänge, wie Radix nennt. Experiment 1.",
    "Zufallszug n = 10, 2 Gleise": "Ein Zufallszug mit 10 Wagen aus dem Zufalls-Seed (Feld leer, dann zieht die App ihn); Experiment 2 steht auf n = 10. Experimente 1 und 2.",
    "Radix zu hoch: n = 10, 2 Gleise": "Bei n = 10 und 2 Gleisen sagt Radix 4 Durchgänge; mehr als 99,95 % der Folgen brauchen weniger. Experiment 2.",
    "Radix passt: n = 27, 3 Gleise": "Bei n = 27 und 3 Gleisen sagt Radix 3 Durchgänge; nur 0,12 % der Folgen brauchen weniger. Experimente 2 und 3.",
    "Fast sortiert (D = 1)": "Modell V mit kurzer Verweilzeit D = 1: Der Zug kommt fast sortiert an; Mittel und Vergleich mit Radix stehen im Verdikt. Experiment 4.",
    "Gleichverteilt (D = ∞)": "Modell V ohne Ordnung der Ankunft (alle Folgen gleich wahrscheinlich); das Verdikt nennt daneben das exakte Mittel. Experiment 4.",
    "Gruppen: 6 Gruppen, 3 Gleise, 8 Wagen": "Gruppieren statt Sortieren: Der Anteil der Züge, in denen die exakte Mindestzahl Radix unterbietet, steht im Verdikt. Experiment 5.",
    "Gruppen: 40 Wagen": "Derselbe Fall (6 Gruppen, 3 Gleise) mit 40 Wagen: Der Anteil der Züge mit Vorsprung gegenüber Radix steht im Verdikt. Experiment 5.",
    "Sortieren ≠ Gruppieren": "Der Zug (3, 3, 2, 2, 1, 1) ist schon gruppiert, aber bei fester Reihenfolge der Gruppen nicht sortiert. Experimente 1 und 5.",
}
