"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, paarweise verschieden; je Preset die erwartete Verdikt-Zeile (DEMO-PLAYBOOK §11a Punkt 7)."""

import pytest

import gdg_arrival as AR
import gdg_constants as C
import gdg_evaluation as ev
import gdg_model as M
import gdg_presets as P


def settings_of(name: str) -> ev.Settings:
    return ev.Settings(**C.PRESETS[name])


def state_of(name: str) -> dict:
    """Vollständiger Zustand aller Regler, wenn das Preset angewendet ist (nicht genannte Regler stehen auf dem Standardwert)."""
    key_of = {state_key: key for key, state_key in P.PRESET_KEYS.items()}
    return {sk: C.PRESETS[name].get(key_of[sk], spec.default) for sk, spec in P.SETTING_SPECS.items()}


def test_every_preset_has_help_and_only_known_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP) and len(C.PRESETS) == 10
    for name, preset in C.PRESETS.items():
        assert set(preset) <= set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_keys_are_the_fields_of_settings_and_setting_specs_cover_them():
    assert set(P.PRESET_KEYS) == set(ev.Settings.__dataclass_fields__)
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_preset_values_are_inside_the_slider_bounds_or_options():
    for name in C.PRESETS:
        for sk, value in state_of(name).items():
            spec = P.SETTING_SPECS[sk]
            if spec.options is not None:
                assert value in spec.options, (name, sk)
            elif spec.lo is not None:
                assert spec.lo <= value <= spec.hi, (name, sk)


def test_default_preset_equals_the_default_settings():
    assert state_of(C.STANDARD_PRESET) == {sk: spec.default for sk, spec in P.SETTING_SPECS.items()}
    assert next(iter(C.PRESETS)) == C.STANDARD_PRESET and settings_of(C.STANDARD_PRESET) == ev.Settings()


def test_presets_are_pairwise_distinct_states():
    """Sonst könnte die Hervorhebung nie das zweite von zwei gleichen Presets markieren."""
    states = [tuple(sorted(state_of(name).items())) for name in C.PRESETS]
    assert len(set(states)) == len(states)


def test_clamp_setting_limits_values_and_rejects_unknown_options():
    assert P.clamp_setting("e2_n", 10**9) == C.E2_N_MAX and P.clamp_setting("e2_n", -5) == C.E2_N_MIN
    assert P.clamp_setting("e3_k", 5) == C.E3_DEFAULT_K and P.clamp_setting("e3_k", 6) == 6
    assert P.clamp_setting("e4_d", "7") == C.E4_DEFAULT_D and P.clamp_setting("e4_d", "16") == "16"
    assert P.clamp_setting("e5_order", "egal") == C.E5_DEFAULT_ORDER
    assert len(P.clamp_setting("e1_text", "1, " * 100)) == C.E1_TEXT_MAX_LEN


def test_random_train_preset_text_is_the_shuffle_of_its_seed():
    s = settings_of("Zufallszug n = 10, 2 Gleise")
    p, error = M.parse_train(s.text)
    assert error is None and p == AR.random_train(10, s.seed1) and s.n1 == 10


# ---------------------------------------------------------------- je Preset die erwartete Verdikt-Zeile


def test_handbeispiel_preset_verdict():
    s = settings_of("Handbeispiel (2, 4, 6, 1, 3, 5), 2 Gleise")
    kind, text = ev.verdict_train(ev.analyse_train(s.text, s.k1))
    assert kind == "success" and "R = 4" in text and "2 Durchgänge" in text and "Radix: 3" in text and "findet keine" in text


def test_reversal_preset_verdict_radix_is_sharp():
    s = settings_of("Umkehrfolge n = 8: Radix ist scharf")
    kind, text = ev.verdict_train(ev.analyse_train(s.text, s.k1))
    assert kind == "info" and "R = 8" in text and "3 Durchgänge" in text and "Radix: 3" in text         # gleich Radix: kein Vorsprung gemeldet


def test_random_train_preset_verdict_names_its_train_and_r():
    s = settings_of("Zufallszug n = 10, 2 Gleise")
    p = AR.random_train(10, s.seed1)
    pos = {v: i for i, v in enumerate(p)}
    r = 1 + sum(1 for v in range(1, 10) if pos[v + 1] < pos[v])
    kind, text = ev.verdict_train(ev.analyse_train(s.text, s.k1))
    assert ev.train_text(p) in text and f"R = {r}" in text and "Radix: 4" in text


def test_radix_too_high_preset_verdict():
    s = settings_of("Radix zu hoch: n = 10, 2 Gleise")
    kind, text = ev.verdict_distribution(ev.analyse_distribution(s.n2, s.k2))
    assert kind == "info" and "Radix 4" in text and "Weniger als Radix brauchen 99,97 %" in text


def test_radix_fits_preset_verdicts():
    s = settings_of("Radix passt: n = 27, 3 Gleise")
    kind, text = ev.verdict_distribution(ev.analyse_distribution(s.n2, s.k2))
    assert kind == "warning" and "Radix 3" in text and "fast alle Folgen genau richtig" in text
    kind3, text3 = ev.verdict_sawtooth(ev.analyse_sawtooth(s.k3))
    assert "n = 27 (0,0012)" in text3


def test_model_v_presets_verdicts():
    near = settings_of("Fast sortiert (D = 1)")
    a = ev.analyse_model_v(near.d4, near.n4, near.k4, near.trials4, near.seed4)
    kind, text = ev.verdict_model_v(a)
    assert kind == "success" and "D = 1" in text and a.mean_passes < 3 and a.mean_r < 6
    uni = settings_of("Gleichverteilt (D = ∞)")
    b = ev.analyse_model_v(uni.d4, uni.n4, uni.k4, uni.trials4, uni.seed4)
    assert "gleichverteilt (jede Folge" in ev.verdict_model_v(b)[1]
    assert abs(b.mean_passes - 3.9391) < 0.15 and abs(b.uniform_exact_mean - 3.9391) < 5e-4       # Band: 4 Standardfehler bei 500 Folgen; exakt 3,939


def test_group_presets_verdicts():
    small = settings_of("Gruppen: 6 Gruppen, 3 Gleise, 8 Wagen")
    g = ev.analyse_groups(small.m5, small.n5, small.k5, small.trials5, small.seed5)
    assert g.free_lt_present / g.trials > 0.80 and g.free_lt_present >= g.fixed_lt_present      # gemessen 93,8 % bei 3000 Zügen
    big = settings_of("Gruppen: 40 Wagen")
    g40 = ev.analyse_groups(big.m5, big.n5, big.k5, big.trials5, big.seed5)
    assert g40.free_lt_present == 0                                                            # gemessen 0 von 3000
    kind, text = ev.verdict_groups(g40)
    assert kind == "info"


def test_sort_versus_group_preset_verdict():
    s = settings_of("Sortieren ≠ Gruppieren")
    word, error = ev.parse_word(s.text5)
    assert error is None and word == (3, 3, 2, 2, 1, 1)
    ex = ev.analyse_word(word, max(word), s.k5, s.order5, "eingetragen")
    assert (ex.passes_fixed, ex.passes_free, ex.radix_present) == (2, 0, 2) and ex.goal_ok
