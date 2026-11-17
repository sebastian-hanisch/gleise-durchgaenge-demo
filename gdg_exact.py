"""Exakte Verteilung der Mindestzahl Durchgänge über alle n! Folgen: aus den Eulerschen Zahlen, ohne Aufzählung (Ganzzahlen, n bis 500).

Zahl der Folgen mit R steigenden Folgen = Eulersche Zahl A(n, R − 1) (Zahl der Folgen mit R − 1 Abstiegen; aus der Rekursion
A(m, d) = (d + 1)·A(m − 1, d) + (m − d)·A(m − 1, d − 1) neu gerechnet und bis n = 9 gegen die Aufzählung geprüft, tests/test_oracle_gleise.py).
Die Mindestzahl Durchgänge ist ⌈log_k R⌉, das Mittel von R ist exakt (n + 1)/2. Anteile sind Brüche aus Ganzzahlen (`fractions`)."""

import itertools
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import numpy as np

import gdg_constants as C
from gdg_model import ceil_log, radix


def _next_row(row: list[int], m: int) -> list[int]:
    """Zeile m der Eulerschen Zahlen aus Zeile m − 1."""
    new = [0] * m
    for d in range(m):
        a = row[d] * (d + 1) if d < len(row) else 0
        b = row[d - 1] * (m - d) if d >= 1 else 0
        new[d] = a + b
    return new


@lru_cache(maxsize=64)
def eulerian_row(n: int) -> tuple[int, ...]:
    """A(n, 0), …, A(n, n − 1): Zahl der Folgen von 1..n mit d Abstiegen, also mit R = d + 1 steigenden Folgen. n >= 1."""
    if n < 1:
        raise ValueError("n muss mindestens 1 sein")
    row = [1]
    for m in range(2, n + 1):
        row = _next_row(row, m)
    return tuple(row)


@dataclass(frozen=True)
class Summary:
    n: int
    k: int
    total: int                      # n!
    counts: dict                    # Zahl der Durchgänge t -> Zahl der Folgen, die genau t brauchen
    radix: int
    at_radix: int                   # Folgen, die genau Radix Durchgänge brauchen
    mean: Fraction                  # mittlere Zahl Durchgänge
    share_below: Fraction           # Anteil der Folgen mit weniger Durchgängen als Radix


def _summary_from_row(row, n: int, k: int) -> Summary:
    total = sum(row)
    prefix = list(itertools.accumulate(row))     # prefix[c - 1] = Folgen mit R <= c
    counts = {0: row[0]}
    t, cap_prev = 1, 1
    while cap_prev < n:
        cap = min(k**t, n)
        counts[t] = prefix[cap - 1] - prefix[cap_prev - 1]
        cap_prev, t = cap, t + 1
    rad = radix(n, k)
    at_radix = counts.get(rad, 0)
    mean = Fraction(sum(t * c for t, c in counts.items()), total)
    return Summary(n, k, total, counts, rad, at_radix, mean, Fraction(total - at_radix, total))


@lru_cache(maxsize=256)
def summary(n: int, k: int) -> Summary:
    """Verteilung der Mindestzahl Durchgänge für n Wagen und k Gleise (alle n! Folgen gleich wahrscheinlich). n >= 2, k >= 2."""
    if n < 2 or k < 2:
        raise ValueError("n und k müssen mindestens 2 sein")
    return _summary_from_row(eulerian_row(n), n, k)


@lru_cache(maxsize=8)
def sawtooth(ks: tuple = C.E3_K_OPTIONS, n_max: int = C.E3_N_TO) -> dict:
    """Für n = 2..n_max und jedes k: (Anteil unter Radix, mittlere Zahl Durchgänge) als Gleitkommazahlen, aus den Eulerschen Zahlen, einmal gerechnet."""
    result = {k: {} for k in ks}
    row = [1]
    for n in range(2, n_max + 1):
        row = _next_row(row, n)
        for k in ks:
            s = _summary_from_row(row, n, k)
            result[k][n] = (float(s.share_below), float(s.mean))
    return result


def sawtooth_stats(ks=C.E3_K_OPTIONS, n_from=C.E3_N_FROM, n_to=C.E3_N_TO) -> dict:
    """Kennzahlen des Sägezahns je k im Bereich n_from..n_to: kleinster und größter Anteil unter Radix (mit n), Zahl der n mit Anteil < E3_ZERO_EPS."""
    data = sawtooth(tuple(C.E3_K_OPTIONS), C.E3_N_TO)
    out = {}
    for k in ks:
        vals = [(n, data[k][n][0]) for n in range(n_from, n_to + 1)]
        lo = min(vals, key=lambda x: (x[1], x[0]))
        hi = max(vals, key=lambda x: x[1])                    # bei Gleichstand das kleinste n (max liefert das erste)
        zeros = [n for n, v in vals if v < C.E3_ZERO_EPS]
        out[k] = {"min": lo[1], "min_n": lo[0], "max": hi[1], "max_n": hi[0], "zeros": zeros, "count": len(vals)}
    return out


# ---------------------------------------------------------------- Aufzählung (Gegenprobe bis n = 8, eingefrorene Tabelle bis n = 9)

def all_trains(n: int) -> np.ndarray:
    """Alle n! Folgen als Zeilen (n <= 9)."""
    return np.array(list(itertools.permutations(range(1, n + 1))), dtype=np.int16)


def rising_counts_of(trains: np.ndarray) -> np.ndarray:
    """R für jede Zeile: 1 + Zahl der v, bei denen v + 1 vor v steht."""
    pos = np.argsort(trains, axis=1)
    return 1 + (pos[:, 1:] < pos[:, :-1]).sum(axis=1)


def enumerate_rising_histogram(n: int) -> list[int]:
    """Aufzählung aller n! Folgen: Zahl der Folgen mit R = 1, 2, …, n steigenden Folgen."""
    r = rising_counts_of(all_trains(n))
    return [int((r == v).sum()) for v in range(1, n + 1)]


def lds_histogram(n: int) -> list[int]:
    """Aufzählung aller n! Folgen: Zahl der Folgen mit längster fallender Teilfolge 1, 2, …, n (vektorisierte Dynamik über alle Zeilen)."""
    trains = all_trains(n).astype(np.int16)
    best = np.ones(trains.shape, dtype=np.int16)
    for i in range(n):
        for j in range(i):
            bigger = trains[:, j] > trains[:, i]
            best[:, i] = np.where(bigger, np.maximum(best[:, i], best[:, j] + 1), best[:, i])
    lds = best.max(axis=1)
    return [int((lds == v).sum()) for v in range(1, n + 1)]


def mean_passes_from_histogram(hist: list[int], k: int) -> Fraction:
    """Mittlere Mindestzahl Durchgänge aus einer Aufzählung (hist[R − 1] = Zahl der Folgen mit R)."""
    total = sum(hist)
    return Fraction(sum(c * (0 if r == 1 else ceil_log(r, k)) for r, c in enumerate(hist, start=1)), total)
