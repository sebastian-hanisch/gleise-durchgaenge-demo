"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2): Aussagen, die für das Verfahren gelten müssen, ohne dass man das Ergebnis kennt. Zufallsinstanzen aus dem SplitMix64 mit festem Zufalls-Seed.

Jede Eigenschaft ist eine belegte Aussage (Aufzählung bis n = 8 bzw. Beweisskizze im Expander), nicht nur das heutige Verhalten des Codes."""

import itertools

import gdg_arrival as AR
import gdg_exact as EX
import gdg_model as M
import gdg_words as W
from gdg_rng import SplitMix64


def trains(count, n_lo=2, n_hi=14, seed=1):
    rng = SplitMix64(seed)
    out = []
    for _ in range(count):
        n = n_lo + rng.below(n_hi - n_lo + 1)
        p = list(range(1, n + 1))
        rng.shuffle(p)
        out.append(tuple(p))
    return out


def inverse(p):
    inv = [0] * len(p)
    for i, v in enumerate(p):
        inv[v - 1] = i + 1
    return tuple(inv)


def test_rising_count_is_one_plus_descents_of_the_inverse():
    for p in trains(200):
        inv = inverse(p)
        assert M.rising_count(p) == 1 + sum(1 for i in range(len(inv) - 1) if inv[i] > inv[i + 1])


def test_rising_count_is_invariant_under_reverse_and_complement():
    """p'_i = n + 1 − p_{n+1−i}: aus (v+1 vor v) wird wieder (v'+1 vor v')."""
    for p in trains(200, seed=2):
        n = len(p)
        q = tuple(n + 1 - p[n - 1 - i] for i in range(n))
        assert M.rising_count(q) == M.rising_count(p)


def test_identity_needs_none_reversal_needs_radix_and_nothing_exceeds_radix():
    for p in trains(200, seed=3):
        n = len(p)
        for k in (2, 3, 4, 7):
            t = M.min_passes(p, k)
            assert t <= M.radix(n, k)
            assert M.min_passes(tuple(range(1, n + 1)), k) == 0 and M.min_passes(tuple(range(n, 0, -1)), k) == M.radix(n, k)
    for n in range(2, 9):                                              # Gegenprobe über alle Folgen bis n = 8: nie mehr als Radix
        for k in (2, 3):
            assert all(M.min_passes(p, k) <= M.radix(n, k) for p in itertools.permutations(range(1, n + 1)))


def test_more_tracks_never_need_more_passes():
    for p in trains(200, seed=4):
        counts = [M.min_passes(p, k) for k in range(2, 9)]
        assert counts == sorted(counts, reverse=True)


def test_after_the_first_pass_of_the_plan_one_pass_less_remains():
    """Nach dem ersten Durchgang des Plans reichen höchstens t − 1 weitere (die Ziffern der Beschriftung werden der Reihe nach abgearbeitet)."""
    for p in trains(120, n_lo=3, seed=5):
        for k in (2, 3):
            pl = M.plan(p, k)
            if pl:
                assert M.min_passes(pl[0].after, k) <= len(pl) - 1


def test_longest_decreasing_subsequence_is_at_most_rising_count():
    for p in trains(200, seed=6):
        assert M.lds_length(p) <= M.rising_count(p)
    for n in range(1, 8):
        assert all(M.lds_length(p) <= M.rising_count(p) for p in itertools.permutations(range(1, n + 1)))


def test_free_never_worse_than_fixed_and_distinct_cars_are_always_grouped():
    rng = SplitMix64(7)
    for _ in range(150):
        m = 2 + rng.below(4)
        word = AR.random_word(4 + rng.below(8), m, rng)
        for k in (2, 3):
            assert W.passes_free(word, m, k)[0] <= W.passes_fixed(word, k)
    for p in trains(40, n_hi=6, seed=8):
        assert W.passes_free(p, len(p), 2)[0] == 0


def test_renaming_the_groups_does_not_change_the_free_result():
    """Bei freier Reihenfolge kommt es nicht auf die Namen der Gruppen an (nur auf die Gleichheit der Gruppen)."""
    rng = SplitMix64(9)
    for _ in range(60):
        m = 2 + rng.below(3)
        word = AR.random_word(5 + rng.below(6), m, rng)
        names = list(range(1, m + 1))
        rng.shuffle(names)
        renamed = tuple(names[g - 1] for g in word)
        assert W.passes_free(word, m, 2)[0] == W.passes_free(renamed, m, 2)[0]


def test_same_seed_same_result_and_different_seed_differs():
    a = AR.model_v_trains(15, 2.0, 30, 3)
    assert a == AR.model_v_trains(15, 2.0, 30, 3) and a != AR.model_v_trains(15, 2.0, 30, 4)


def test_mean_of_rising_count_in_samples_is_in_the_expected_band_for_uniform_trains():
    """Mittel von R bei gleichverteilten Folgen liegt (n + 1)/2 nahe: 1000 Folgen mit n = 15 (Band 4 Standardfehler)."""
    sample = [M.rising_count(p) for p in AR.model_v_trains(15, None, 1000, 10)]
    mean = sum(sample) / 1000
    sd = (sum((x - mean) ** 2 for x in sample) / 1000) ** 0.5
    assert abs(mean - 8.0) < 4 * sd / 1000**0.5


def test_exact_mean_passes_never_exceeds_radix_and_grows_with_n():
    for k in (2, 3, 4):
        means = [float(EX.summary(n, k).mean) for n in range(2, 60)]
        assert all(m <= M.radix(n, k) for m, n in zip(means, range(2, 60)))
        assert means == sorted(means)
