"""Gleichstände: Beschriftungszahl L, feste und freie Gruppenreihenfolge, Radix aus den vorhandenen Gruppen. Mini-Instanzen von Hand."""

import itertools

import numpy as np
import pytest

import gdg_model as M
import gdg_words as W


def test_label_count_by_hand():
    """Zug (2, 1, 2, 1, 3, 3), Stellen 0 bis 5. Gruppe 1 (Stellen 1, 3) bekommt Beschriftung 0. Jeder 2er (Stellen 0, 2) steht links von der 1er an Stelle 3, also Beschriftung 0 + 1 = 1.
    Die 3er (Stellen 4, 5) stehen rechts von allen: Beschriftung 1. Also L = 2."""
    w = (2, 1, 2, 1, 3, 3)
    assert W.label_count(w) == 2
    assert W.labels_for_ranks(w) == (1, 0, 1, 0, 1, 1)
    assert W.passes_fixed(w, 2) == 1 and W.radix_present(w, 2) == 2 and W.radix_present(w, 3) == 1


def test_reversed_groups_by_hand():
    """(3, 3, 2, 2, 1, 1): sortiert braucht er die Beschriftungen 2, 2, 1, 1, 0, 0 (L = 3, 2 Durchgänge bei 2 Gleisen); gruppiert ist er schon (0 Durchgänge)."""
    w = (3, 3, 2, 2, 1, 1)
    assert W.labels_for_ranks(w) == (2, 2, 1, 1, 0, 0) and W.label_count(w) == 3
    assert W.passes_fixed(w, 2) == 2 and W.passes_fixed(w, 3) == 1
    assert W.is_grouped(w) and not W.is_sorted_word(w)
    t, ranks, count = W.passes_free(w, 3, 2)
    assert t == 0 and count == 1 and ranks == (2, 1, 0)              # beste Reihenfolge: Gruppe 3 zuerst, dann 2, dann 1


def test_distinct_cars_equal_rising_runs():
    for p in itertools.permutations(range(1, 6)):
        assert W.label_count(p) == M.rising_count(p)


def test_all_distinct_groups_are_always_grouped():
    for p in itertools.permutations(range(1, 5)):
        assert W.is_grouped(p)
        assert W.passes_free(p, 4, 2)[0] == 0


def test_free_never_exceeds_fixed():
    rng_words = [w for w in itertools.product(range(1, 4), repeat=6)]
    for w in rng_words[::7]:
        assert W.passes_free(w, 3, 2)[0] <= W.passes_fixed(w, 2)


def test_vectorised_label_counts_equal_the_scalar_routine():
    """Die vektorisierte Rechnung über alle m! Reihenfolgen gegen die einfache Doppelschleife mit umbenannten Gruppen."""
    rng = np.random.default_rng(5)
    for _ in range(40):
        m = int(rng.integers(2, 5))
        n = int(rng.integers(3, 10))
        word = tuple(int(x) for x in rng.integers(1, m + 1, size=n))
        counts = W.label_counts_all_orders(np.array(word) - 1, m)
        ranks = W.group_rank_orders(m)
        for o in range(ranks.shape[0]):
            assert counts[o] == W.label_count([int(ranks[o, g - 1]) for g in word])


def test_group_rank_orders_are_all_permutations():
    r = W.group_rank_orders(4)
    assert r.shape == (24, 4) and (r[0] == [0, 1, 2, 3]).all()
    assert len({tuple(int(x) for x in row) for row in r}) == 24 and all(sorted(row) == [0, 1, 2, 3] for row in r.tolist())


def test_present_groups_and_radix():
    assert W.present_groups((1, 1, 5, 5)) == 2
    assert W.radix_present((1, 1, 5, 5), 2) == 1 and W.radix_present((1, 1), 2) == 0 and W.radix_present((1, 2, 3, 4, 5), 2) == 3
    assert W.radix_all(6, 3) == 2 and W.radix_all(1, 3) == 0


def test_word_plan_reaches_the_goal():
    """Der Plan nach Beschriftung bringt jedes Wort der Mehrfachmenge (2, 2, 2) in die feste Reihenfolge; mit der besten freien Reihenfolge gruppiert er."""
    for w in set(itertools.permutations((1, 1, 2, 2, 3, 3))):
        labels = W.labels_for_ranks(w)
        passes = M.plan_from_labels(w, labels, 2)
        assert len(passes) == W.passes_fixed(w, 2)
        assert W.is_sorted_word(M.play(w, [p.assign for p in passes], 2))
        t, ranks, _ = W.passes_free(w, 3, 2)
        free_labels = W.labels_for_ranks([ranks[g - 1] for g in w])
        free_passes = M.plan_from_labels(w, free_labels, 2)
        assert len(free_passes) == t
        assert W.is_grouped(M.play(w, [p.assign for p in free_passes], 2))
