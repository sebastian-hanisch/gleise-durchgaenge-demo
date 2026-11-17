"""Die vorgerechneten Tabellen (data/gdg_tables.json): Aufbau, bekannte Folgen, Neuberechnung der ersten Züge. Die volle Neuberechnung ist `tools/gdg_make_tables.py --check`
(etwa 1,5 Minuten); hier läuft sie als langsamer Test (GDG_SLOW=1)."""

import json
from fractions import Fraction

import pytest

import gdg_constants as C
import gdg_exact as EX
import gdg_tables as T


@pytest.fixture(scope="module")
def tables():
    return T.load()


def test_structure(tables):
    assert tables["version"] == 1
    assert sorted(int(n) for n in tables["parallel"]) == list(C.TABLE_N)
    assert [(c["m"], c["k"], c["n"], c["trials"]) for c in tables["gruppen"]] == [(m, k, n, t) for m, k, n, t in T.GROUP_CELLS]
    assert [(c["n"], c["d"]) for c in tables["modell_v"]] == [(n, d) for n in T.MODEL_V_N for d in T.MODEL_V_D]
    assert all(c["trials"] == C.MODEL_V_TRIALS and sum(c["r_hist"]) == C.MODEL_V_TRIALS for c in tables["modell_v"])


def test_parallel_rows_equal_known_sequences(tables):
    """Frei, k = 2: Catalan-Zahlen; frei, k = 3: 6, 23, 103, 513, 2761, 15767, 94359 (n = 3 bis 9; stimmt mit OEIS A005802 nach Quellenbericht überein); Gleise: 2^n − n für k = 2."""
    catalan = [5, 14, 42, 132, 429, 1430, 4862]
    three = [6, 23, 103, 513, 2761, 15767, 94359]
    for i, n in enumerate(C.TABLE_N):
        assert T.parallel_row(tables, n, 2)["frei"] == catalan[i]
        assert T.parallel_row(tables, n, 3)["frei"] == three[i]
        assert T.parallel_row(tables, n, 2)["gleise"] == 2**n - n
        assert T.parallel_row(tables, n, 3)["gleise"] == sum(EX.eulerian_row(n)[:3])
        assert T.parallel_row(tables, n, 2)["total"] == __import__("math").factorial(n)


def test_parallel_known_cells(tables):
    """n = 5, k = 3: 93 gegen 103; n = 6, k = 3: 360 gegen 513; n = 9, k = 3: 15 111 gegen 94 359."""
    assert (T.parallel_row(tables, 5, 3)["gleise"], T.parallel_row(tables, 5, 3)["frei"]) == (93, 103)
    assert (T.parallel_row(tables, 6, 3)["gleise"], T.parallel_row(tables, 6, 3)["frei"]) == (360, 513)
    assert (T.parallel_row(tables, 9, 3)["gleise"], T.parallel_row(tables, 9, 3)["frei"]) == (15111, 94359)


def test_parallel_histograms_are_recomputed_up_to_n8(tables):
    for n in range(3, 9):
        assert tables["parallel"][str(n)]["lds_hist"] == EX.lds_histogram(n)


@pytest.mark.parametrize("index", range(9))
def test_group_cell_prefix_is_reproduced(tables, index):
    """Die ersten 100 Züge jeder Zelle (m <= 6) neu gerechnet: genau die gespeicherten Zähler (SplitMix64 und Ganzzahlen, auf jeder Plattform gleich)."""
    c = tables["gruppen"][index]
    assert c["m"] <= 6 and c["prefix_trials"] == C.GROUP_PREFIX_TRIALS
    assert T.group_counts(c["m"], c["k"], c["n"], c["prefix_trials"], c["seed"]) == c["prefix_counts"]


def test_model_v_prefix_is_reproduced(tables):
    for c in tables["modell_v"]:
        trains = T.AR.model_v_trains(c["n"], T.dwell_of(c["d"]), c["prefix_trials"], c["seed"])
        assert T.r_histogram(trains, c["n"]) == c["prefix_r_hist"]


def test_counters_are_consistent(tables):
    for c in tables["gruppen"]:
        cc = c["counts"]
        assert 0 <= cc["free_lt_present"] <= c["trials"] and 0 <= cc["fixed_lt_present"] <= c["trials"]
        assert cc["fixed_lt_present"] <= cc["free_lt_present"]                       # frei ist nie schlechter als fest (je Zug)
        assert cc["sum_free"] <= cc["sum_fixed"]


def test_passes_from_r_hist_by_hand():
    """Histogramm von R für n = 4 (R = 1..4): 1, 11, 11, 1 Folgen (die Eulerschen Zahlen); k = 2: Durchgänge 0, 1, 2, 2 → Mittel (11 + 22 + 2)/24 = 35/24."""
    s = T.passes_from_r_hist([1, 11, 11, 1], 2)
    assert s["mean"] == pytest.approx(35 / 24) and s["total"] == 24 and s["radix"] == 2
    assert s["one_or_less"] == pytest.approx(12 / 24) and s["below_radix"] == pytest.approx(12 / 24)
    assert s["mean_r"] == pytest.approx(2.5)


def test_json_is_plain_text_with_unix_newlines():
    raw = T.DATA_PATH.read_bytes()
    assert b"\r\n" not in raw and json.loads(raw)["version"] == 1


@pytest.mark.slow
def test_full_recomputation_equals_the_file(tables):
    assert json.loads(json.dumps(T.make_all())) == tables
