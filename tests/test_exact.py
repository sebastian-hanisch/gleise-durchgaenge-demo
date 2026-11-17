"""Exakte Verteilung: Eulersche Zahlen, Mittel, Anteil unter Radix, Sägezahn. Handwerte aus Brüchen (Ganzzahlen), keine Gleitkomma-Gleichheit."""

import math
from fractions import Fraction

import pytest

import gdg_constants as C
import gdg_exact as EX
import gdg_model as M


def test_eulerian_rows_by_hand():
    assert EX.eulerian_row(1) == (1,)
    assert EX.eulerian_row(2) == (1, 1)
    assert EX.eulerian_row(3) == (1, 4, 1)
    assert EX.eulerian_row(4) == (1, 11, 11, 1)
    assert EX.eulerian_row(5) == (1, 26, 66, 26, 1)
    assert EX.eulerian_row(6) == (1, 57, 302, 302, 57, 1)
    with pytest.raises(ValueError):
        EX.eulerian_row(0)


@pytest.mark.parametrize("n", [10, 20, 50, 100, 200, 500])
def test_row_sum_symmetry_and_mean_of_rising_runs(n):
    row = EX.eulerian_row(n)
    assert sum(row) == math.factorial(n)
    assert row == row[::-1]                                                        # A(n, d) = A(n, n − 1 − d)
    assert Fraction(sum((d + 1) * a for d, a in enumerate(row)), math.factorial(n)) == Fraction(n + 1, 2)


def test_summary_n10_k2_by_hand():
    """n = 10, k = 2: Radix 4; 1 Folge mit 0, 1 013 mit 1, 503 032 mit 2, 3 123 740 mit 3 und 1 014 mit 4 Durchgängen; Mittel 2,861."""
    s = EX.summary(10, 2)
    assert s.counts == {0: 1, 1: 1013, 2: 503032, 3: 3123740, 4: 1014}
    assert s.total == 3628800 and s.radix == 4 and s.at_radix == 1014
    assert s.share_below == Fraction(3628800 - 1014, 3628800)
    assert abs(float(s.mean) - 2.8611) < 5e-5


def test_summary_n8_k2_is_exactly_half_below_radix():
    """n = 8, k = 2: höchstens 2 Durchgänge heißt R ≤ 4, das sind 1 + 247 + 4 293 + 15 619 = 20 160 Folgen: genau die Hälfte von 40 320."""
    s = EX.summary(8, 2)
    assert sum(EX.eulerian_row(8)[:4]) == 20160
    assert s.share_below == Fraction(1, 2)


@pytest.mark.parametrize("r", range(2, 8))
def test_half_below_radix_at_powers_of_two(r):
    """k = 2, n = 2^r: der Anteil unter Radix ist genau 1/2 (Symmetrie der Eulerschen Zahlen); n = 2^r + 1 (r >= 3): alle bis auf die Umkehrfolge und wenige andere."""
    assert EX.summary(2**r, 2).share_below == Fraction(1, 2)


def test_n9_k2_all_but_the_reversal_are_below_radix():
    s = EX.summary(9, 2)
    assert s.radix == 4 and s.share_below == Fraction(362879, 362880)


def test_n27_k3_share_below_radix_is_tiny():
    s = EX.summary(27, 3)
    assert s.radix == 3 and Fraction(11, 10000) < s.share_below < Fraction(13, 10000)


def test_summary_n10_k4_share_below_radix():
    s = EX.summary(10, 4)
    assert s.radix == 2 and s.share_below == Fraction(sum(EX.eulerian_row(10)[:4]), math.factorial(10))
    assert abs(float(s.share_below) - 0.1389) < 5e-4


def test_worst_case_equals_radix_for_all_n_and_k():
    """Schlimmster Fall = Radix (die Umkehrfolge hat R = n): n = 2 bis 200, k = 2 bis 10, aus den Verteilungen gezählt."""
    for k in range(2, 11):
        for n in range(2, 201):
            s = EX.summary(n, k)
            assert max(s.counts) == M.radix(n, k) and s.counts[M.radix(n, k)] == s.at_radix > 0


def test_n500_is_exact_integer_arithmetic():
    s = EX.summary(500, 2)
    assert s.total == math.factorial(500) and sum(s.counts.values()) == s.total
    assert 8 < float(s.mean) < 9 and s.radix == 9


def test_summary_rejects_degenerate_input():
    for bad in ((1, 2), (5, 1)):
        with pytest.raises(ValueError):
            EX.summary(*bad)


def test_sawtooth_counts_of_zero_shares():
    """Zahl der n zwischen 20 und 200 (181 Werte) mit Anteil unter 0,00005: k = 2: 0, k = 3: 15, k = 4: 62, k = 6: 121, k = 10: 68."""
    stats = EX.sawtooth_stats()
    assert {k: len(v["zeros"]) for k, v in stats.items()} == {2: 0, 3: 15, 4: 62, 6: 121, 10: 68}
    assert all(v["count"] == 181 for v in stats.values())


def test_sawtooth_extremes_for_k2_and_k3():
    s2, s3 = EX.sawtooth_stats((2, 3))[2], EX.sawtooth_stats((2, 3))[3]
    assert (s2["min"], s2["min_n"]) == (0.5, 32) and (s2["max"], s2["max_n"]) == (1.0, 33)
    assert s3["max_n"] == 28 and s3["max"] == 1.0 and s3["min_n"] == 81 and s3["min"] < 1e-6


def test_sawtooth_shares_at_powers():
    saw = EX.sawtooth()
    assert saw[3][9][0] == pytest.approx(0.0416, abs=5e-5) and saw[3][27][0] == pytest.approx(0.0012, abs=5e-5)
    assert saw[4][16][0] == pytest.approx(0.0002, abs=5e-5)
    assert all(saw[2][2**r][0] == 0.5 for r in range(3, 8))


def test_sawtooth_matches_summary_for_every_k_and_n():
    saw = EX.sawtooth()
    for k in C.E3_K_OPTIONS:
        for n in (2, 3, 9, 27, 28, 64, 100, 150, 200):
            s = EX.summary(n, k)
            assert saw[k][n] == (float(s.share_below), float(s.mean))


def test_enumeration_helpers():
    assert EX.enumerate_rising_histogram(5) == list(EX.eulerian_row(5))
    assert EX.lds_histogram(4) == [1, 13, 9, 1]                                     # Zahl der Folgen mit längster fallender Teilfolge 1, 2, 3, 4
    assert EX.mean_passes_from_histogram(EX.enumerate_rising_histogram(6), 2) == Fraction(1439, 720)
