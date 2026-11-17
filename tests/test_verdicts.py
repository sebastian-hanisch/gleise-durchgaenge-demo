"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

from fractions import Fraction

import gdg_constants as C
import gdg_evaluation as ev
import gdg_exact as EX


def _train(**kw):
    base = dict(error=None, train=(2, 4, 6, 1, 3, 5), k=2, runs=((1,), (2, 3), (4, 5), (6,)), r=4, passes=2, radix=3, plan=(), final=(1, 2, 3, 4, 5, 6),
                sorted_ok=True, forward=(64, 0), passes_by_k={2: 2, 3: 2, 4: 1, 5: 1, 6: 1})
    base.update(kw)
    return ev.OneTrain(**base)


def test_format_helpers():
    assert ev.de(2.8611, 3) == "2,861" and ev.thousands(3628800) == "3 628 800"
    assert ev.pct(0) == "0 %" and ev.pct(1) == "100 %" and ev.pct(Fraction(1, 2)) == "50,00 %"
    assert ev.pct(1e-9) == "weniger als 0,01 %" and ev.pct(1 - 1e-9) == "mehr als 99,99 %"
    assert ev.pct1(Fraction(1, 3)) == "33,3 %"
    assert ev.train_text((2, 1)) == "(2, 1)" and ev.runs_text([[1], [2, 3]]) == "{1}, {2, 3}"


def test_verdict_train_handbeispiel_names_all_numbers():
    kind, text = ev.verdict_train(_train())
    assert kind == "success"                                                        # 2 Durchgänge < Radix 3
    assert "R = 4" in text and "2 Durchgänge" in text and "Radix: 3" in text and "{2, 3}" in text
    assert "alle 64 Zuweisungen findet keine" in text and "(R > k)" in text
    assert "2 Gleise: 2, 3 Gleise: 2, 4 Gleise: 1" in text


def test_verdict_train_one_pass_names_the_found_assignments():
    kind, text = ev.verdict_train(_train(k=4, passes=1, radix=2, forward=(4096, 5)))
    assert kind == "success" and "findet 5, die ihn in einem Durchgang sortieren" in text


def test_verdict_train_equal_to_radix_is_info_and_sorted_train_has_no_pass():
    kind, text = ev.verdict_train(_train(train=(3, 2, 1), r=3, passes=2, radix=2, runs=((1,), (2,), (3,)), forward=None, passes_by_k={2: 2}))
    assert kind == "info" and "Radix: 2" in text
    kind, text = ev.verdict_train(_train(train=(1, 2, 3), r=1, passes=0, radix=2))
    assert kind == "info" and "schon sortiert" in text and "0 Durchgänge" in text


def test_verdict_train_error_is_a_warning():
    kind, text = ev.verdict_train(ev.analyse_train("1, 1", 2))
    assert kind == "warning" and "genau einmal" in text


def test_analyse_train_handbeispiel_end_to_end():
    a = ev.analyse_train(C.E1_DEFAULT_TEXT, 2)
    assert (a.r, a.passes, a.radix, a.sorted_ok, a.forward) == (4, 2, 3, True, (64, 0))
    assert a.final == (1, 2, 3, 4, 5, 6) and len(a.plan) == 2


def test_verdict_distribution_n10_k2():
    kind, text = ev.verdict_distribution(ev.analyse_distribution(10, 2))
    assert kind == "info"
    assert "n = 10, k = 2" in text and "Radix 4" in text and "**2,861 Durchgänge**" in text
    assert "1 014 von 3 628 800 Folgen (0,03 %) brauchen 4" in text
    assert "3 123 740 brauchen 3" in text
    assert "Weniger als Radix brauchen 99,97 % der Folgen" in text
    assert "bestätigt" not in text and "WIDERSPRICHT" not in text                      # n > 8: keine Aufzählung


def test_verdict_distribution_n8_names_the_enumeration():
    kind, text = ev.verdict_distribution(ev.analyse_distribution(8, 2))
    assert "Die Aufzählung aller 40 320 Folgen bestätigt die Eulerschen Zahlen." in text
    assert "Weniger als Radix brauchen 50,00 % der Folgen" in text


def test_verdict_distribution_radix_exact_is_a_warning():
    kind, text = ev.verdict_distribution(ev.analyse_distribution(27, 3))
    assert kind == "warning" and "fast alle Folgen genau richtig" in text and "0,12 %" in text


def test_verdict_distribution_large_n_names_no_count():
    kind, text = ev.verdict_distribution(ev.analyse_distribution(300, 2))
    assert " von " not in text and "der n! Folgen brauchen 9" in text           # n! hat mehr als 15 Stellen: nur Anteile, keine Ganzzahlen


