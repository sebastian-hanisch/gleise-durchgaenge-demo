"""Gleise und Durchgänge: wie oft muss ein Zug über den Berg? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Ein Zug rollt über den Ablaufberg auf k Gleise (Warteschlangen); die Gleise werden hintereinander abgezogen. Wie viele Durchgänge braucht er mindestens, bis er sortiert
steht, und was sagt die Radix-Zahl ⌈log_k n⌉ darüber? Fünf Experimente; Aufbau nach DEMO-PLAYBOOK §2.

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import gdg_arrival as AR
import gdg_constants as C
import gdg_exact as EX
import gdg_model as M
import gdg_tables as T
import gdg_texts as TX
import gdg_visualization as V
from gdg_rng import SplitMix64
from gdg_evaluation import (
    Settings,
    WordExample,
    analyse_distribution,
    analyse_groups,
    analyse_model_v,
    analyse_sawtooth,
    analyse_train,
    analyse_word,
    de,
    kernfrage_texts,
    parse_word,
    pct,
    pct1,
    runs_text,
    thousands,
    train_text,
    verdict_distribution,
    verdict_groups,
    verdict_model_v,
    verdict_sawtooth,
    verdict_train,
    verdict_word,
)
from gdg_layout import dunkles_design, kopf_css
from gdg_presets import (
    PRESET_KEYS,
    SETTING_SPECS,
    bounds,
    draw_random_train,
    draw_reverse_train,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seeds,
    sidebar_presets,
    sync_query_params,
)

st.set_page_config(page_title="Gleise und Durchgänge – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _train(text, k):
    return analyse_train(text, k)


@st.cache_data(show_spinner=False)
def _distribution(n, k):
    return analyse_distribution(n, k)


@st.cache_data(show_spinner=False)
def _sawtooth(k):
    return analyse_sawtooth(k)


@st.cache_data(show_spinner=False)
def _model_v(d, n, k, trials, seed):
    return analyse_model_v(d, n, k, trials, seed)


@st.cache_data(show_spinner=False)
def _groups(m, n, k, trials, seed):
    return analyse_groups(m, n, k, trials, seed)


@st.cache_data(show_spinner=False)
def _word(word, m, k, order, source):
    return analyse_word(word, m, k, order, source)


@st.cache_data(show_spinner=False)
def _tables():
    return T.load()


def ranges(values):
    """[74, 75, 76, 80] → „74–76, 80“."""
    out, start, prev = [], None, None
    for v in values:
        if start is None:
            start = prev = v
        elif v == prev + 1:
            prev = v
        else:
            out.append((start, prev))
            start = prev = v
    if start is not None:
        out.append((start, prev))
    return ", ".join(str(a) if a == b else f"{a}–{b}" for a, b in out)


def tracks_frame(passes):
    """Tabelle: Durchgang, Gleis, Wagen von vorn."""
    rows = []
    for j, p in enumerate(passes, start=1):
        for g, track in enumerate(p.tracks, start=1):
            rows.append({"Durchgang": j, "Gleis": g, "Wagen (von vorn)": ", ".join(str(v) for v in track) if track else "leer"})
    return pd.DataFrame(rows)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in gdg_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🚂 Gleise und Durchgänge: wie oft muss ein Zug über den Berg?")
st.markdown(
    """
Ein Güterzug rollt über den Ablaufberg auf **k Richtungsgleise**; jedes Gleis ist eine **Warteschlange** (wer zuerst rollt, steht vorn). Danach werden die Gleise 1 bis k **hintereinander abgezogen**:
das ist ein **Durchgang**. Die Demo zählt, **wie viele Durchgänge** ein Zug mindestens braucht, bis er aufsteigend sortiert steht, und vergleicht das mit der Radix-Zahl ⌈log_k n⌉ (Radix-Sortierung
nach den Ziffern des Rangs zur Basis k). Die Antwort hängt an einer einzigen Zahl des Zuges: der Zahl **R seiner steigenden Folgen**. Gilt in diesem Modell (k Warteschlangen, Abziehen hintereinander,
keine Gleislängen).

