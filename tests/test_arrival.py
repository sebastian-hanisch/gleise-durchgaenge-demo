"""Ankunftsmodell: Zufallszug, Modell V, Zufallswörter. Handrechnung und Eigenschaften (fester Zufalls-Seed)."""

import gdg_arrival as AR
import gdg_model as M
from gdg_rng import SplitMix64


def test_model_v_by_hand():
    """Ankunft zur Zeit 1 bis 6, Verweilzeiten 3,5; 0,5; 2,0; 4,5; 0,2; 1,0: Abfahrtszeiten 4,5; 2,5; 5,0; 8,5; 5,2; 7,0, Ränge (2, 1, 3, 6, 4, 5), R = 3 (2 vor 1, 6 vor 5)."""
    dwell = (3.5, 0.5, 2.0, 4.5, 0.2, 1.0)
    times = [i + 1 + d for i, d in enumerate(dwell)]
    ranks = AR.ranks_from_times(times)
    assert ranks == (2, 1, 3, 6, 4, 5)
    assert M.rising_count(ranks) == 3
    assert M.min_passes(ranks, 2) == 2 and M.min_passes(ranks, 3) == 1 and M.radix(6, 2) == 3


def test_ties_are_broken_by_arrival_index():
    assert AR.ranks_from_times([2.0, 2.0, 1.0]) == (2, 3, 1)


def test_random_train_is_a_permutation_and_reproducible():
    for seed in range(20):
        p = AR.random_train(9, seed)
        assert M.is_train(p) and p == AR.random_train(9, seed)
    assert AR.random_train(9, 1) != AR.random_train(9, 2)


def test_model_v_without_dwell_is_the_identity_and_trains_are_permutations():
    assert AR.model_v_train(7, 0.0, SplitMix64(1)) == tuple(range(1, 8))
    for p in AR.model_v_trains(12, 3.0, 30, 5):
        assert M.is_train(p)


def test_model_v_is_reproducible_and_depends_on_the_seed():
    a = AR.model_v_trains(10, 2.0, 20, 7)
    assert a == AR.model_v_trains(10, 2.0, 20, 7) and a != AR.model_v_trains(10, 2.0, 20, 8)
    assert AR.model_v_trains(10, None, 5, 1) == AR.model_v_trains(10, None, 5, 1)


def test_mean_rising_count_grows_with_the_dwell_time_and_the_uniform_mean_is_exact():
    """Mittel von R wächst mit D (n = 20, 400 Folgen je D) und liegt bei gleichverteilten Folgen bei (n + 1)/2 = 10,5 (Band: 4 Standardfehler)."""
    means = []
    for d in (0.5, 1.0, 4.0, 16.0):
        trains = AR.model_v_trains(20, d, 400, 11)
        means.append(sum(M.rising_count(p) for p in trains) / 400)
    assert means == sorted(means) and means[0] < 3 and means[-1] > 8
    uni = [M.rising_count(p) for p in AR.model_v_trains(20, None, 2000, 12)]
    mean = sum(uni) / len(uni)
    sd = (sum((x - mean) ** 2 for x in uni) / len(uni)) ** 0.5
    assert abs(mean - 10.5) < 4 * sd / len(uni) ** 0.5


def test_random_word_stays_inside_the_groups():
    rng = SplitMix64(3)
    for _ in range(50):
        w = AR.random_word(15, 4, rng)
        assert len(w) == 15 and set(w) <= {1, 2, 3, 4}
    assert set(AR.random_word(400, 5, SplitMix64(4))) == {1, 2, 3, 4, 5}


def test_rng_is_bit_identical_to_known_values():
    """SplitMix64 mit Seed 0: die ersten Ausgaben (aus der Referenz des Verfahrens)."""
    g = SplitMix64(0)
    assert [g.next_u64() for _ in range(3)] == [0xE220A8397B1DCDAF, 0x6E789E6AA1B965F4, 0x06C45D188009454F]