def test_verdict_sawtooth_k3_names_the_counts():
    kind, text = ev.verdict_sawtooth(ev.analyse_sawtooth(3))
    assert kind == "warning"
    assert "in 15 von 181 Werten" in text and "n = 81" in text and "n = 28" in text and "n = 27 (0,0012)" in text
    kind2, text2 = ev.verdict_sawtooth(ev.analyse_sawtooth(2))
    assert kind2 == "info" and "in 0 von 181 Werten" in text2 and "n = 32" in text2 and "0,5000" in text2


def _model(**kw):
    base = dict(n=20, k=2, d="1", trials=4000, radix=5, mean_passes=2.42, one_or_less=0.07, below_radix=1.0, mean_r=4.5, r_hist=(1,), example=(1, 2),
                uniform_exact_mean=3.94, uniform_exact_mean_r=10.5, uniform_sample_mean=3.9)
    base.update(kw)
    return ev.ModelV(**base)


def test_verdict_model_v_names_numbers_and_threshold():
    kind, text = ev.verdict_model_v(_model())
    assert kind == "success"
    assert "n = 20, k = 2, Radix 5" in text and "D = 1" in text and "**2,42 Durchgänge**" in text and "Mittel von R: 4,5" in text
    assert "7,0 % der Folgen mit höchstens einem Durchgang" in text and "100,0 % unter Radix" in text and "4 000 Folgen" in text
    assert "gleichverteilt exakt: 3,94 Durchgänge, Mittel von R 10,5" in text
    assert ev.verdict_model_v(_model(mean_passes=4.5))[0] == "success" and ev.verdict_model_v(_model(mean_passes=4.6))[0] == "info"      # Schwelle: Mittel + 0,5 <= Radix
    assert "gleichverteilt (jede Folge gleich wahrscheinlich)" in ev.verdict_model_v(_model(d="gleichverteilt"))[1]
    assert "D = 0,5" in ev.verdict_model_v(_model(d="0.5"))[1]


def _group(**kw):
    base = dict(m=6, n=8, k=3, trials=3000, asked_trials=3000, seed=29, free_lt_present=2813, fixed_lt_present=1694, mean_radix=1.937, mean_fixed=1.371, mean_free=0.965)
    base.update(kw)
    return ev.GroupStats(**base)


def test_verdict_groups_names_numbers_and_threshold():
    kind, text = ev.verdict_groups(_group())
    assert kind == "success"
    assert "6 Gruppen, 3 Gleise, 8 Wagen (3 000 Züge" in text and "Zufalls-Seed 29" in text
    assert "freier** Reihenfolge unterbietet die exakte Mindestzahl Radix (aus den vorhandenen Gruppen) in 93,8 %" in text
    assert "fester** Reihenfolge (Sortieren) in 56,5 %" in text
    assert "Radix 1,94, fest 1,37, frei 0,96" in text
    assert ev.verdict_groups(_group(free_lt_present=1500))[0] == "info" and ev.verdict_groups(_group(free_lt_present=1501))[0] == "success"   # mehr als die Hälfte
    assert "höchstens 150 Züge" in ev.verdict_groups(_group(trials=150, asked_trials=300, m=7))[1]
    assert "höchstens" not in ev.verdict_groups(_group())[1]


def test_verdict_word_reversed_groups_sortieren_gegen_gruppieren():
    ex = ev.analyse_word((3, 3, 2, 2, 1, 1), 3, 2, C.E5_ORDER_FIXED, "eingetragen")
    kind, text = ev.verdict_word(ex)
    assert kind == "info" and ex.goal_ok
    assert "(3, 3, 2, 2, 1, 1)" in text and "fester** Reihenfolge der Gruppen 2 Durchgänge" in text and "freier** Reihenfolge 0" in text and "Radix aus den vorhandenen Gruppen: 2" in text
    ex_free = ev.analyse_word((3, 3, 2, 2, 1, 1), 3, 2, C.E5_ORDER_FREE, "eingetragen")
    assert ex_free.goal_ok and len(ex_free.plan) == 0 and "(frei, 0 Durchgänge)" in ev.verdict_word(ex_free)[1]


def test_parse_word():
    assert ev.parse_word("3, 3, 2, 2, 1, 1") == ((3, 3, 2, 2, 1, 1), None)
    assert ev.parse_word("1")[0] is None and ev.parse_word("1, 9")[0] is None and ev.parse_word("0, 1")[0] is None and ev.parse_word("a, 1")[0] is None
    assert ev.parse_word("1, 2" + ", 1" * 40)[0] is None


def test_kernfrage_texts():
    q1, q2, q3 = ev.kernfrage_texts(_train(), ev.analyse_distribution(10, 2), _group())
    assert q1 == "2 Durchgänge bei R = 4" and q2 == "Mittel 2,861 gegen Radix 4" and q3 == "93,8 % unter Radix (frei)"
    assert ev.kernfrage_texts(ev.analyse_train("", 2), ev.analyse_distribution(10, 2), _group())[0] == "–"


def test_summary_object_is_consistent_with_verdict_inputs():
    s = EX.summary(10, 2)
    assert s.at_radix == 1014 and s.counts[3] == 3123740
