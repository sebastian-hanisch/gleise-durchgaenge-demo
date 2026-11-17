"""Mini-Instanzen von Hand (DEMO-PLAYBOOK §1b): steigende Folgen, Plan, Prüfer, Vorwärtssuche, Eingabe."""

import itertools

import pytest

import gdg_model as M


def test_ceil_log_by_hand():
    assert M.ceil_log(1, 2) == 0 and M.ceil_log(2, 2) == 1 and M.ceil_log(3, 2) == 2 and M.ceil_log(4, 2) == 2 and M.ceil_log(5, 2) == 3
    assert M.ceil_log(27, 3) == 3 and M.ceil_log(28, 3) == 4 and M.ceil_log(8, 2) == 3 and M.ceil_log(9, 2) == 4
    with pytest.raises(ValueError):
        M.ceil_log(0, 2)
    with pytest.raises(ValueError):
        M.ceil_log(5, 1)


def test_ceil_log_is_exact_at_large_powers():
    """Ganzzahlig, kein Gleitkomma: k^t liefert genau t, k^t + 1 liefert t + 1 (math.log würde bei 3^40 schwanken)."""
    for k in (2, 3, 4, 6, 10):
        for t in (5, 20, 40):
            assert M.ceil_log(k**t, k) == t and M.ceil_log(k**t + 1, k) == t + 1


def test_handbeispiel_runs_and_counts(handbeispiel):
    """(2, 4, 6, 1, 3, 5): v + 1 steht vor v bei v = 1 (2 vor 1), v = 3 (4 vor 3), v = 5 (6 vor 5), sonst nicht: R = 4."""
    assert M.rising_runs(handbeispiel) == [[1], [2, 3], [4, 5], [6]]
    assert M.rising_count(handbeispiel) == 4
    assert M.run_labels(handbeispiel) == (1, 2, 3, 0, 1, 2)       # Beschriftung je Wagen: 2 → Folge 1, 4 → 2, 6 → 3, 1 → 0, 3 → 1, 5 → 2
    assert M.min_passes(handbeispiel, 2) == 2 and M.min_passes(handbeispiel, 3) == 2 and M.min_passes(handbeispiel, 4) == 1
    assert M.radix(6, 2) == 3 and M.radix(6, 3) == 2 and M.radix(6, 4) == 2


def test_handbeispiel_plan_by_hand(handbeispiel):
    """Durchgang 1 nach der niedrigen Binärziffer: Gleis A (Beschriftung gerade: Ränge 1, 4, 5) = (4, 1, 5), Gleis B = (2, 6, 3), danach (4, 1, 5, 2, 6, 3);
    Durchgang 2 nach der hohen Ziffer: Gleis A = (1, 2, 3), Gleis B = (4, 5, 6)."""
    pl = M.plan(handbeispiel, 2)
    assert len(pl) == 2
    assert pl[0].tracks == ((4, 1, 5), (2, 6, 3)) and pl[0].after == (4, 1, 5, 2, 6, 3)
    assert pl[1].tracks == ((1, 2, 3), (4, 5, 6)) and pl[1].after == (1, 2, 3, 4, 5, 6)
    assert M.play(handbeispiel, [p.assign for p in pl], 2) == (1, 2, 3, 4, 5, 6)


def test_one_pass_and_play_by_hand():
    assert M.one_pass((3, 1, 2), (1, 0, 0), 2) == (1, 2, 3)            # Gleis 0: 1, 2; Gleis 1: 3
    assert M.one_pass((3, 1, 2), (0, 0, 0), 2) == (3, 1, 2)            # alle auf ein Gleis: nichts ändert sich
    assert M.play((3, 1, 2), [(1, 0, 0)], 2) == (1, 2, 3)
    with pytest.raises(ValueError):
        M.play((3, 1, 2), [(0, 0, 2)], 2)
    with pytest.raises(ValueError):
        M.play((3, 1, 2), [(0, 0)], 2)


def test_forward_one_pass_counts_by_hand(handbeispiel):
    """Alle 2^6 = 64 Zuweisungen sortieren den Zug nicht; mit 4 Gleisen gibt es sortierende Zuweisungen (Handrechnung: sie sind durch die Beschriftung der steigenden Folgen bestimmt)."""
    total, ok = M.forward_one_pass(handbeispiel, 2)
    assert (total, ok) == (64, 0)
    assert M.forward_one_pass(handbeispiel, 3) == (729, 0)
    total4, ok4 = M.forward_one_pass(handbeispiel, 4)
    expected = sum(
        1 for a in itertools.product(range(4), repeat=6)
        if tuple(c for g in range(4) for c, x in zip(handbeispiel, a) if x == g) == (1, 2, 3, 4, 5, 6)
    )
    assert (total4, ok4) == (4096, expected) and expected > 0
    assert M.forward_one_pass((1, 2, 3, 4, 5, 6, 7, 8), 2) is None       # n = 8: über der Grenze
    assert M.forward_one_pass((1, 2, 3, 4, 5, 6, 7), 7) is None          # 7^7 = 823 543 Zuweisungen: über der Grenze


def test_forward_one_pass_counts_the_identity_by_hand():
    """Die Identität (1, 2, 3) mit 2 Gleisen: sortiert wird, wenn Gleis 0 einen Anfang und Gleis 1 den Rest bekommt: 000, 001, 011, 111 → 4 von 8."""
    assert M.forward_one_pass((1, 2, 3), 2) == (8, 4)


def test_labels_make_equal_runs_share_a_label():
    assert M.run_labels((1, 2, 3)) == (0, 0, 0)
    assert M.run_labels((3, 2, 1)) == (2, 1, 0)


def test_parse_train_accepts_and_rejects():
    assert M.parse_train("2, 4, 6, 1, 3, 5") == ((2, 4, 6, 1, 3, 5), None)
    assert M.parse_train("2 1")[0] == (2, 1) and M.parse_train("1;2;3")[0] == (1, 2, 3)
    assert M.parse_train("")[0] is None
    assert M.parse_train("1")[0] is None                                # ein Wagen: kein Zug
    assert "ganze Zahlen" in M.parse_train("1, a")[1]
    assert "genau einmal" in M.parse_train("1, 1, 3")[1]
    assert M.parse_train("1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13")[0] is None
    assert M.parse_train("x" * 100)[0] is None


def test_lds_by_hand():
    assert M.lds_length((2, 4, 6, 1, 3, 5)) == 2
    assert M.lds_length((1, 2, 3)) == 1 and M.lds_length((3, 2, 1)) == 3 and M.lds_length(()) == 0