**Das Ankunftsmodell ist ausgedacht** (Modell V in Experiment 4, dazu alle Folgen gleich wahrscheinlich): Es ist **keine reale Ankunftsfolge** und kein Fall. Weiter unten: die Experimente 1 bis 5,
der Abschnitt **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

# erklaerseite:einfach:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/gleise-durchgaenge-erklaert.json, nicht von Hand ändern)
with st.expander("💬 In einfachen Worten"):
    st.markdown(
        """
Stellen Sie sich einen Zug vor, der in falscher Reihenfolge ankommt und am Ablaufberg auf mehrere Gleise verteilt wird. Danach werden die Gleise nacheinander abgezogen: Das ist ein **Durchgang**. Die Demo zählt, wie viele Durchgänge mindestens nötig sind, bis der Zug richtig steht. Es hängt nur an einer Zahl des Zuges, den **steigenden Folgen**: Ketten aufeinanderfolgender Nummern, die im Zug schon in der richtigen Reihenfolge stehen. Die **Radix-Zahl** ist die Obergrenze, die Zahl für den schlimmsten Zug; ein gewöhnlicher Zug liegt je nach Wagen- und Gleiszahl darunter oder nicht. Im letzten Versuch haben mehrere Wagen dasselbe Ziel (Gruppieren statt Sortieren). Alle Reihenfolgen sind ausgedacht, es ist ein Rechenmodell und kein echter Betrieb.

[Ausführlich und verständlich erklärt, mit Fachteil](https://sebastianhanisch.net/gleise-durchgaenge-erklaert.html)
        """
    )
# erklaerseite:einfach:end

