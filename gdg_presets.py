"""Permalink (Begrenzen), Presets und Zufalls-Seed-Knöpfe (Standardmuster aus dem Demo-Portfolio).

Alle Regler stehen in `SETTING_SPECS`: Die Hervorhebung des aktiven Presets vergleicht jeden von ihnen mit dem Preset (Regler im Hauptbereich beim Experiment
gehören dazu). Jeder Regler ist immer sichtbar und immer wirksam (keine ausgeblendeten Regler)."""

import random
from dataclasses import dataclass

import streamlit as st

import gdg_arrival as AR
import gdg_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None
    options: tuple | None = None


SETTING_SPECS = {
    "e1_text": SettingSpec("zug", str, C.E1_DEFAULT_TEXT),
    "e1_n": SettingSpec("n1", int, C.E1_DEFAULT_N, C.E1_N_MIN, C.E1_N_MAX),
    "e1_k": SettingSpec("k1", int, C.E1_DEFAULT_K, C.E1_K_MIN, C.E1_K_MAX),
    "e1_seed": SettingSpec("s1", int, C.E1_DEFAULT_SEED, 0, C.SEED_MAX),
    "e2_n": SettingSpec("n2", int, C.E2_DEFAULT_N, C.E2_N_MIN, C.E2_N_MAX),
    "e2_k": SettingSpec("k2", int, C.E2_DEFAULT_K, C.E2_K_MIN, C.E2_K_MAX),
    "e3_k": SettingSpec("k3", int, C.E3_DEFAULT_K, options=C.E3_K_OPTIONS),
    "e4_d": SettingSpec("d4", str, C.E4_DEFAULT_D, options=C.E4_D_OPTIONS),
    "e4_n": SettingSpec("n4", int, C.E4_DEFAULT_N, C.E4_N_MIN, C.E4_N_MAX),
    "e4_k": SettingSpec("k4", int, C.E4_DEFAULT_K, C.E4_K_MIN, C.E4_K_MAX),
    "e4_trials": SettingSpec("t4", int, C.E4_DEFAULT_TRIALS, C.E4_TRIALS_MIN, C.E4_TRIALS_MAX),
    "e4_seed": SettingSpec("s4", int, C.E4_DEFAULT_SEED, 0, C.SEED_MAX),
    "e5_m": SettingSpec("m5", int, C.E5_DEFAULT_M, C.E5_M_MIN, C.E5_M_MAX),
    "e5_n": SettingSpec("n5", int, C.E5_DEFAULT_N, C.E5_N_MIN, C.E5_N_MAX),
    "e5_k": SettingSpec("k5", int, C.E5_DEFAULT_K, C.E5_K_MIN, C.E5_K_MAX),
    "e5_order": SettingSpec("o5", str, C.E5_DEFAULT_ORDER, options=(C.E5_ORDER_FIXED, C.E5_ORDER_FREE)),
    "e5_seed": SettingSpec("s5", int, C.E5_DEFAULT_SEED, 0, C.SEED_MAX),
    "e5_trials": SettingSpec("t5", int, C.E5_DEFAULT_TRIALS, C.E5_TRIALS_MIN, C.E5_TRIALS_MAX),
    "e5_text": SettingSpec("w5", str, ""),
}
# Schlüssel der Presets (Einträge in C.PRESETS) -> Schlüssel im Session State; gleich benannt wie die Felder von gdg_evaluation.Settings
PRESET_KEYS = {
    "text": "e1_text", "n1": "e1_n", "k1": "e1_k", "seed1": "e1_seed", "n2": "e2_n", "k2": "e2_k", "k3": "e3_k",
    "d4": "e4_d", "n4": "e4_n", "k4": "e4_k", "trials4": "e4_trials", "seed4": "e4_seed",
    "m5": "e5_m", "n5": "e5_n", "k5": "e5_k", "order5": "e5_order", "seed5": "e5_seed", "trials5": "e5_trials", "text5": "e5_text",
}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def clamp_setting(state_key, value):
    """Wert auf die Grenzen bzw. zulässigen Auswahlwerte des Reglers begrenzen (Permalink); ungültige Auswahl: Standardwert."""
    spec = SETTING_SPECS[state_key]
    if spec.options is not None:
        return value if value in spec.options else spec.default
    if isinstance(value, str):
        return value[: C.E1_TEXT_MAX_LEN]
    if spec.lo is not None:
        value = max(spec.lo, value)
    if spec.hi is not None:
        value = min(spec.hi, value)
    return value


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt (Auswahlwerte nur, wenn sie zulässig sind)."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            st.session_state[state_key] = clamp_setting(state_key, value)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    """Ein Preset setzt ALLE Regler: die genannten auf ihren Wert, alle übrigen auf den Standardwert (so stimmt die Hervorhebung, die genau das vergleicht)."""
    for key, state_key in PRESET_KEYS.items():
        st.session_state[state_key] = C.PRESETS[name].get(key, SETTING_SPECS[state_key].default)


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Preset ohne Eintrag für einen Regler meint dessen Standardwert) mit dem Session State.
    tests/test_layout.py prüft, dass jeder Regler (Seitenleiste und Hauptbereich) dort steht und seine Änderung die Markierung aufhebt."""
    preset_key_of = {state_key: key for key, state_key in PRESET_KEYS.items()}
    for name, preset in C.PRESETS.items():
        if all(
            st.session_state.get(state_key, spec.default) == preset.get(preset_key_of.get(state_key), spec.default)
            for state_key, spec in SETTING_SPECS.items()
        ):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seeds():
    """Neue Zufalls-Seeds für die Experimente 1, 4 und 5."""
    for key in ("e1_seed", "e4_seed", "e5_seed"):
        st.session_state[key] = random.randint(0, C.SEED_MAX)


def draw_random_train():
    """Experiment 1: den Zug des Eingabefelds durch einen Zufallszug mit n Wagen aus dem Zufalls-Seed ersetzen."""
    p = AR.random_train(st.session_state["e1_n"], st.session_state["e1_seed"])
    st.session_state["e1_text"] = ", ".join(str(v) for v in p)


def draw_reverse_train():
    """Experiment 1: den Zug des Eingabefelds durch die Umkehrfolge n, n − 1, …, 1 ersetzen."""
    n = st.session_state["e1_n"]
    st.session_state["e1_text"] = ", ".join(str(v) for v in range(n, 0, -1))
