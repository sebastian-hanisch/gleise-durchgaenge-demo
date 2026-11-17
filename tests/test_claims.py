"""Claims-Tests: jede Zahl der Befunde B1 bis B14 der README mit ihren Voraussetzungen (DEMO-PLAYBOOK §4, §11a).

Exakt: Ganzzahlen, Brüche, Zählung aller Folgen bzw. Wörter. Zufallsproben (B10 bis B12): ganzzahlige Zähler aus dem SplitMix64, auf jeder Plattform gleich; hier aus der
vorgerechneten Tabelle gelesen, ihre ersten Züge rechnet `tests/test_tables.py` neu. Prozentwerte sind auf die in der README genannten Stellen gerundet.
Jede README-Zahl wird hier gerechnet **und** im README-Text gesucht (`_readme_has`)."""

import itertools
import math
import re
from fractions import Fraction
from pathlib import Path

import pytest

import gdg_constants as C
import gdg_evaluation as ev
import gdg_exact as EX
import gdg_model as M
import gdg_tables as T
import gdg_texts as TX
import gdg_words as W
import oracle_helpers as O

ROOT = Path(__file__).resolve().parent.parent


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace(" ", " ").replace(" ", " ").replace("\\|", "|"))


README = _norm((ROOT / "README.md").read_text(encoding="utf-8"))
TABLES = T.load()


def _readme_has(*items):
    for item in items:
        assert _norm(item) in README, item


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def pc(x, nd=1):
    return de(100 * float(x), nd) + " %"


