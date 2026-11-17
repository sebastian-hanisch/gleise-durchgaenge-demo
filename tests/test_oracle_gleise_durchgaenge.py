"""Orakel-Tests: die Mindestzahl Durchgänge und die Verteilung gegen einen ANDEREN Rechenweg (ORACLE-PLAYBOOK §5, §6).

Rechenwege, die nichts von R, den Eulerschen Zahlen oder der Beschriftung wissen (tests/oracle_helpers.py):

* Vorwärtssimulation: von jedem Zug aus **alle k^n** Zuweisungen eines Durchgangs, Breitensuche bis zum sortierten Zug.
* Rückwärts-Breitensuche vom sortierten Zug (die Vorgänger sind alle Füllungen der Gleise mit Teilstücken).
* Aufzählung aller n! Folgen für die Eulerschen Zahlen, das Mittel von R und die Tabelle der parallelen Warteschlangen.

Der Fall n = 9 (362 880 Folgen) läuft mit GDG_SLOW=1 (`pytest -m slow`); alle anderen Fälle (bis n = 8) laufen immer."""

import itertools
import math
from fractions import Fraction

import pytest

import gdg_exact as EX
import gdg_model as M
import gdg_words as W
import oracle_helpers as O


def perms(n):
    return list(itertools.permutations(range(1, n + 1)))


def ceil_log_independent(value: int, k: int) -> int:
    """Kleinstes t mit k^t >= value, ohne die Funktion der Demo (Gleitkomma mit Korrektur)."""
    t = max(0, math.ceil(math.log(value, k) - 1e-9)) if value > 1 else 0
    while k**t < value:
        t += 1
    while t > 0 and k ** (t - 1) >= value:
        t -= 1
    return t


def rising_independent(p) -> int:
    """R ohne die Funktion der Demo: 1 + Zahl der v, bei denen v + 1 vor v steht."""
    pos = [0] * (len(p) + 2)
    for i, v in enumerate(p):
        pos[v] = i
    return 1 + sum(1 for v in range(1, len(p)) if pos[v + 1] < pos[v])


# ---------------------------------------------------------------- Vorwärtssimulation gegen die Formel ⌈log_k R⌉


@pytest.mark.parametrize("n,k", [(3, 2), (4, 2), (5, 2), (6, 2), (4, 3), (5, 3), (6, 3), (5, 4), (6, 4)])
def test_forward_simulation_equals_formula_for_all_trains(n, k):
    words = perms(n)
    levels = O.forward_levels(words, k, lambda w: w == tuple(range(1, n + 1)))
    assert len(levels) == math.factorial(n)
    for p in words:
        assert levels[p] == M.min_passes(p, k) == (0 if rising_independent(p) == 1 else ceil_log_independent(rising_independent(p), k)), p


def test_forward_levels_of_known_cases():
    """Stufen (Zahl der Folgen mit 0, 1, 2, … Durchgängen) von Hand bzw. aus der Handrechnung: n = 6, k = 2 hat 1, 57, 604, 58; Mittel 1439/720."""
    levels = O.levels_list(O.forward_levels(perms(6), 2, lambda w: w == (1, 2, 3, 4, 5, 6)))
    assert levels == [1, 57, 604, 58]
    assert Fraction(sum(t * c for t, c in enumerate(levels)), 720) == Fraction(1439, 720)
    assert O.levels_list(O.forward_levels(perms(6), 3, lambda w: w == (1, 2, 3, 4, 5, 6))) == [1, 359, 360]


@pytest.mark.parametrize("n,k,stufen", [(7, 2, [1, 120, 3607, 1312]), (8, 2, [1, 247, 19912, 20160]), (7, 3, [1, 1311, 3728]), (7, 4, [1, 3727, 1312])])
def test_forward_simulation_larger_cases(n, k, stufen):
    words = perms(n)
    levels = O.forward_levels(words, k, lambda w: w == tuple(range(1, n + 1)))
    assert O.levels_list(levels) == stufen
    assert all(levels[p] == M.min_passes(p, k) for p in words)


