"""Gleichstände: Wagen mit gleicher Zielgruppe (ein „Wort“ aus Gruppennummern) und die Frage, ob die Gruppen sortiert oder nur gruppiert werden müssen.

**Sortiert (feste Reihenfolge der Gruppen):** nach t Durchgängen stehen die Gruppen 1, 2, …, m hintereinander. **Gruppiert (freie Reihenfolge):** jede Gruppe
steht zusammenhängend, die Reihenfolge der Gruppen ist egal.

Beschriftungszahl L (eigene Konstruktion, kein Beweis in diesem Repo, bis n = 8 durch Aufzählung geprüft): die kleinste Zahl L von Beschriftungen
0 … L − 1 der Wagen, so dass Sortieren nach (Beschriftung, Stelle im Zug) die Gruppen nichtfallend ordnet. Für zwei Wagen e und j mit Gruppe(e) < Gruppe(j)
gilt Beschriftung(j) >= Beschriftung(e), und Beschriftung(j) >= Beschriftung(e) + 1, wenn e hinter j steht; die kleinste Lösung ist der längste gewichtete
Pfad (O(n²)). Die Mindestzahl Durchgänge ist dann ⌈log_k L⌉; bei freier Reihenfolge das Minimum über alle Gruppenreihenfolgen. Bei lauter verschiedenen
Wagen ist L = R."""

import itertools
from functools import lru_cache

import numpy as np

from gdg_model import ceil_log


def present_groups(word) -> int:
    return len(set(word))


def is_grouped(word) -> bool:
    """Steht jede Gruppe zusammenhängend?"""
    seen, prev = set(), None
    for g in word:
        if g != prev:
            if g in seen:
                return False
            seen.add(g)
            prev = g
    return True


def is_sorted_word(word) -> bool:
    return all(word[i] <= word[i + 1] for i in range(len(word) - 1))


def labels_for_ranks(ranks) -> tuple[int, ...]:
    """Kleinste Beschriftung je Wagen für die Gruppenränge `ranks` (Gleichstände erlaubt): längster gewichteter Pfad, Gruppe für Gruppe in Rangfolge."""
    n = len(ranks)
    order = sorted(range(n), key=lambda i: ranks[i])
    lam = [0] * n
    done: list[int] = []
    i = 0
    while i < n:
        j = i
        while j < n and ranks[order[j]] == ranks[order[i]]:
            j += 1
        group = order[i:j]
        for q in group:
            best = 0
            for e in done:
                c = lam[e] + (1 if e > q else 0)
                if c > best:
                    best = c
            lam[q] = best
        done.extend(group)
        i = j
    return tuple(lam)


def label_count(ranks) -> int:
    """Beschriftungszahl L (mindestens 1; leeres Wort: 1)."""
    return max(labels_for_ranks(ranks), default=0) + 1


@lru_cache(maxsize=16)
def group_rank_orders(m: int) -> np.ndarray:
    """Alle m! Reihenfolgen der Gruppen 0..m−1 als Zeilen: rank_orders[o, g] = Rang der Gruppe g in der Reihenfolge o. Zeile 0 ist die Identität."""
    perms = np.array(list(itertools.permutations(range(m))), dtype=np.int16)   # perms[o, r] = Gruppe mit Rang r
    ranks = np.empty_like(perms)
    rows = np.arange(perms.shape[0])[:, None]
    ranks[rows, perms] = np.arange(m, dtype=np.int16)[None, :]
    return ranks


def label_counts_all_orders(word0, m: int) -> np.ndarray:
    """L für jede der m! Gruppenreihenfolgen (vektorisiert über die Reihenfolgen); `word0` hat Gruppen 0..m−1."""
    w = np.asarray(word0)
    n = len(w)
    rank_orders = group_rank_orders(m)
    count = rank_orders.shape[0]
    rk = rank_orders[:, w]                                    # (Reihenfolgen, Wagen): Rang der Gruppe jedes Wagens
    lam = np.zeros((count, n), dtype=np.int16)
    empty = np.full((count, 1), -1, dtype=np.int16)
    for r in range(m):
        done = np.where(rk < r, lam, -1).astype(np.int16)
        before = np.maximum.accumulate(done, axis=1)
        before_excl = np.concatenate([empty, before[:, :-1]], axis=1)             # größte Beschriftung unter den fertigen Wagen vor mir
        after = np.maximum.accumulate(done[:, ::-1], axis=1)[:, ::-1]
        after_excl = np.concatenate([after[:, 1:], empty], axis=1)                # ... hinter mir (zählt +1)
        cand = np.maximum(np.maximum(before_excl, after_excl + 1), 0)
        lam = np.where(rk == r, cand, lam)
    return lam.max(axis=1) + 1


def passes_fixed(word, k: int) -> int:
    """Mindestzahl Durchgänge bis zur festen Reihenfolge der Gruppennummern (sortiert): ⌈log_k L⌉."""
    count = label_count(word)
    return 0 if count <= 1 else ceil_log(count, k)


def passes_free(word, m: int, k: int):
    """Mindestzahl Durchgänge bis zur Gruppierung bei freier Reihenfolge, die beste Reihenfolge (Rang je Gruppe) und deren L.
    Gruppen 1..m; die Zeile 0 der Reihenfolgen (Identität) gewinnt bei Gleichstand."""
    word0 = [g - 1 for g in word]
    counts = label_counts_all_orders(word0, m)
    best = int(np.argmin(counts))                             # erste Stelle des Minimums
    count = int(counts[best])
    t = 0 if count <= 1 else ceil_log(count, k)
    return t, tuple(int(x) for x in group_rank_orders(m)[best]), count


def radix_present(word, k: int) -> int:
    """Radix wie im Ablaufberg: ⌈log_k (Zahl der vorhandenen Gruppen)⌉."""
    g = present_groups(word)
    return 0 if g <= 1 else ceil_log(g, k)


def radix_all(m: int, k: int) -> int:
    return 0 if m <= 1 else ceil_log(m, k)