def th(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def _perms(n):
    return list(itertools.permutations(range(1, n + 1)))


# --- B1 -------------------------------------------------------------------------------------------------------------------------------------

def test_b1_handbeispiel():
    z = (2, 4, 6, 1, 3, 5)
    assert M.rising_runs(z) == [[1], [2, 3], [4, 5], [6]] and M.rising_count(z) == 4
    assert [M.min_passes(z, k) for k in (2, 3, 4)] == [2, 2, 1] and [M.radix(6, k) for k in (2, 3)] == [3, 2]
    pl = M.plan(z, 2)
    assert pl[0].tracks == ((4, 1, 5), (2, 6, 3)) and pl[0].after == (4, 1, 5, 2, 6, 3) and pl[1].after == (1, 2, 3, 4, 5, 6)
    assert M.forward_one_pass(z, 2) == (64, 0) and M.forward_one_pass(z, 3) == (729, 0)
    _readme_has("(2, 4, 6, 1, 3, 5)", "R = 4 steigende Folgen {1}, {2, 3}, {4, 5}, {6}", "mit 2 und mit 3 Gleisen 2 Durchgänge (Radix 3 bzw. 2), mit 4 Gleisen 1 Durchgang",
                "(4, 1, 5 / 2, 6, 3) → (4, 1, 5, 2, 6, 3) → (1, 2, 3, 4, 5, 6)", "keine der 64 Zuweisungen mit 2 Gleisen und keine der 729 mit 3 Gleisen")


# --- B2 -------------------------------------------------------------------------------------------------------------------------------------

B2_CASES = [(n, 2) for n in range(3, 9)] + [(n, 3) for n in range(4, 8)] + [(n, 4) for n in range(5, 8)]


def test_b2_formula_equals_forward_simulation_in_13_cases():
    assert len(B2_CASES) == 13
    for n, k in B2_CASES:
        words = _perms(n)
        levels = O.forward_levels(words, k, lambda w, n=n: w == tuple(range(1, n + 1)))
        assert all(levels[p] == M.min_passes(p, k) for p in words), (n, k)
    stufen = {(6, 2): [1, 57, 604, 58], (8, 2): [1, 247, 19912, 20160], (7, 3): [1, 1311, 3728]}
    for (n, k), expected in stufen.items():
        assert O.levels_list(O.forward_levels(_perms(n), k, lambda w, n=n: w == tuple(range(1, n + 1)))) == expected
    assert Fraction(sum(t * c for t, c in enumerate(stufen[(6, 2)])), 720) == Fraction(1439, 720)
    for n, k in [(4, 2), (5, 2), (6, 2), (4, 3), (5, 3)]:
        assert all(v == M.min_passes(p, k) for p, v in O.backward_levels(n, k).items())
    _readme_has("in 13 Fällen (k = 2: n = 3 bis 8; k = 3: n = 4 bis 7; k = 4: n = 5 bis 7), 0 Abweichungen", "n = 6, k = 2: 1, 57, 604, 58 (Mittel 1439/720)",
                "n = 8, k = 2: 1, 247, 19 912, 20 160", "n = 7, k = 3: 1, 1 311, 3 728", "bis n = 6 (k = 2) und n = 5 (k = 3)")


# --- B3 -------------------------------------------------------------------------------------------------------------------------------------

def test_b3_eulerian_numbers_and_mean():
    for n in range(4, 9):
        hist = EX.enumerate_rising_histogram(n)
        assert hist == list(EX.eulerian_row(n))
        assert Fraction(sum(r * c for r, c in enumerate(hist, start=1)), math.factorial(n)) == Fraction(n + 1, 2)
    for n in (10, 20, 50, 100, 200, 500):
        row = EX.eulerian_row(n)
        assert Fraction(sum((d + 1) * a for d, a in enumerate(row)), sum(row)) == Fraction(n + 1, 2)
    _readme_has("Aufzählung n = 4 bis 8, n = 9 im langsamen Test", "Mittel von R exakt (n + 1)/2 für n = 10, 20, 50, 100, 200 und 500")


# --- B4 -------------------------------------------------------------------------------------------------------------------------------------

def test_b4_distribution_n10_k2():
    s = EX.summary(10, 2)
    assert s.radix == 4 and s.counts == {0: 1, 1: 1013, 2: 503032, 3: 3123740, 4: 1014} and s.total == 3628800
    assert de(float(s.mean), 3) == "2,861" and pc(Fraction(1014, 3628800), 2) == "0,03 %" and s.share_below > Fraction(9995, 10000)
    _readme_has("n = 10, k = 2: Radix 4, mittlere Zahl Durchgänge 2,861", "1 Folge braucht 0, 1 013 brauchen 1, 503 032 brauchen 2, 3 123 740 brauchen 3 und 1 014 brauchen 4 Durchgänge (0,03 % der 3 628 800 Folgen)",
                "mehr als 99,95 % der Folgen brauchen weniger als Radix", "2,861 Durchgänge gegen Radix 4", "nur 1 014 von 3 628 800 Folgen brauchen 4")


# --- B5 -------------------------------------------------------------------------------------------------------------------------------------

def test_b5_worst_case_is_radix_in_1791_pairs():
    pairs = 0
    for k in range(2, 11):
        for n in range(2, 201):
            s = EX.summary(n, k)
            assert max(s.counts) == M.radix(n, k) and s.counts[M.radix(n, k)] > 0
            pairs += 1
    assert pairs == 1791
    _readme_has("in allen 1 791 Paaren n = 2 bis 200, k = 2 bis 10")


# --- B6, B7, B8 -----------------------------------------------------------------------------------------------------------------------------

def test_b6_share_below_radix():
    share = {(n, k): EX.summary(n, k).share_below for n, k in [(10, 4), (10, 6), (20, 3), (27, 3), (40, 4), (64, 2)]}
    assert [pc(share[key], 2) for key in [(10, 4), (10, 6), (20, 3), (27, 3), (40, 4)]] == ["13,89 %", "86,11 %", "22,07 %", "0,12 %", "1,40 %"]
    assert share[(64, 2)] == Fraction(1, 2)
    s = EX.summary(10, 3)
    assert s.at_radix == 1 and s.radix == 3
    _readme_has("n = 10, k = 4: 13,89 %", "n = 10, k = 6: 86,11 %", "n = 20, k = 3: 22,07 %", "n = 27, k = 3: 0,12 %", "n = 40, k = 4: 1,40 %", "n = 64, k = 2: 50 %",
                "n = 10, k = 3: alle bis auf genau 1 Folge", "k = 3: 0,12 % bei n = 27")


def test_b7_half_at_powers_of_two():
    for n in (4, 8, 16, 32, 64, 128):
        assert EX.summary(n, 2).share_below == Fraction(1, 2)
        assert EX.eulerian_row(n) == EX.eulerian_row(n)[::-1]
    assert EX.summary(9, 2).share_below == Fraction(362879, 362880)
    _readme_has("genau 1/2 bei n = 4, 8, 16, 32, 64, 128", "bei n = 9: 362 879/362 880", "genau 1/2 bei n = 2^r (geprüft für n = 4 bis 128)")


def test_b8_sawtooth():
    stats = EX.sawtooth_stats()
    assert {k: len(v["zeros"]) for k, v in stats.items()} == {2: 0, 3: 15, 4: 62, 6: 121, 10: 68} and all(v["count"] == 181 for v in stats.values())
    assert (stats[2]["min"], stats[2]["min_n"], stats[2]["max"], stats[2]["max_n"]) == (0.5, 32, 1.0, 33)
    saw = EX.sawtooth()
    assert [de(saw[3][n][0], 4) for n in (9, 27)] == ["0,0416", "0,0012"] and saw[3][81][0] < 1e-4 and de(saw[4][16][0], 4) == "0,0002"
    _readme_has("k = 2: Anteil unter Radix zwischen 0,5 (n = 32) und 1,0 (n = 33), in 0 von 181 Werten unter 0,00005", "k = 3: 15, k = 4: 62, k = 6: 121, k = 10: 68 von 181 Werten unter 0,00005",
                "n = 9, 27, 81 und k = 3: 0,0416, 0,0012 und weniger als 0,0001", "n = 16 und k = 4: 0,0002", "121 von 181 Werten von n zwischen 20 und 200")


# --- B9 -------------------------------------------------------------------------------------------------------------------------------------

def test_b9_gleise_against_free():
    cells = {(n, k): T.parallel_row(TABLES, n, k) for n in C.TABLE_N for k in (2, 3)}
    assert [(cells[(n, 3)]["gleise"], cells[(n, 3)]["frei"]) for n in (5, 6, 9)] == [(93, 103), (360, 513), (15111, 94359)]
    assert all(cells[(n, 2)]["gleise"] == 2**n - n for n in C.TABLE_N)
    assert [cells[(n, 2)]["frei"] for n in C.TABLE_N] == [5, 14, 42, 132, 429, 1430, 4862]
    assert (cells[(4, 2)]["gleise"], cells[(4, 2)]["frei"], cells[(9, 2)]["gleise"], cells[(9, 2)]["frei"]) == (12, 14, 503, 4862)
    _readme_has("k = 3: Gleise hintereinander / frei ausgelesen: n = 5: 93 gegen 103; n = 6: 360 gegen 513; n = 9: 15 111 gegen 94 359",
                "k = 2: Gleise 2^n − n (n = 3 bis 9), frei die Catalan-Zahlen (n = 4: 12 gegen 14; n = 9: 503 gegen 4 862)", "A005802: 6, 23, 103, 513, 2 761, 15 767, 94 359")


# --- B10 ------------------------------------------------------------------------------------------------------------------------------------

def _mv(n, d, k):
    cell = next(c for c in TABLES["modell_v"] if c["n"] == n and c["d"] == d)
    assert cell["trials"] == 4000
    return T.passes_from_r_hist(cell["r_hist"], k)


def test_b10_model_v():
    assert [de(_mv(20, d, 2)["mean"]) for d in ("1", "16", "gleichverteilt")] == ["2,40", "3,80", "3,94"] and M.radix(20, 2) == 5
    assert de(float(EX.summary(20, 2).mean), 3) == "3,939"
    assert [de(_mv(40, d, 2)["mean"]) for d in ("0.5", "gleichverteilt")] == ["2,01", "4,98"] and M.radix(40, 2) == 6
    assert [de(_mv(20, d, 2)["mean_r"]) for d in ("1", "gleichverteilt")] == ["4,46", "10,53"]
    for n in (10, 20, 40):
        means = [_mv(n, d, 2)["mean_r"] for d in T.MODEL_V_D]
        assert means == sorted(means)
    assert [de(_mv(20, d, 4)["mean"]) for d in ("4", "16", "gleichverteilt")] == ["2,00", "2,00", "2,00"] and M.radix(20, 4) == 3
    assert de(_mv(40, "gleichverteilt", 4)["mean"]) == "2,98" and M.radix(40, 4) == 3
    _readme_has("n = 20 (Radix 5): D = 1: 2,40, D = 16: 3,80, gleichverteilt 3,94 (exakt 3,939)", "n = 40 (Radix 6): D = 0,5: 2,01, gleichverteilt 4,98",
                "Mittel von R bei n = 20: 4,46 (D = 1) und 10,53 (gleichverteilt, exakt 10,5)", "in allen drei Zeilen n = 10, 20, 40",
                "n = 20 braucht ab D = 4 im Mittel 2,00 gegen Radix 3, n = 40 gleichverteilt 2,98 gegen Radix 3")
    assert EX.summary(20, 2).radix == 5 and Fraction(21, 2) == Fraction(20 + 1, 2)


# --- B11, B12 -------------------------------------------------------------------------------------------------------------------------------

def _group(m, k, n):
    return next(c for c in TABLES["gruppen"] if (c["m"], c["k"], c["n"]) == (m, k, n))


def test_b11_groups_table():
    ns = (8, 12, 20, 30, 40)
    cells = [_group(6, 3, n) for n in ns]
    assert all(c["trials"] == 3000 for c in cells)
    free = [pc(c["counts"]["free_lt_present"] / 3000) for c in cells]
    fixed = [pc(c["counts"]["fixed_lt_present"] / 3000) for c in cells]
    assert free == ["93,8 %", "98,7 %", "35,3 %", "0,7 %", "0,0 %"] and fixed == ["56,5 %", "23,4 %", "0,7 %", "0,0 %", "0,0 %"]
    assert [c["counts"]["free_lt_all"] for c in cells[:2]] == [3000, 2974]
    _readme_has("93,8 / 98,7 / 35,3 / 0,7 / 0,0 % der Züge mit 8 / 12 / 20 / 30 / 40 Wagen", "56,5 / 23,4 / 0,7 / 0,0 / 0,0 %", "93,8 / 98,7 / 35,3 / 0,7 / 0,0 % (B11, 3 000 Züge)",
                "bei 8 Wagen 100,0 % (3 000 von 3 000 Zügen) und bei 12 Wagen 99,1 %",
                "95 / 100 / 30 / 0 / 0 %", "6 Gruppen, 3 Gleise: 93,8 % der Züge mit 8 Wagen, 0,0 % bei 40 Wagen", "bei 30 Wagen 0,7 % und bei 40 Wagen 0,0 %; nicht überall: bei 8 Gruppen, 6 Gleisen und 40 Wagen in 60 von 60 Zügen noch",
                "6 Gruppen, 3 Gleise: 0,7 % bei 30, 0,0 % bei 40 Wagen", "Gruppen bei 8 Wagen 93,8 % statt 92,3 % (3 000 Züge)", "Modell V bei n = 40, k = 2, D = 0,5: 2,01 statt 1,97")
    assert de(2974 / 3000 * 100, 1) == "99,1"


@pytest.mark.slow
def test_b11_stability():
    """Mit 15 000 Zügen und zwei anderen Zufalls-Seeds (999, 1234): 92,9 % und 93,0 % frei, 57,3 % und 57,5 % fest bei 6 Gruppen, 3 Gleisen, 8 Wagen."""
    got = []
    for seed in (999, 1234):
        c = T.group_counts(6, 3, 8, 15000, seed)
        got.append((pc(c["free_lt_present"] / 15000), pc(c["fixed_lt_present"] / 15000)))
    assert got == [("92,9 %", "57,3 %"), ("93,0 %", "57,5 %")]
    _readme_has("bei 8 Wagen 92,9 % und 93,0 % frei, 57,3 % und 57,5 % fest", "92,9 % und 93,0 %")


def test_b12_groups_with_eight_groups():
    k4, k6, k2 = _group(8, 4, 40), _group(8, 6, 40), _group(8, 2, 40)
    assert all(c["trials"] == 60 for c in (k4, k6, k2))
    assert k4["counts"]["free_lt_present"] == 0 and k4["counts"]["sum_free"] == k4["counts"]["sum_radix_present"] == 120            # gleich Radix 2 in allen Zügen
    assert k6["counts"]["free_lt_present"] == 60 and k6["counts"]["sum_free"] == 60 and k6["counts"]["sum_radix_present"] == 120   # exakt 1 gegen Radix 2
    assert k2["counts"]["free_lt_present"] == 0 and k2["counts"]["sum_free"] == k2["counts"]["sum_radix_present"] == 180           # gleich Radix 3
    _readme_has("k = 4: gleich Radix in 60 von 60 Zügen", "k = 6: exakt 1 gegen Radix 2 in 60 von 60", "k = 2: gleich Radix 3 in 60 von 60")


# --- B13 ------------------------------------------------------------------------------------------------------------------------------------

def test_b13_groups_hand_values():
    w = (2, 1, 2, 1, 3, 3)
    assert W.label_count(w) == 2 and W.passes_fixed(w, 2) == 1 and W.radix_present(w, 2) == 2
    rev = (3, 3, 2, 2, 1, 1)
    assert W.passes_fixed(rev, 2) == 2 and W.passes_free(rev, 3, 2)[0] == 0
    words = O.multiset_words((2, 2, 2))
    goal = (1, 1, 2, 2, 3, 3)
    assert O.levels_list(O.forward_levels(words, 2, lambda x: x == goal)) == [1, 42, 47]
    assert O.levels_list(O.forward_levels(words, 2, O.is_grouped)) == [6, 84]
    _readme_has("in 11 von 11 geprüften Fällen (Mehrfachmenge und k, n ≤ 8)", "in 8 von 8", "(2, 2, 2), k = 2: fest 1, 42, 47 Wörter mit 0, 1, 2 Durchgängen, frei 6 und 84",
                "Zug (2, 1, 2, 1, 3, 3), k = 2: L = 2, 1 Durchgang, Radix 2", "Zug (3, 3, 2, 2, 1, 1), k = 2: fest 2 Durchgänge, frei 0", "11 + 8 Fälle")


def test_readme_names_the_seed_formulas_of_the_tables():
    """B10 bis B12: die in der README genannten Zufalls-Seeds sind die des Codes."""
    assert T.model_v_seed(20, "1") == 4_600_000 + 1000 * 20 + 1 and T.model_v_seed(10, "0.5") == 4_600_000 + 1000 * 10 + 0
    assert T.model_v_seed(40, "gleichverteilt") == 4_600_000 + 1000 * 40 + 7
    assert T.group_seed(6, 3, 8) == 4_100_000 + 1000 * 6 + 100 * 3 + 8
    assert all(c["seed"] == T.group_seed(c["m"], c["k"], c["n"]) for c in TABLES["gruppen"])
    _readme_has("4 600 000 + 1 000 · n + Index von D", "4 100 000 + 1 000 · m + 100 · k + n", "Zufalls-Seeds 999 und 1 234")


def test_b13_case_counts_are_those_of_the_oracle_file():
    import test_oracle_gleise_durchgaenge as O2
    assert len(O2.FIXED_CASES) + len(O2.FIXED_SLOW) == 11 and len(O2.FREE_CASES) + 1 == 8


# --- B14 ------------------------------------------------------------------------------------------------------------------------------------

def test_b14_label_count_and_lds():
    for n in range(2, 7):
        assert all(W.label_count(p) == M.rising_count(p) for p in _perms(n))
    for n in range(1, 8):
        assert all(M.lds_length(p) <= M.rising_count(p) for p in _perms(n))
    _readme_has("L ist gleich R für alle Folgen n ≤ 6", "längste fallende Teilfolge ist höchstens R für alle Folgen n ≤ 7")


# --- Text und Struktur ----------------------------------------------------------------------------------------------------------------------

def test_assumptions_table_is_the_same_in_app_and_readme():
    assert _norm(TX.ASSUMPTIONS_MARKDOWN.strip()) in README


def test_readme_names_the_model_as_made_up_and_has_no_planning_words():
    assert "Das Ankunftsmodell ist ausgedacht" in README and "keine reale Ankunftsfolge" in README
    body = README.split("Diese Demo ist Teil des Portfolios", 1)[0]
    for wort in ("Stück", "Linie", "Vormessung", "Phase 0", "sm_v", "Plan Z", " V1", "V14", "trägt", "tragen", "Saatwert", "läuft lokal"):
        assert wort not in body, wort


def test_readme_does_not_call_the_website_integration_open():
    assert "Einbindung" not in README and "noch nicht eingebunden" not in README
