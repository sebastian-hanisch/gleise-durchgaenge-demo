"""Kern: Zug, Durchgang, steigende Folgen, Plan nach der Radix-Regel und der unabhängige Prüfer.

Anlage: k Gleise sind k Warteschlangen (wer zuerst rollt, steht vorn). **Ein Durchgang:** Jeder Wagen des Zuges rollt auf ein Gleis; danach werden die
Gleise 1, 2, …, k nacheinander ganz abgezogen und ergeben den Zug für den nächsten Durchgang. Keine Gleislängen, keine Zeit.
Ein Zug ist die Folge der Abfahrtsränge 1..n in Ankunftsreihenfolge; **sortiert** heißt: aufsteigend 1, 2, …, n.

Steigende Folge: maximale Reihe aufeinanderfolgender Ränge v, v+1, …, w, die im Zug in dieser Reihenfolge stehen (v+1 hinter v).
R = Zahl der steigenden Folgen = 1 + Zahl der v, bei denen v+1 vor v steht. Die Mindestzahl Durchgänge mit k Gleisen ist ⌈log_k R⌉ (eigene Rechnung,
bis n = 8 durch Aufzählung bestätigt, siehe tests/test_oracle_gleise.py). Radix, die Lehrbuchzahl, ist ⌈log_k n⌉.

Der Plan (Beschriftung = Nummer der steigenden Folge, niedrigste Ziffer zur Basis k zuerst) ist unabhängig vom Prüfer `play`: dieser spielt nur die
Gleiswahl ab."""

import bisect
from dataclasses import dataclass

import numpy as np

import gdg_constants as C


def ceil_log(count: int, k: int) -> int:
    """Kleinstes t mit k**t >= count (count >= 1, k >= 2)."""
    if count < 1:
        raise ValueError("count muss mindestens 1 sein")
    if k < 2:
        raise ValueError("k muss mindestens 2 sein")
    t, capacity = 0, 1
    while capacity < count:
        capacity *= k
        t += 1
    return t


def radix(n: int, k: int) -> int:
    """Die Lehrbuchzahl ⌈log_k n⌉ (Radix-Sortierung nach den Ziffern des Rangs zur Basis k); 0 für n <= 1."""
    return 0 if n <= 1 else ceil_log(n, k)


def is_train(p) -> bool:
    return sorted(p) == list(range(1, len(p) + 1))


def rising_runs(p) -> list[list[int]]:
    """Die steigenden Folgen als Listen von Rängen, nach Rang geordnet. Leerer Zug: keine."""
    n = len(p)
    if n == 0:
        return []
    pos = {v: i for i, v in enumerate(p)}
    runs, cur = [], [1]
    for v in range(2, n + 1):
        if pos[v] > pos[v - 1]:
            cur.append(v)
        else:
            runs.append(cur)
            cur = [v]
    runs.append(cur)
    return runs


def rising_count(p) -> int:
    """R, die Zahl der steigenden Folgen (0 für den leeren Zug)."""
    return len(rising_runs(p))


def run_labels(p) -> tuple[int, ...]:
    """Beschriftung je Wagen (Stelle im Zug): Nummer 0, 1, … der steigenden Folge, zu der sein Rang gehört."""
    label_of_rank = {}
    for label, run in enumerate(rising_runs(p)):
        for v in run:
            label_of_rank[v] = label
    return tuple(label_of_rank[v] for v in p)


def min_passes(p, k: int) -> int | None:
    """Mindestzahl Durchgänge ⌈log_k R⌉ (0, wenn der Zug schon sortiert ist). Mit k = 1 geht nur die Identität; sonst None (unmöglich)."""
    r = rising_count(p)
    if r <= 1:
        return 0
    if k < 2:
        return None
    return ceil_log(r, k)


def one_pass(train, assign, k: int) -> tuple:
    """Ein Durchgang: Wagen i rollt auf Gleis assign[i]; danach werden die Gleise 1..k hintereinander abgezogen."""
    tracks = [[] for _ in range(k)]
    for car, gleis in zip(train, assign):
        tracks[gleis].append(car)
    return tuple(car for track in tracks for car in track)


