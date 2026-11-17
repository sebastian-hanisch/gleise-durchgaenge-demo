"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, fährt jeden Regler an seine Grenzen und
prüft, dass kein Python-Fehler auftritt - insbesondere `streamlit.errors.StreamlitDuplicateElementId` (mehrere st.plotly_chart-Aufrufe ohne eindeutiges key=) und
`StreamlitAPIException` bei Slidern mit berechneten Grenzen (min == max). Dazu die Eingabefelder mit ungültigen Einträgen und die Auswahlregler an jedem Wert."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import gdg_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "▶"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    at = _fresh_app()
    assert len(at.get("plotly_chart")) >= 5


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


@pytest.mark.parametrize("key,options", [("e3_k", C.E3_K_OPTIONS), ("e4_d", C.E4_D_OPTIONS)])
def test_every_select_slider_value_does_not_raise(key, options):
    for value in options:
        at = _fresh_app()
        at.select_slider(key=key).set_value(value).run(timeout=TIMEOUT)
        assert not at.exception, (key, value, [str(e) for e in at.exception])


def test_radio_and_number_inputs_do_not_raise():
    for value in (C.E5_ORDER_FIXED, C.E5_ORDER_FREE):
        at = _fresh_app()
        at.radio(key="e5_order").set_value(value).run(timeout=TIMEOUT)
        assert not at.exception
    for key in ("e1_seed", "e4_seed", "e5_seed"):
        for value in (0, 999999):
            at = _fresh_app()
            at.number_input(key=key).set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (key, value)


@pytest.mark.parametrize("text", ["", "1", "1, 1", "a, b", "2, 1", "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13", "12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1", "3, 1, 2, 5"])
def test_train_text_input_accepts_any_entry(text):
    at = _fresh_app()
    at.text_input(key="e1_text").set_value(text).run(timeout=TIMEOUT)
    assert not at.exception, (text, [str(e) for e in at.exception])
    if text in ("", "1", "1, 1", "a, b", "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13", "3, 1, 2, 5"):
        assert at.warning, text                                              # ungültiger Zug: Warnung statt Fehler


@pytest.mark.parametrize("text", ["", "3, 3, 2, 2, 1, 1", "1", "9, 1", "x", "1, 2, 3, 4, 5, 6, 7, 1, 1, 1"])
def test_group_text_input_accepts_any_entry(text):
    at = _fresh_app()
    at.text_input(key="e5_text").set_value(text).run(timeout=TIMEOUT)
    assert not at.exception, (text, [str(e) for e in at.exception])


def test_random_and_reverse_buttons_write_the_train_field():
    at = _fresh_app()
    at.button(key="draw_reverse").click().run(timeout=TIMEOUT)
    assert at.text_input(key="e1_text").value == "8, 7, 6, 5, 4, 3, 2, 1"
    at.button(key="draw_random").click().run(timeout=TIMEOUT)
    assert sorted(int(x) for x in at.text_input(key="e1_text").value.split(", ")) == list(range(1, 9))
    assert not at.exception


def test_seed_button_changes_all_three_seeds():
    at = _fresh_app()
    before = [at.number_input(key=k).value for k in ("e1_seed", "e4_seed", "e5_seed")]
    next(b for b in at.sidebar.button if b.label.startswith("🎲")).click().run(timeout=TIMEOUT)
    after = [at.number_input(key=k).value for k in ("e1_seed", "e4_seed", "e5_seed")]
    assert not at.exception and all(a != b for a, b in zip(before, after))


def test_page_has_no_planning_words_and_names_the_model_as_made_up():
    at = _fresh_app()
    texte = " ".join(m.value for m in at.markdown) + " " + " ".join(c.value for c in at.caption)
    assert "keine reale Ankunftsfolge" in texte and "ausgedacht" in texte
    sichtbar = " ".join(line for line in texte.split("\n") if "Mehr zu den Demos" not in line)
    for wort in ("Stück", "Linie", "Vormessung", "Phase 0", "sm_v", "Plan Z"):
        assert wort not in sichtbar, wort
