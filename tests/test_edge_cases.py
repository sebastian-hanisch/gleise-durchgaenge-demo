"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): n = 0, 1, 2, k = 1, k >= n, Gruppen mit einem Wagen, Grenzen der Regler."""

import pytest

import gdg_arrival as AR
import gdg_constants as C
import gdg_evaluation as ev
import gdg_exact as EX
import gdg_model as M
import gdg_words as W
from gdg_rng import SplitMix64


def test_empty_and_single_car_trains():
    assert M.rising_runs(()) == [] and M.rising_count(()) == 0 and M.min_passes((), 2) == 0
    assert M.rising_runs((1,)) == [[1]] and M.min_passes((1,), 2) == 0 and M.plan((1,), 2) == []
    assert M.radix(0, 2) == 0 and M.radix(1, 2) == 0
    assert M.run_labels(()) == ()


def test_exactly_two_cars():
    """n = 2: (1, 2) ist sortiert, (2, 1) braucht einen Durchgang (R = 2 <= k = 2); mit k = 1 geht (2, 1) nicht."""
    assert M.min_passes((1, 2), 2) == 0 and M.min_passes((2, 1), 2) == 1
    assert M.plan((2, 1), 2)[0].after == (1, 2)
    assert M.min_passes((2, 1), 1) is None and M.min_passes((1, 2), 1) == 0
    with pytest.raises(ValueError):
        M.plan((2, 1), 1)
    s = EX.summary(2, 2)
    assert s.counts == {0: 1, 1: 1} and s.radix == 1 and s.share_below == __import__("fractions").Fraction(1, 2)


def test_k_at_least_n_needs_one_pass_for_every_train():
    from itertools import permutations
    for p in permutations(range(1, 5)):
        assert M.min_passes(p, 4) <= 1 and M.min_passes(p, 6) <= 1


def test_identity_needs_none_and_reversal_needs_radix():
    for n in range(2, 15):
        for k in (2, 3, 5):
            assert M.min_passes(tuple(range(1, n + 1)), k) == 0
            assert M.min_passes(tuple(range(n, 0, -1)), k) == M.radix(n, k)


def test_all_cars_in_one_group_and_two_groups():
    assert W.passes_fixed((2, 2, 2, 2), 2) == 0 and W.passes_free((2, 2, 2, 2), 2, 2)[0] == 0 and W.radix_present((2, 2, 2, 2), 2) == 0
    w = (2, 1, 2, 1)
    assert W.passes_fixed(w, 2) == 1 and W.passes_free(w, 2, 2)[0] == 1 and W.radix_present(w, 2) == 1     # zwei Gruppen, zwei Gleise: ein Durchgang


def test_already_grouped_word_needs_no_pass_for_free_order():
    assert W.passes_free((2, 2, 3, 3, 1, 1), 3, 2)[0] == 0 and W.passes_fixed((2, 2, 3, 3, 1, 1), 2) >= 1


def test_group_stats_at_the_slider_limits():
    g = ev.analyse_groups(C.E5_M_MAX, C.E5_N_MAX, C.E5_K_MAX, C.E5_TRIALS_MAX, 1)
    assert g.trials == C.E5_TRIAL_CAP[7] and g.asked_trials == C.E5_TRIALS_MAX
    g2 = ev.analyse_groups(C.E5_M_MIN, C.E5_N_MIN, C.E5_K_MIN, C.E5_TRIALS_MIN, 1)
    assert g2.trials == C.E5_TRIALS_MIN and 0 <= g2.free_lt_present <= g2.trials


def test_model_v_at_the_limits():
    a = ev.analyse_model_v("0.5", C.E4_N_MIN, C.E4_K_MAX, C.E4_TRIALS_MIN, 0)
    assert a.radix == M.radix(C.E4_N_MIN, C.E4_K_MAX) and 0 <= a.mean_passes <= a.radix
    b = ev.analyse_model_v("gleichverteilt", 12, 2, 100, 0)
    assert b.d == "gleichverteilt" and 1 <= b.mean_r <= 12


def test_distribution_at_the_limits():
    for n, k in ((C.E2_N_MIN, C.E2_K_MIN), (C.E2_N_MIN, C.E2_K_MAX), (C.E2_N_MAX, C.E2_K_MIN), (C.E2_N_MAX, C.E2_K_MAX)):
        d = ev.analyse_distribution(n, k)
        kind, text = ev.verdict_distribution(d)
        assert kind in ("info", "warning") and f"n = {n}, k = {k}" in text


def test_random_train_edge_sizes():
    assert AR.random_train(1, 5) == (1,) and AR.random_train(2, 5) in ((1, 2), (2, 1)) and AR.random_train(0, 5) == ()


def test_random_word_with_one_group_is_constant():
    assert AR.random_word(5, 1, SplitMix64(1)) == (1, 1, 1, 1, 1)
