"""Vorgerechnete Messreihen (Skript `tools/gdg_make_tables.py`, Datei `data/gdg_tables.json`, Prüfung mit `--check`).

Drei Tabellen, alle aus ganzen Zahlen (Zähler) und dem SplitMix64 der Demo, also auf jeder Plattform dieselben Zahlen:

* `parallel`: je n = 3 … 9 die Aufzählung aller n! Folgen nach der längsten fallenden Teilfolge (LDS); daraus „frei auslesen“ (k parallele Warteschlangen,
  genau die Folgen mit LDS <= k, Tarjan Lemma 2, nach Quellenbericht) gegen „Gleise hintereinander“ (R <= k, aus den Eulerschen Zahlen).
* `gruppen`: Züge mit Zielgruppen, Zähler je Zelle (m Gruppen, k Gleise, n Wagen, Zahl der Züge, Zufalls-Seed der Zelle).
* `modell_v`: Histogramm von R je Zelle (n, D) aus Modell V (ausgedacht) mit 4000 Folgen; daraus folgen die Durchgänge für jedes k.
"""

import json
from pathlib import Path

import gdg_arrival as AR
import gdg_constants as C
import gdg_exact as EX
import gdg_model as M
import gdg_words as W
from gdg_rng import SplitMix64

DATA_PATH = Path(__file__).resolve().parent / C.TABLES_FILE

GROUP_CELLS = (  # (Gruppen m, Gleise k, Wagen n, Zahl der Züge)
    (6, 3, 8, C.GROUP_TRIALS), (6, 3, 12, C.GROUP_TRIALS), (6, 3, 20, C.GROUP_TRIALS), (6, 3, 30, C.GROUP_TRIALS), (6, 3, 40, C.GROUP_TRIALS),
    (6, 2, 12, C.GROUP_TRIALS), (6, 4, 12, C.GROUP_TRIALS), (4, 2, 8, C.GROUP_TRIALS), (4, 2, 20, C.GROUP_TRIALS),
    (8, 4, 40, 60), (8, 6, 40, 60), (8, 2, 40, 60),
)
MODEL_V_N = (10, 20, 40)
MODEL_V_D = ("0.5", "1", "4", "16", "gleichverteilt")


def group_seed(m: int, k: int, n: int) -> int:
    return C.TABLE_SEED_BASE + 1000 * m + 100 * k + n


def model_v_seed(n: int, d: str) -> int:
    return C.TABLE_SEED_BASE + 500_000 + 1000 * n + C.E4_D_OPTIONS.index(d)


def dwell_of(d: str) -> float | None:
    return None if d == "gleichverteilt" else float(d)


# ---------------------------------------------------------------- Gruppen

def group_trial(m: int, k: int, n: int, rng: SplitMix64) -> dict:
    """Ein Zug mit Gruppen: Mindestzahl bei fester und bei freier Reihenfolge sowie die beiden Radix-Zahlen."""
    word = AR.random_word(n, m, rng)
    fixed_passes = W.passes_fixed(word, k)
    free_passes, _, _ = W.passes_free(word, m, k)
    return {"fixed": fixed_passes, "free": free_passes, "radix_present": W.radix_present(word, k), "radix_all": W.radix_all(m, k)}


def group_counts(m: int, k: int, n: int, trials: int, seed: int) -> dict:
    """Zähler über die ersten `trials` Züge des Stroms mit dem Zufalls-Seed `seed`."""
    rng = SplitMix64(seed)
    c = {"free_lt_present": 0, "fixed_lt_present": 0, "free_lt_all": 0, "sum_free": 0, "sum_fixed": 0, "sum_radix_present": 0}
    for _ in range(trials):
        t = group_trial(m, k, n, rng)
        c["free_lt_present"] += t["free"] < t["radix_present"]
        c["fixed_lt_present"] += t["fixed"] < t["radix_present"]
        c["free_lt_all"] += t["free"] < t["radix_all"]
        c["sum_free"] += t["free"]
        c["sum_fixed"] += t["fixed"]
        c["sum_radix_present"] += t["radix_present"]
    return c


def make_group_cells() -> list[dict]:
    cells = []
    for m, k, n, trials in GROUP_CELLS:
        seed = group_seed(m, k, n)
        prefix_trials = C.GROUP_PREFIX_TRIALS if m <= 6 else 0
        cell = {"m": m, "k": k, "n": n, "trials": trials, "seed": seed, "counts": group_counts(m, k, n, trials, seed), "prefix_trials": prefix_trials}
        cell["prefix_counts"] = group_counts(m, k, n, prefix_trials, seed) if prefix_trials else None
        cells.append(cell)
    return cells


# ---------------------------------------------------------------- Modell V

def r_histogram(trains, n: int) -> list[int]:
    hist = [0] * n
    for p in trains:
        hist[M.rising_count(p) - 1] += 1
    return hist


def make_model_v_cells() -> list[dict]:
    cells = []
    for n in MODEL_V_N:
        for d in MODEL_V_D:
            seed = model_v_seed(n, d)
            trains = AR.model_v_trains(n, dwell_of(d), C.MODEL_V_TRIALS, seed)
            prefix = trains[: C.GROUP_PREFIX_TRIALS]
            cells.append({"n": n, "d": d, "trials": C.MODEL_V_TRIALS, "seed": seed, "r_hist": r_histogram(trains, n),
                          "prefix_trials": C.GROUP_PREFIX_TRIALS, "prefix_r_hist": r_histogram(prefix, n)})
    return cells


# ---------------------------------------------------------------- parallel

def make_parallel() -> dict:
    return {str(n): {"lds_hist": EX.lds_histogram(n)} for n in C.TABLE_N}


def make_all() -> dict:
    return {"version": 1, "parallel": make_parallel(), "gruppen": make_group_cells(), "modell_v": make_model_v_cells()}


def load() -> dict:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- Auswertung der gespeicherten Zahlen

def passes_from_r_hist(r_hist: list[int], k: int) -> dict:
    """Aus dem Histogramm von R (r_hist[R − 1]) die Durchgänge für k Gleise: Mittel, Anteil mit höchstens einem Durchgang, Zahl der Folgen unter Radix."""
    n = len(r_hist)
    total = sum(r_hist)
    rad = M.radix(n, k)
    passes = [(0 if r == 1 else M.ceil_log(r, k), c) for r, c in enumerate(r_hist, start=1)]
    return {
        "mean": sum(t * c for t, c in passes) / total,
        "one_or_less": sum(c for t, c in passes if t <= 1) / total,
        "below_radix": sum(c for t, c in passes if t < rad) / total,
        "mean_r": sum(r * c for r, c in enumerate(r_hist, start=1)) / total,
        "radix": rad,
        "total": total,
    }


def parallel_row(table: dict, n: int, k: int) -> dict:
    """Zeile der Tabelle „ein Durchgang: Gleise hintereinander gegen frei auslesen“ für n Wagen und k Gleise."""
    lds_hist = table["parallel"][str(n)]["lds_hist"]
    euler = EX.eulerian_row(n)
    return {"n": n, "total": sum(euler), "gleise": sum(euler[:k]), "frei": sum(lds_hist[:k])}