# ---------------------------------------------------------------- zweites Orakel: Rückwärts-Breitensuche


@pytest.mark.parametrize("n,k", [(4, 2), (5, 2), (6, 2), (4, 3), (5, 3)])
def test_backward_search_equals_formula(n, k):
    dist = O.backward_levels(n, k)
    assert len(dist) == math.factorial(n)
    assert all(dist[p] == M.min_passes(p, k) for p in dist)


# ---------------------------------------------------------------- Verteilung, Mittel, Tabelle


@pytest.mark.parametrize("n", range(4, 9))
def test_eulerian_numbers_equal_enumeration_of_rising_runs(n):
    counts = [0] * (n + 1)
    for p in perms(n):
        counts[rising_independent(p)] += 1
    assert counts[1:] == list(EX.eulerian_row(n))
    assert sum(counts) == math.factorial(n)
    assert Fraction(sum(r * c for r, c in enumerate(counts)), math.factorial(n)) == Fraction(n + 1, 2)


@pytest.mark.parametrize("n,k", [(5, 2), (6, 2), (7, 3), (8, 2), (8, 3), (8, 4)])
def test_summary_equals_enumeration_of_formula(n, k):
    """Verteilung der Mindestzahl aus den Eulerschen Zahlen gegen die Aufzählung aller Folgen mit unabhängig gerechnetem R."""
    counts = {}
    for p in perms(n):
        r = rising_independent(p)
        t = 0 if r == 1 else ceil_log_independent(r, k)
        counts[t] = counts.get(t, 0) + 1
    s = EX.summary(n, k)
    assert dict(sorted(s.counts.items())) == dict(sorted(counts.items()))
    assert s.total == math.factorial(n)
    assert s.mean == Fraction(sum(t * c for t, c in counts.items()), math.factorial(n))


@pytest.mark.slow
def test_eulerian_numbers_up_to_nine_and_table_of_parallel_queues():
    """n = 9: Eulersche Zahlen gegen Aufzählung; Tabelle „frei“ gegen die Maschine für parallele Warteschlangen (n <= 6) und die bekannten Folgen (Catalan, 6, 23, 103, …)."""
    counts = [0] * 10
    for p in perms(9):
        counts[rising_independent(p)] += 1
    assert counts[1:] == list(EX.eulerian_row(9))
    hist = EX.lds_histogram(9)
    assert sum(hist[:2]) == 4862 and sum(hist[:3]) == 94359
    brute = [0] * 9
    for p in perms(9):
        brute[M.lds_length(p) - 1] += 1
    assert hist == brute


@pytest.mark.parametrize("n,k", [(3, 2), (4, 2), (5, 2), (4, 3), (5, 3), (6, 2), (6, 3)])
def test_parallel_queue_machine_equals_longest_decreasing_subsequence(n, k):
    """Tarjan Lemma 2 (nach Quellenbericht) an allen Folgen: k parallele Warteschlangen sortieren genau die Folgen mit LDS <= k."""
    for p in perms(n):
        assert O.parallel_queues_sortable(p, k) == (M.lds_length(p) <= k), p


def test_free_counts_are_catalan_and_known_sequence_for_three_queues():
    """Zahl der Folgen mit LDS <= k aus der Aufzählung: k = 2 sind die Catalan-Zahlen, k = 3 die Folge 6, 23, 103, 513, 2761 (n = 3 bis 7)."""
    catalan = {3: 5, 4: 14, 5: 42, 6: 132, 7: 429}
    three = {3: 6, 4: 23, 5: 103, 6: 513, 7: 2761}
    for n in range(3, 8):
        hist = EX.lds_histogram(n)
        assert sum(hist[:2]) == catalan[n]
        assert sum(hist[:3]) == three[n]
        assert hist == [sum(1 for p in perms(n) if M.lds_length(p) == v) for v in range(1, n + 1)]


# ---------------------------------------------------------------- der Plan wird von einem unabhängigen Prüfer abgespielt