def play(train, assigns, k: int) -> tuple:
    """Unabhängiger Prüfer: spielt die Gleiswahl aller Durchgänge ab und gibt den Zug danach zurück (kennt weder R noch die Beschriftung)."""
    current = tuple(train)
    for assign in assigns:
        if len(assign) != len(current) or any(not 0 <= g < k for g in assign):
            raise ValueError("ungültige Gleiswahl")
        current = one_pass(current, assign, k)
    return current


@dataclass(frozen=True)
class Pass:
    before: tuple
    assign: tuple
    tracks: tuple
    after: tuple


def plan_from_labels(train, labels, k: int) -> list[Pass]:
    """Radix-Plan mit frei gewählten Ziffern: Durchgang j (niedrigste Ziffer zuerst) schickt jeden Wagen auf das Gleis der j-ten Ziffer seiner
    Beschriftung zur Basis k. Danach steht der Zug nach (Beschriftung, ursprüngliche Stelle) geordnet, weil jedes Gleis stabil ist.
    Gebraucht werden ⌈log_k L⌉ Durchgänge für L Beschriftungen."""
    n = len(train)
    if n == 0:
        return []
    count = max(labels) + 1
    if count == 1:
        return []
    if k < 2:
        raise ValueError("mit einem Gleis ist kein Durchgang nötig oder möglich")
    t = ceil_log(count, k)
    order = list(range(n))                     # aktuelle Reihenfolge: Stellen im ursprünglichen Zug
    passes = []
    for j in range(t):
        digits = [(labels[i] // k**j) % k for i in order]
        before = tuple(train[i] for i in order)
        tracks = [[] for _ in range(k)]
        for i, d in zip(order, digits):
            tracks[d].append(i)
        order = [i for track in tracks for i in track]
        passes.append(Pass(before, tuple(digits), tuple(tuple(train[i] for i in track) for track in tracks), tuple(train[i] for i in order)))
    return passes


def plan(p, k: int) -> list[Pass]:
    """Plan für einen Zug aus lauter verschiedenen Rängen: Beschriftung = Nummer der steigenden Folge."""
    return plan_from_labels(tuple(p), run_labels(p), k)


def lds_length(p) -> int:
    """Längste fallende Teilfolge (Patience-Verfahren mit negierten Werten). Bei aufsteigendem Ziel ist das die Mindestzahl paralleler Warteschlangen."""
    tails: list[int] = []
    for x in p:
        y = -x
        i = bisect.bisect_left(tails, y)
        if i == len(tails):
            tails.append(y)
        else:
            tails[i] = y
    return len(tails)


def parse_train(text: str, n_max: int = C.E1_N_MAX):
    """Text wie „2, 4, 6, 1, 3, 5“ → (Zug, None) oder (None, Meldung). Verlangt eine Folge der Ränge 1..n mit 2 <= n <= n_max."""
    if len(text) > C.E1_TEXT_MAX_LEN:
        return None, f"Der Eintrag ist zu lang (höchstens {C.E1_TEXT_MAX_LEN} Zeichen)."
    parts = [s for s in text.replace(";", " ").replace(",", " ").split() if s]
    try:
        p = tuple(int(s) for s in parts)
    except ValueError:
        return None, "Bitte ganze Zahlen eintragen, getrennt durch Komma oder Leerzeichen."
    if not 2 <= len(p) <= n_max:
        return None, f"Der Zug braucht 2 bis {n_max} Wagen (eingetragen: {len(p)})."
    if not is_train(p):
        return None, f"Jeder Rang 1 bis {len(p)} muss genau einmal vorkommen."
    return p, None


def forward_one_pass(p, k: int):
    """Vorwärtssuche über **alle** k^n Zuweisungen eines Durchgangs (unabhängig von R): (Zahl der Zuweisungen, Zahl derer, die den Zug sortieren).
    Gibt None zurück, wenn n oder k^n über den Grenzen liegen."""
    n = len(p)
    if n > C.FORWARD_N_MAX or k**n > C.FORWARD_ASSIGN_MAX or n < 1:
        return None
    assignments = np.indices((k,) * n).reshape(n, -1).T
    keys = assignments * n + np.arange(n)
    order = np.argsort(keys, axis=1, kind="stable")
    result = np.asarray(p)[order]
    ok = (result == np.arange(1, n + 1)).all(axis=1)
    return int(len(assignments)), int(ok.sum())
