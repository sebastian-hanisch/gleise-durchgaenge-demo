"""Unabhängige Rechenwege für die Orakel-Tests (kein Import aus den Rechenmodulen der Demo außer der Zufalls- und Konstantenseite).

* Vorwärtssimulation: Von jedem Wort aus werden **alle** k^n Zuweisungen eines Durchgangs ausgeführt; die Mindestzahl ist die Stufe der Breitensuche.
* Rückwärtssuche: Vom Ziel aus werden alle Zuweisungen **umgekehrt** (die Vorgänger eines Zuges q sind alle Füllungen der Gleise mit den Teilstücken von q).
* Maschine für parallele Warteschlangen: alle Zuweisungen zu Warteschlangen, dann Auslesen der Vorderseiten in beliebiger Reihenfolge.
"""

import itertools

import numpy as np


def distinct_orders(n: int, k: int) -> np.ndarray:
    """Alle verschiedenen Umordnungen, die ein Durchgang erzeugen kann: Zeile = Indizes, nach denen der Zug neu gelesen wird (aus allen k^n Zuweisungen)."""
    assign = np.indices((k,) * n).reshape(n, -1).T
    keys = assign * n + np.arange(n)
    orders = np.argsort(keys, axis=1, kind="stable")
    return np.unique(orders, axis=0)


def forward_levels(words, k: int, is_goal) -> dict:
    """Mindestzahl Durchgänge je Wort durch Breitensuche über die Vorwärts-Nachfolger aller Zuweisungen. `is_goal(wort)`: Zielwörter (Stufe 0)."""
    words = [tuple(w) for w in words]
    n = len(words[0])
    index = {w: i for i, w in enumerate(words)}
    arr = np.array(words, dtype=np.int64)
    base = int(arr.max()) + 1
    pw = base ** np.arange(n - 1, -1, -1, dtype=np.int64)
    codes = arr @ pw
    sort_idx = np.argsort(codes)
    sorted_codes = codes[sort_idx]
    orders = distinct_orders(n, k)
    level = np.full(len(words), -1, dtype=np.int64)
    for w, i in index.items():
        if is_goal(w):
            level[i] = 0
    t = 0
    chunk = max(1, 4_000_000 // (len(orders) * n))
    while (level < 0).any():
        t += 1
        known = level >= 0
        todo = np.nonzero(~known)[0]
        found = np.zeros(len(words), dtype=bool)
        for s in range(0, len(todo), chunk):
            ids = todo[s:s + chunk]
            succ = arr[ids][:, orders]                       # (Wörter, Reihenfolgen, n)
            succ_codes = succ @ pw
            pos = np.searchsorted(sorted_codes, succ_codes)
            hit = sort_idx[np.minimum(pos, len(words) - 1)]
            valid = sorted_codes[np.minimum(pos, len(words) - 1)] == succ_codes
            found[ids] = (known[hit] & valid).any(axis=1)
        if not found.any():
            break
        level[found] = t
    return {w: int(level[i]) for w, i in index.items()}


def levels_list(levels: dict) -> list[int]:
    top = max(levels.values())
    return [sum(1 for v in levels.values() if v == t) for t in range(top + 1)]


def backward_levels(n: int, k: int) -> dict:
    """Rückwärts-Breitensuche vom sortierten Zug: Vorgänger von q sind alle Füllungen `fill(q, a)` mit einer Zuweisung a (Teilstücke von q auf die Gleise)."""
    goal = tuple(range(1, n + 1))
    dist = {goal: 0}
    frontier = [goal]
    t = 0
    while frontier:
        t += 1
        new = []
        for q in frontier:
            for a in itertools.product(range(k), repeat=n):
                counts = [a.count(g) for g in range(k)]
                segs, pos = [], 0
                for c in counts:
                    segs.append(list(q[pos:pos + c]))
                    pos += c
                nxt = [0] * k
                p = []
                for g in a:
                    p.append(segs[g][nxt[g]])
                    nxt[g] += 1
                p = tuple(p)
                if p not in dist:
                    dist[p] = t
                    new.append(p)
        frontier = new
    return dist


def parallel_queues_sortable(p, k: int) -> bool:
    """k parallele Warteschlangen, Ausgabe 1..n: gibt es eine Zuweisung, nach der sich der Zug sortiert ausgeben lässt (Vorderseiten frei auslesbar)?"""
    n = len(p)
    for assign in itertools.product(range(k), repeat=n):
        queues = [[] for _ in range(k)]
        for x, a in zip(p, assign):
            queues[a].append(x)
        heads = [0] * k
        nxt = 1
        while nxt <= n:
            for q in range(k):
                if heads[q] < len(queues[q]) and queues[q][heads[q]] == nxt:
                    heads[q] += 1
                    nxt += 1
                    break
            else:
                break
        if nxt == n + 1:
            return True
    return False


def multiset_words(sizes):
    """Alle verschiedenen Wörter mit den Gruppengrößen `sizes` (Gruppe g kommt sizes[g − 1]-mal vor)."""
    return sorted(set(itertools.permutations([g + 1 for g, c in enumerate(sizes) for _ in range(c)])))


def is_grouped(word) -> bool:
    seen, prev = set(), None
    for g in word:
        if g != prev:
            if g in seen:
                return False
            seen.add(g)
            prev = g
    return True


def parallel_queues_sortable_immediate(p, k: int) -> bool:
    """Wie `parallel_queues_sortable`, aber die Ausgabe erfolgt **sofort**, sobald der nächste Rang an einer Vorderseite steht (Tiefensuche über die Wahl der Warteschlange je Wagen)."""
    n = len(p)
    seen = set()

    def drain(queues, nxt):
        queues = [list(q) for q in queues]
        again = True
        while again:
            again = False
            for q in queues:
                if q and q[0] == nxt:
                    q.pop(0)
                    nxt += 1
                    again = True
        return tuple(tuple(q) for q in queues), nxt

    def rec(i, queues, nxt):
        queues, nxt = drain(queues, nxt)
        key = (i, tuple(sorted(queues)), nxt)
        if key in seen:
            return False
        seen.add(key)
        if i == n:
            return nxt == n + 1
        for a in range(k):
            new = [list(q) for q in queues]
            new[a].append(p[i])
            if rec(i + 1, tuple(tuple(q) for q in new), nxt):
                return True
        return False

    return rec(0, tuple(() for _ in range(k)), 1)