def independent_play(train, assigns, k):
    cur = list(train)
    for assign in assigns:
        tracks = [[] for _ in range(k)]
        for car, g in zip(cur, assign):
            tracks[g].append(car)
        cur = [c for t in tracks for c in t]
    return cur


@pytest.mark.parametrize("n,k", [(n, k) for n in range(2, 8) for k in (2, 3, 4)])
def test_plan_sorts_every_train_and_uses_the_minimum(n, k):
    for p in perms(n):
        pl = M.plan(p, k)
        assert len(pl) == M.min_passes(p, k)
        assert independent_play(p, [x.assign for x in pl], k) == list(range(1, n + 1)), p


# ---------------------------------------------------------------- Gleichstände: Beschriftungszahl L gegen Vorwärtssimulation

FIXED_CASES = [((2, 2, 2), 2), ((2, 2, 2), 3), ((2, 2, 2, 1), 2), ((2, 2, 2, 1), 3), ((3, 2, 1), 2)]
FIXED_SLOW = [((2, 2, 2, 2), 2), ((3, 3, 1, 1), 2), ((2, 2, 1, 1, 1, 1), 2), ((2, 2, 2, 2), 3), ((3, 3, 1, 1), 3), ((2, 2, 1, 1, 1, 1), 3)]


def _check_fixed(sizes, k):
    words = O.multiset_words(sizes)
    goal = tuple(sorted(words[0]))
    levels = O.forward_levels(words, k, lambda w: w == goal)
    for w in words:
        assert levels[w] == W.passes_fixed(w, k), (sizes, k, w)
    return O.levels_list(levels)


@pytest.mark.parametrize("sizes,k", FIXED_CASES)
def test_label_formula_for_fixed_group_order(sizes, k):
    _check_fixed(sizes, k)


def test_known_levels_for_fixed_group_order():
    assert _check_fixed((2, 2, 2), 2) == [1, 42, 47]
    assert _check_fixed((2, 2, 2), 3) == [1, 89]


@pytest.mark.parametrize("sizes,k", FIXED_SLOW)
def test_label_formula_for_fixed_group_order_larger(sizes, k):
    _check_fixed(sizes, k)


FREE_CASES = [((2, 2, 2), 2), ((2, 2, 2), 3), ((2, 2, 2, 1), 2), ((3, 2, 1), 2), ((2, 2, 1, 1), 2), ((1, 1, 1, 1, 1, 1), 2), ((2, 2, 1, 1, 1), 2)]


def _check_free(sizes, k):
    words = O.multiset_words(sizes)
    m = len(sizes)
    levels = O.forward_levels(words, k, O.is_grouped)
    for w in words:
        assert levels[w] == W.passes_free(w, m, k)[0], (sizes, k, w)
    return O.levels_list(levels)


@pytest.mark.parametrize("sizes,k", FREE_CASES)
def test_label_formula_for_free_group_order(sizes, k):
    _check_free(sizes, k)


def test_known_levels_for_free_group_order():
    assert _check_free((2, 2, 2), 2) == [6, 84]


def test_label_formula_for_free_group_order_larger():
    assert _check_free((2, 2, 2, 2), 2) == [24, 1608, 888]


def test_label_count_equals_rising_count_for_distinct_cars():
    for n in range(2, 7):
        for p in perms(n):
            assert W.label_count(p) == rising_independent(p)


@pytest.mark.parametrize("n,k", [(3, 2), (4, 2), (5, 2), (6, 2), (4, 3), (5, 3), (6, 3)])
def test_immediate_output_equals_delayed_output_for_parallel_queues(n, k):
    """Bei Warteschlangen ändert Aufschieben der Ausgabe nichts: sofortige und spätere Ausgabe sortieren dieselben Folgen (alle Folgen n <= 6, k = 2, 3)."""
    for p in perms(n):
        assert O.parallel_queues_sortable_immediate(p, k) == O.parallel_queues_sortable(p, k) == (M.lds_length(p) <= k), p