with st.expander("So funktioniert ein Durchgang", expanded=True):
    st.markdown(
        """
1. **Zug:** die Folge der Abfahrtsränge 1 bis n in Ankunftsreihenfolge; **sortiert** heißt aufsteigend 1, 2, …, n.
2. **Durchgang:** Jeder Wagen rollt auf ein Gleis seiner Wahl; danach werden die Gleise 1, 2, …, k nacheinander ganz abgezogen und ergeben den Zug für den nächsten Durchgang.
3. **Steigende Folge:** eine Reihe aufeinanderfolgender Ränge v, v+1, …, w, die im Zug in dieser Reihenfolge stehen. **R** ist ihre Zahl; R − 1 zählt die Stellen, an denen v+1 vor v steht.
4. **Plan:** Jeder Wagen bekommt als Beschriftung die Nummer seiner steigenden Folge. Durchgang 1 sortiert nach der niedrigsten Ziffer der Beschriftung zur Basis k, Durchgang 2 nach der nächsten, usw.
   Nach ⌈log_k R⌉ Durchgängen steht der Zug sortiert.
5. **Radix:** In diesem Modell (Zug aus lauter verschiedenen Rängen, k ≥ 2 Gleise) reichen ⌈log_k n⌉ Durchgänge immer (Radix-Sortierung nach den Ziffern des Rangs, dazu ist R höchstens n). Der **umgekehrte** Zug hat R = n und braucht genau so viele.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.caption("Die Regler der Experimente stehen jeweils beim Experiment. Hier nur der Zufall.")
    st.button("🎲 Neue Zufalls-Seeds (Experimente 1, 4 und 5)", width="stretch", on_click=randomize_seeds,
              help="Zieht für die Experimente 1, 4 und 5 neue Zufalls-Seeds (ganzzahliger SplitMix64).")

s = Settings(**{key: st.session_state[state_key] for key, state_key in PRESET_KEYS.items()})
sync_query_params({state_key: st.session_state[state_key] for state_key in SETTING_SPECS})

a1 = _train(s.text, s.k1)
d2 = _distribution(s.n2, s.k2)
g5_trials = min(s.trials5, C.E5_TRIAL_CAP[s.m5])
with st.spinner(f"Rechne {g5_trials} Züge mit {s.m5} Gruppen (bei 7 Gruppen bis etwa 2 s) …"):
    g5 = _groups(s.m5, s.n5, s.k5, s.trials5, s.seed5)

# --- Kernfragen ----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfragen")
q1, q2, q3 = kernfrage_texts(a1, d2, g5)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**1. Wie viele Durchgänge braucht dieser Zug, und warum?**")
    st.metric("Mindestzahl Durchgänge", q1)
    st.caption(f"Zug {train_text(a1.train)} mit {s.k1} Gleisen; Radix würde {a1.radix} nennen. Experiment 1." if not a1.error else "Bitte einen gültigen Zug eintragen (Experiment 1).")
with c2:
    st.markdown("**2. Wann ist die Radix-Zahl zu hoch, wann genau richtig?**")
    st.metric("Mittlere Durchgänge gegen Radix", q2)
    st.caption(f"n = {s.n2}, k = {s.k2}, alle n! Folgen gleich wahrscheinlich. Experimente 2 und 3.")
with c3:
    st.markdown("**3. Was ändert sich mit Gruppen?**")
    st.metric("Exakt unter Radix (freie Reihenfolge)", q3)
    st.caption(f"{s.m5} Gruppen, {s.k5} Gleise, {s.n5} Wagen, {g5.trials} Züge. Experiment 5.")

st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Ein Zug von Hand")
st.caption("Der Zug ist die Folge der Abfahrtsränge in Ankunftsreihenfolge (Zahl = Rang). Farben markieren die steigenden Folgen. Das Feld gilt, so wie es dasteht; "
           "die beiden Knöpfe darunter schreiben einen Zufallszug aus n und dem Zufalls-Seed oder die Umkehrfolge in das Feld.")
col_a, col_b = st.columns([3, 2])
with col_a:
    st.text_input("Zug (Abfahrtsränge, durch Komma getrennt)", key="e1_text", max_chars=C.E1_TEXT_MAX_LEN,
                  help="Ränge 1 bis n, jeder genau einmal, 2 bis 12 Wagen. Beispiel: 2, 4, 6, 1, 3, 5.")
    st.slider("Gleise k", *bounds("e1_k"), key="e1_k", help="Wie viele Gleise (Warteschlangen) der Ablaufberg hat.")
with col_b:
    st.slider("Wagen n für Zufallszug und Umkehrfolge", *bounds("e1_n"), key="e1_n", help="Gilt für die Knöpfe unten.")
    st.number_input("Zufalls-Seed für den Zufallszug", *bounds("e1_seed"), key="e1_seed", step=1, help="Bestimmt den Zufallszug (ganzzahliger SplitMix64).")
    b1, b2 = st.columns(2)
    b1.button("🎲 Zufallszug", width="stretch", on_click=draw_random_train, key="draw_random")
    b2.button("↧ Umkehrfolge", width="stretch", on_click=draw_reverse_train, key="draw_reverse")

if a1.error:
    st.warning(a1.error)
else:
    m1, m2, m3 = st.columns(3)
    m1.metric("Steigende Folgen R", a1.r)
    m2.metric(f"Mindestzahl Durchgänge (k = {a1.k})", a1.passes, delta=f"{a1.passes - a1.radix:+d} gegen Radix", delta_color="inverse")
    m3.metric("Radix ⌈log_k n⌉", a1.radix, delta="Referenz", delta_color="off")
    run_index = {v: i for i, run in enumerate(a1.runs) for v in run}
    rows = [("Zug vorher", a1.train)] + [(f"nach Durchgang {j}", p.after) for j, p in enumerate(a1.plan, start=1)]
    st.plotly_chart(V.build_states_figure(rows, lambda v: run_index[v]), width="stretch", key="e1_states")
    st.caption(f"Steigende Folgen: {runs_text(a1.runs)}. Gleiche Farbe = gleiche steigende Folge. Der Plan beschriftet jeden Wagen mit der Nummer seiner steigenden Folge.")
    if a1.plan:
        st.dataframe(tracks_frame(a1.plan), hide_index=True, width="stretch")
        st.caption("Gleis 1 wird zuerst abgezogen. Die Gleiswahl je Wagen steht in der Ziffer der Beschriftung zur Basis k (niedrigste Ziffer im ersten Durchgang).")
    st.caption(f"Prüfung durch Abspielen der Gleiswahl (unabhängiger Prüfer): Zug danach {train_text(a1.final)}, sortiert: {'ja' if a1.sorted_ok else 'nein'}.")
kind, text = verdict_train(a1)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Wie viele Durchgänge im Mittel? Radix ist der schlimmste Fall")
st.caption("Exakte Verteilung über alle n! Folgen, aus den Eulerschen Zahlen (Ganzzahlen; die Zahl der Folgen mit R steigenden Folgen ist die Eulersche Zahl A(n, R − 1)). "
           "Für n bis 8 zählt die App zur Gegenprobe alle Folgen einzeln auf. Radix ist die Zahl für den schlimmsten Zug (die Umkehrfolge); wie weit ein typischer Zug darunter liegt, hängt an n und k (Experiment 3).")
cc1, cc2 = st.columns(2)
cc1.slider("Wagen n", *bounds("e2_n"), key="e2_n", help="Zahl der Wagen; alle n! Folgen sind gleich wahrscheinlich.")
cc2.slider("Gleise k", *bounds("e2_k"), key="e2_k", help="Zahl der Gleise.")
sm = d2.summary
m1, m2, m3 = st.columns(3)
m1.metric("Mittlere Zahl Durchgänge", de(float(sm.mean), 3), delta=f"{float(sm.mean) - sm.radix:+.3f} gegen Radix".replace(".", ","), delta_color="inverse")
m2.metric("Radix ⌈log_k n⌉ = schlimmster Fall", sm.radix, delta="Referenz", delta_color="off")
m3.metric("Anteil der Folgen unter Radix", pct(sm.share_below))
st.plotly_chart(V.build_distribution_figure(sm), width="stretch", key="e2_dist")
if sm.total < 10**15:
    frame = pd.DataFrame({"Durchgänge": list(sm.counts), "Zahl der Folgen": [thousands(c) for c in sm.counts.values()],
                          "Anteil": [f"{100 * c / sm.total:.4f} %".replace(".", ",") for c in sm.counts.values()]})
    st.dataframe(frame, hide_index=True, width="stretch")
kind, text = verdict_distribution(d2)
getattr(st, kind)(text)

st.markdown("**Ein Durchgang: Gleise hintereinander abziehen gegen die Vorderseiten frei auslesen** (vorgerechnet, `tools/gdg_make_tables.py`)")
st.caption("Zähleinheit Folgen aller n!. „Gleise“: Folgen, die ein Durchgang über k Gleise sortiert (R ≤ k). „Frei“: Folgen, die k parallele Warteschlangen sortieren, wenn die Vorderseiten in "
           "beliebiger Reihenfolge ausgelesen werden dürfen (längste fallende Teilfolge höchstens k; Tarjan 1971, Lemma 2, nach Quellenbericht, hier für n ≤ 6 und k = 2, 3 durch Simulation bestätigt). "
           "Bei Warteschlangen macht es keinen Unterschied, ob die Ausgabe sofort oder später erfolgt; der Unterschied ist das Abziehen hintereinander.")
tables = _tables()
table_rows = []
for n in C.TABLE_N:
    row = {"n": n, "n!": thousands(sum(EX.eulerian_row(n)))}
    for k in C.TABLE_K:
        pr = T.parallel_row(tables, n, k)
        row[f"k = {k}: Gleise"] = thousands(pr["gleise"])
        row[f"k = {k}: frei"] = thousands(pr["frei"])
    table_rows.append(row)
st.dataframe(pd.DataFrame(table_rows), hide_index=True, width="stretch")

st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 3: Wann ist Radix zu hoch? Der Sägezahn")
st.caption("Anteil der Folgen, die weniger Durchgänge brauchen als Radix, gegen n = 20 bis 200 (exakt aus den Eulerschen Zahlen, einmal gerechnet). „Radix ist meist zu hoch“ gilt nicht allgemein.")
st.select_slider("Gleise k", options=C.E3_K_OPTIONS, key="e3_k", help="Die Zahlen der Gleise, für die der Sägezahn gerechnet wird.")
a3 = _sawtooth(s.k3)
st.plotly_chart(V.build_sawtooth_figure(a3["data"], a3["powers"], s.k3), width="stretch", key="e3_saw")
st.plotly_chart(V.build_sawtooth_mean_figure(a3["data"], s.k3), width="stretch", key="e3_mean")
if a3["stats"]["zeros"]:
    st.caption(f"Werte von n mit Anteil unter {de(C.E3_ZERO_EPS, 5)} (Radix ist dort für fast alle Folgen genau richtig): {ranges(a3['stats']['zeros'])}.")
kind, text = verdict_sawtooth(a3)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 4 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 4: Wie kommt der Zug an? Modell V (ausgedacht)")
st.caption("Wagen i kommt zur Zeit i an und bleibt eine exponentialverteilte Verweilzeit mit dem Mittel D (in Ankunftsabständen); der Abfahrtsrang ist die Stelle in der Reihenfolge der Abfahrtszeiten. "
           "**Nur diese Rangfolge geht in die Rechnung ein.** Kleines D heißt fast sortiert, „gleichverteilt“ heißt jede Folge gleich wahrscheinlich. Keine reale Ankunftsfolge.")
r1, r2, r3 = st.columns(3)
with r1:
    st.select_slider("Mittlere Verweilzeit D", options=C.E4_D_OPTIONS, key="e4_d", help="In Ankunftsabständen; „gleichverteilt“ ist der Grenzfall D → ∞.")
    st.slider("Wagen n", *bounds("e4_n"), key="e4_n")
with r2:
    st.slider("Gleise k", *bounds("e4_k"), key="e4_k")
    st.slider("Zahl der Folgen", *bounds("e4_trials"), key="e4_trials", step=100, help="Je Folge n Zufallszahlen; 1000 Folgen mit n = 60 brauchen etwa 2 Sekunden.")
with r3:
    st.number_input("Zufalls-Seed", *bounds("e4_seed"), key="e4_seed", step=1, help="Bestimmt die Folgen (ganzzahliger SplitMix64).")
with st.spinner(f"Rechne {s.trials4} Folgen mit n = {s.n4} (bis etwa 2 s) …"):
    a4 = _model_v(s.d4, s.n4, s.k4, s.trials4, s.seed4)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Mittlere Durchgänge", de(a4.mean_passes), delta=f"{a4.mean_passes - a4.radix:+.2f} gegen Radix".replace(".", ","), delta_color="inverse")
m2.metric("Anteil mit höchstens 1 Durchgang", pct1(a4.one_or_less))
m3.metric("Anteil unter Radix", pct1(a4.below_radix))
m4.metric("Mittel von R", de(a4.mean_r, 1), delta=f"gleichverteilt exakt {de(a4.uniform_exact_mean_r, 1)}", delta_color="off")
st.plotly_chart(V.build_r_histogram_figure(a4.r_hist, a4.uniform_exact_mean_r), width="stretch", key="e4_hist")
st.caption(f"Erster Zug der Probe: {train_text(a4.example)} mit R = {M.rising_count(a4.example)} steigenden Folgen.")
kind, text = verdict_model_v(a4)
getattr(st, kind)(text)

st.markdown(f"**Vorgerechnet** ({thousands(C.MODEL_V_TRIALS)} Folgen je Zelle, `tools/gdg_make_tables.py`): Mittel Durchgänge / Anteil mit höchstens einem Durchgang / Anteil unter Radix, k = {s.k4}")
mv_rows = []
for n in T.MODEL_V_N:
    row = {"n": n, "Radix": M.radix(n, s.k4)}
    for d in T.MODEL_V_D:
        cell = next(c for c in tables["modell_v"] if c["n"] == n and c["d"] == d)
        st_ = T.passes_from_r_hist(cell["r_hist"], s.k4)
        label = "gleichverteilt" if d == "gleichverteilt" else "D = " + d.replace(".", ",")
        row[label] = f"{de(st_['mean'])} / {de(st_['one_or_less'])} / {de(st_['below_radix'])}"
    mv_rows.append(row)
st.dataframe(pd.DataFrame(mv_rows), hide_index=True, width="stretch")

st.markdown("---")

# --- Experiment 5 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 5: Gruppen – Gruppieren statt Sortieren (die aufgehobene Annahme)")
st.caption("Jetzt haben mehrere Wagen dieselbe Zielgruppe. **Sortiert** heißt: die Gruppen 1, 2, …, m stehen in dieser Reihenfolge. **Gruppiert** heißt: jede Gruppe steht zusammenhängend, die Reihenfolge der Gruppen "
           "ist frei (so rechnet die Ablaufberg-Demo). Radix ⌈log_k g⌉ rechnet mit g, der Zahl der **vorhandenen** Gruppen. Die Mindestzahl ist ⌈log_k L⌉ mit der Beschriftungszahl L (im 📐-Expander).")
g1, g2, g3 = st.columns(3)
with g1:
    st.slider("Gruppen m", *bounds("e5_m"), key="e5_m", help="Jeder Wagen gehört unabhängig und gleichverteilt zu einer der m Gruppen. Bei 7 Gruppen sind 5040 Reihenfolgen zu prüfen.")
    st.slider("Wagen n", *bounds("e5_n"), key="e5_n")
with g2:
    st.slider("Gleise k", *bounds("e5_k"), key="e5_k")
    st.radio("Reihenfolge der Gruppen (für den Beispielzug)", (C.E5_ORDER_FIXED, C.E5_ORDER_FREE), key="e5_order", horizontal=True,
             help="Bestimmt, welchen Plan der Beispielzug zeigt; die Anteile unten zeigen immer beide.")
with g3:
    st.slider("Zahl der Züge", *bounds("e5_trials"), key="e5_trials", step=20, help=f"Bei 7 Gruppen höchstens {C.E5_TRIAL_CAP[7]} Züge.")
    st.number_input("Zufalls-Seed", *bounds("e5_seed"), key="e5_seed", step=1, help="Bestimmt die Züge (ganzzahliger SplitMix64).")
st.text_input("Eigener Beispielzug (Gruppennummern, durch Komma getrennt; leer = erster Zufallszug)", key="e5_text", max_chars=4 * C.E5_N_MAX,
              help="Gruppen 1 bis 7, 2 bis 40 Wagen. Beispiel: 3, 3, 2, 2, 1, 1. Die Anteile oben rechnen unabhängig davon über Zufallszüge.")
m1, m2, m3 = st.columns(3)
m1.metric("Frei: exakt unter Radix", pct1(g5.free_lt_present / g5.trials))
m2.metric("Fest: exakt unter Radix", pct1(g5.fixed_lt_present / g5.trials))
m3.metric("Mittlere Durchgänge (frei)", de(g5.mean_free), delta=f"{g5.mean_free - g5.mean_radix:+.2f} gegen Radix".replace(".", ","), delta_color="inverse")
st.plotly_chart(V.build_groups_figure(g5), width="stretch", key="e5_means")
kind, text = verdict_groups(g5)
getattr(st, kind)(text)

if s.text5.strip():
    word, word_error = parse_word(s.text5)
    source = "eingetragen"
else:
    word, word_error = AR.random_word(s.n5, s.m5, SplitMix64(s.seed5)), None
    source = "erster Zufallszug"
if word_error:
    st.warning(word_error)
else:
    m_ex = max(word) if source == "eingetragen" else s.m5
    ex: WordExample = _word(word, m_ex, s.k5, s.order5, source)
    st.markdown(f"**Beispielzug** ({source}), Plan für die **{ex.order}e** Reihenfolge der Gruppen")
    rows = [("Zug vorher", ex.word)] + [(f"nach Durchgang {j}", p.after) for j, p in enumerate(ex.plan, start=1)]
    st.plotly_chart(V.build_states_figure(rows, lambda v: v - 1), width="stretch", key="e5_states")
    if ex.plan:
        st.dataframe(tracks_frame(ex.plan), hide_index=True, width="stretch")
    st.caption(f"Farbe = Gruppe. Beschriftungen der Wagen (Nummer, nach der der Plan sortiert): {train_text(ex.labels)}; L = {ex.L}. "
               + ("Gruppenreihenfolge nach Rang: " + ", ".join(str(g + 1) for g in sorted(range(len(ex.best_ranks)), key=lambda g: ex.best_ranks[g])) + "." if ex.order == C.E5_ORDER_FREE else
                  "Gruppen in der Reihenfolge ihrer Nummern."))
    kind, text = verdict_word(ex)
    getattr(st, kind)(text)

st.markdown(f"**Vorgerechnet** ({thousands(C.GROUP_TRIALS)} Züge je Zelle, bei 8 Gruppen 60; `tools/gdg_make_tables.py`): jeder Wagen gleichverteilt in eine von m Gruppen, Radix aus den vorhandenen Gruppen")
gr_rows = []
for c in tables["gruppen"]:
    n_tr, cc_ = c["trials"], c["counts"]
    gr_rows.append({"Gruppen m": c["m"], "Gleise k": c["k"], "Wagen n": c["n"], "Züge": n_tr,
                    "frei unter Radix": pct1(cc_["free_lt_present"] / n_tr), "fest unter Radix": pct1(cc_["fixed_lt_present"] / n_tr),
                    "Mittel Radix": de(cc_["sum_radix_present"] / n_tr, 3), "Mittel fest": de(cc_["sum_fixed"] / n_tr, 3), "Mittel frei": de(cc_["sum_free"] / n_tr, 3)})
st.dataframe(pd.DataFrame(gr_rows), hide_index=True, width="stretch")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(TX.ASSUMPTIONS_MARKDOWN)
st.caption(TX.LIMITS_NOTE)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    # erklaerseite:lesehilfe:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/gleise-durchgaenge-erklaert.json, nicht von Hand ändern)
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind ein Zug $p$ aus den Abfahrtsrängen $1,\dots,n$ in Ankunftsreihenfolge und $k \ge 2$ Gleise. Gesucht ist die kleinste Zahl $t^*$ von Durchgängen, nach denen der Zug aufsteigend steht.

| Symbol | Bedeutung |
|---|---|
| $p$, $n$ | der Zug (Folge der Ränge $1,\dots,n$ in Ankunftsreihenfolge) und die Zahl der Wagen |
| $k$ | Zahl der Gleise (Warteschlangen) |
| Durchgang | jeder Wagen rollt auf ein Gleis, danach werden die Gleise $1,\dots,k$ hintereinander abgezogen |
| $g_i \in \{1,\dots,k\}$ | das gewählte Gleis des Wagens an Stelle $i$ in einem Durchgang |
| $R$ | Zahl der steigenden Folgen von $p$ |
| $\mathrm{Radix}(n,k)$ | die Zahl $\lceil \log_k n \rceil$ |
| $t^*$ | die Mindestzahl Durchgänge |
| $L$ | Beschriftungszahl bei Wagen mit gleicher Zielgruppe |
| $D$ | mittlere Verweilzeit in Modell V, in Ankunftsabständen |
| sortiert / gruppiert | aufsteigend $1,\dots,n$ bzw. jede Zielgruppe zusammenhängend |

[Schritt für Schritt erklärt, mit Herleitung und Literatur](https://sebastianhanisch.net/gleise-durchgaenge-erklaert.html#fachleute)
        """
    )
    # erklaerseite:lesehilfe:end
    st.markdown(
        r"""
**Modell eines Durchgangs.** Mit der Gleiswahl $g$ steht der Zug danach nach den Schlüsseln $(g_i, i)$ geordnet; der Durchgang $\Phi_g$ ordnet die Wagen also stabil nach dem Gleis.

$$\Phi_g(p) = \bigl(p_i\bigr)_{i \text{ geordnet nach } (g_i,\, i)}$$

Gesucht ist die kleinste Zahl $t$ mit Gleiswahlen $g^{(1)},\dots,g^{(t)}$, so dass der Zug nach den $t$ Durchgängen sortiert ist:

$$t^*(p,k) = \min\Bigl\{ t : \Phi_{g^{(t)}} \circ \cdots \circ \Phi_{g^{(1)}}(p) = (1,2,\dots,n) \Bigr\}$$

**Steigende Folgen.** Mit der Stelle $\mathrm{pos}(v)$ des Rangs $v$ im Zug:

$$R(p) = 1 + \bigl|\{\, v \in \{1,\dots,n-1\} : \mathrm{pos}(v+1) < \mathrm{pos}(v) \,\}\bigr|$$

**Formel (eigene Rechnung, bis n = 8 für k = 2 und bis n = 7 für k = 3 und 4 durch Aufzählung aller Folgen bestätigt).**

$$t^*(p,k) = \lceil \log_k R(p) \rceil \qquad (t^* = 0 \text{ für } R = 1)$$

*Beweisskizze, kein vollständiger Beweis:* Ein Durchgang sortiert genau dann, wenn sich die Ränge an den $R-1$ Stellen, an denen $v+1$ vor $v$ steht, in höchstens $k$ Blöcke schneiden lassen, also wenn $R \le k$.
$t$ Durchgänge sind eine Radix-Sortierung mit frei wählbaren Ziffern: Jeder Wagen bekommt $t$ Ziffern zur Basis $k$, eine je Durchgang, und weil jedes Gleis stabil ist, steht der Zug am Ende nach (Ziffernwert, ursprüngliche
Stelle) geordnet. Die kleinste Beschriftung, die den Zug sortiert, ist die Nummer der steigenden Folge, also $R$ Werte; $R \le k^t$ ist gleichwertig mit $t \ge \lceil \log_k R \rceil$.

**Radix und schlimmster Fall.** Der umgekehrte Zug hat $R = n$; gilt die Formel, ist $\lceil \log_k n \rceil$ der schlimmste Fall (für $k \ge 2$; in allen 1 791 Paaren $n = 2$ bis $200$, $k = 2$ bis $10$ aus den Verteilungen gezählt, Befund B5 der README; die Formel selbst ist bis $n = 8$ aufgezählt):

$$\mathrm{Radix}(n,k) = \lceil \log_k n \rceil = \max_p \, t^*(p,k)$$

**Verteilung bei gleichverteilten Folgen.** Die Zahl der Folgen mit $R = r$ ist die Eulersche Zahl $A(n, r-1)$, das Mittel von $R$ ist $(n+1)/2$:

$$A(m,d) = (d+1)\,A(m-1,d) + (m-d)\,A(m-1,d-1), \qquad A(1,0) = 1, \qquad \mathbb{E}[R] = \frac{n+1}{2}$$

Dabei sind alle $A(m,d)$ mit $d < 0$ oder $d > m-1$ gleich 0.

**Wagen mit gleicher Zielgruppe (eigene Konstruktion, in den geprüften Fällen bestätigt, kein Beweis).** Für zwei Wagen $e$ und $j$ mit Gruppe($e$) < Gruppe($j$) muss die Beschriftung $\lambda$ erfüllen:

$$\lambda_j \ge \lambda_e + [\, e \text{ steht hinter } j \,]$$

$L = 1 + \max_i \lambda_i$ für die kleinste Lösung. Sortiert: $t^* = \lceil \log_k L \rceil$. Gruppiert (freie Reihenfolge $\sigma$ der Gruppen):

$$t^*_{\text{frei}} = \min_{\sigma} \lceil \log_k L_\sigma \rceil$$

**Modell V (ausgedacht).** Wagen $i$ kommt zur Zeit $i$ an und fährt zur Zeit $a_i$ ab; der Abfahrtsrang ist die Stelle in der Reihenfolge der $a_i$ (Gleichstand: kleinerer Index zuerst):

$$a_i = i + X_i, \qquad X_i \sim \mathrm{Exp}(\text{Mittel } D)$$

Der Formelblock ist ein vollständiges Modell der Durchgänge für Wagen mit verschiedenem Rang (Experimente 1 bis 4); die Beweisskizze und die Konstruktion für Gruppen sind ausdrücklich Skizzen.

**Literatur und Quellen.** Jacob, Márton, Maue, Nunkesser: *Multistage Methods for Freight Train Classification*, ATMOS 2007 (Fassung 2007 gelesen; mit begrenzter Gleiskapazität ist mehrstufiges Sortieren
NP-schwer; die erweiterte Fassung in Networks 57(1), 2011 nicht gelesen). Tarjan: *The Switchyard Problem: Sorting Using Networks of Queues and Stacks*, Stanford CS-TR-71-213, 1971 (Vorfassung des Aufsatzes im
J. ACM 1972; Lemma 2 nach Quellenbericht: k parallele Warteschlangen sortieren genau die Folgen mit längster fallender Teilfolge höchstens k; der Aufsatz selbst nicht gelesen). Für die Gleichheit
$\lceil \log_k n \rceil$ der Radix-Zahl und für die Formel $\lceil \log_k R \rceil$ ist keine gelesene Quelle bekannt: beide sind hier nachgerechnet, nicht belegt.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
