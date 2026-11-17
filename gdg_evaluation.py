"""Kennzahlen und Verdikte der fünf Experimente. Jedes Verdikt ist eine reine Funktion `verdict_*(…) -> (Art, Text)`; die App ruft `getattr(st, Art)(Text)`.

Alle Zahlen sind Ganzzahlen oder Anteile aus Ganzzahlen; Zufall nur aus dem SplitMix64 (`gdg_rng.py`).
Zähleinheiten: Experiment 1 ein Zug; 2 und 3 Folgen (alle n! gleich wahrscheinlich); 4 Folgen aus Modell V (ausgedacht); 5 Züge mit Gruppen."""

from dataclasses import dataclass
from fractions import Fraction

import gdg_arrival as AR
import gdg_constants as C
import gdg_exact as EX
import gdg_model as M
import gdg_tables as T
import gdg_words as W
from gdg_rng import SplitMix64

# ---------------------------------------------------------------- Zahlenformate (deutsch)


def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def thousands(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def pct(x: float | Fraction) -> str:
    """Anteil als Prozentangabe mit Rücksicht auf sehr kleine und sehr große Werte (nie „0,00 %“ für einen Anteil über 0, nie „100,00 %“ unter 1)."""
    x = float(x)
    if x == 0:
        return "0 %"
    if x == 1:
        return "100 %"
    if x < 1e-4:
        return "weniger als 0,01 %"
    if x > 1 - 1e-4:
        return "mehr als 99,99 %"
    return f"{de(100 * x, 2)} %"


def pct1(x: float | Fraction) -> str:
    """Prozent mit einer Stelle (Zufallsproben mit einigen Tausend Zügen)."""
    return f"{de(100 * float(x), 1)} %"


def train_text(p) -> str:
    return "(" + ", ".join(str(v) for v in p) + ")"


def runs_text(runs) -> str:
    return ", ".join("{" + ", ".join(str(v) for v in run) + "}" for run in runs)


# ---------------------------------------------------------------- Einstellungen


@dataclass(frozen=True)
class Settings:
    text: str = C.E1_DEFAULT_TEXT
    n1: int = C.E1_DEFAULT_N
    k1: int = C.E1_DEFAULT_K
    seed1: int = C.E1_DEFAULT_SEED
    n2: int = C.E2_DEFAULT_N
    k2: int = C.E2_DEFAULT_K
    k3: int = C.E3_DEFAULT_K
    d4: str = C.E4_DEFAULT_D
    n4: int = C.E4_DEFAULT_N
    k4: int = C.E4_DEFAULT_K
    trials4: int = C.E4_DEFAULT_TRIALS
    seed4: int = C.E4_DEFAULT_SEED
    m5: int = C.E5_DEFAULT_M
    n5: int = C.E5_DEFAULT_N
    k5: int = C.E5_DEFAULT_K
    order5: str = C.E5_DEFAULT_ORDER
    seed5: int = C.E5_DEFAULT_SEED
    trials5: int = C.E5_DEFAULT_TRIALS
    text5: str = ""


# ---------------------------------------------------------------- Experiment 1: ein Zug von Hand


@dataclass(frozen=True)
class OneTrain:
    error: str | None
    train: tuple
    k: int
    runs: tuple
    r: int
    passes: int
    radix: int
    plan: tuple
    final: tuple
    sorted_ok: bool
    forward: tuple | None            # (Zahl der Zuweisungen, davon sortierende) oder None
    passes_by_k: dict                # k = 2..6 -> Mindestzahl


def analyse_train(text: str, k: int) -> OneTrain:
    p, error = M.parse_train(text)
    if p is None:
        return OneTrain(error, (), k, (), 0, 0, 0, (), (), False, None, {})
    runs = tuple(tuple(r) for r in M.rising_runs(p))
    r = len(runs)
    passes = M.min_passes(p, k)
    pl = M.plan(p, k)
    final = M.play(p, [x.assign for x in pl], k)
    by_k = {kk: M.min_passes(p, kk) for kk in range(C.E1_K_MIN, C.E1_K_MAX + 1)}
    return OneTrain(None, p, k, runs, r, passes, M.radix(len(p), k), tuple(pl), final, final == tuple(range(1, len(p) + 1)), M.forward_one_pass(p, k), by_k)


def verdict_train(a: OneTrain) -> tuple[str, str]:
    if a.error:
        return "warning", a.error
    zug = train_text(a.train)
    if a.r == 1:
        return "info", f"Der Zug {zug} ist schon sortiert: R = 1 steigende Folge, 0 Durchgänge."
    text = (f"Zug {zug}: **R = {a.r}** steigende Folgen ({runs_text(a.runs)}), mit {a.k} Gleisen **{a.passes} Durchgänge** (Radix: {a.radix}). "
            f"Der abgespielte Plan sortiert den Zug: {'ja' if a.sorted_ok else 'NEIN'}.")
    if a.forward is not None:
        total, ok = a.forward
        if a.r <= a.k:
            text += f" Die Vorwärtssuche über alle {thousands(total)} Zuweisungen findet {thousands(ok)}, die ihn in einem Durchgang sortieren."
        else:
            text += f" Die Vorwärtssuche über alle {thousands(total)} Zuweisungen findet keine, die ihn in einem Durchgang sortiert (R > k)."
    by_k = ", ".join(f"{k} Gleise: {t}" for k, t in a.passes_by_k.items())
    text += f" Mindestzahl nach der Formel je Gleiszahl: {by_k}."
    return ("success" if a.passes < a.radix else "info"), text


# ---------------------------------------------------------------- Experiment 2: exakte Verteilung


@dataclass(frozen=True)
class Distribution:
    summary: EX.Summary
    enumerated: bool | None          # Aufzählung aller n! Folgen stimmt mit den Eulerschen Zahlen überein (nur n <= 8)


def analyse_distribution(n: int, k: int) -> Distribution:
    s = EX.summary(n, k)
    enumerated = None
    if n <= C.ENUM_N_MAX:
        enumerated = EX.enumerate_rising_histogram(n) == list(EX.eulerian_row(n)) and EX.mean_passes_from_histogram(EX.enumerate_rising_histogram(n), k) == s.mean
    return Distribution(s, enumerated)


def verdict_distribution(d: Distribution) -> tuple[str, str]:
    s = d.summary
    if s.total < 10**15:
        gleich = f"{thousands(s.at_radix)} von {thousands(s.total)} Folgen ({pct(Fraction(s.at_radix, s.total))}) brauchen {s.radix}"
    else:
        gleich = f"{pct(Fraction(s.at_radix, s.total))} der n! Folgen brauchen {s.radix}"
    text = f"n = {s.n}, k = {s.k}: Radix {s.radix}, im Mittel **{de(float(s.mean), 3)} Durchgänge**; {gleich}"
    nxt = s.radix - 1
    if nxt in s.counts and s.total < 10**15:
        text += f", {thousands(s.counts[nxt])} brauchen {nxt}"
    text += f". Weniger als Radix brauchen {pct(s.share_below)} der Folgen. Zähleinheit Folgen, alle n! gleich wahrscheinlich."
    if d.enumerated is not None:
        text += f" Die Aufzählung aller {thousands(s.total)} Folgen {'bestätigt' if d.enumerated else 'WIDERSPRICHT'} die Eulerschen Zahlen."
    if s.share_below < Fraction(1, 100):
        return "warning", text + " Hier ist Radix für fast alle Folgen genau richtig."
    return "info", text


# ---------------------------------------------------------------- Experiment 3: Sägezahn


def analyse_sawtooth(k: int) -> dict:
    stats = EX.sawtooth_stats((k,))[k]
    data = EX.sawtooth()[k]
    powers = [(k**r, data[k**r][0], data[k**r][1]) for r in range(1, 9) if C.E3_N_FROM <= k**r <= C.E3_N_TO]
    return {"k": k, "stats": stats, "data": data, "powers": powers}


def verdict_sawtooth(a: dict) -> tuple[str, str]:
    s, k = a["stats"], a["k"]
    text = (f"k = {k}, n = {C.E3_N_FROM} bis {C.E3_N_TO}: Der Anteil der Folgen mit weniger Durchgängen als Radix liegt zwischen {de(s['min'], 4)} (n = {s['min_n']}) "
            f"und {de(s['max'], 4)} (n = {s['max_n']}); in {len(s['zeros'])} von {s['count']} Werten von n liegt er unter {de(C.E3_ZERO_EPS, 5)}. ")
    if a["powers"]:
        text += "Bei n = " + ", ".join(f"{n} ({de(share, 4)})" for n, share, _ in a["powers"]) + " (Potenzen von k). "
    text += "Zähleinheit Folgen, alle n! gleich wahrscheinlich, exakt aus den Eulerschen Zahlen."
    return ("warning" if s["zeros"] else "info"), text


# ---------------------------------------------------------------- Experiment 4: Modell V


@dataclass(frozen=True)
class ModelV:
    n: int
    k: int
    d: str
    trials: int
    radix: int
    mean_passes: float
    one_or_less: float
    below_radix: float
    mean_r: float
    r_hist: tuple
    example: tuple
    uniform_exact_mean: float
    uniform_exact_mean_r: float
    uniform_sample_mean: float


def _passes_stats(trains, k: int, n: int) -> dict:
    hist = [0] * n
    for p in trains:
        hist[M.rising_count(p) - 1] += 1
    return T.passes_from_r_hist(hist, k) | {"hist": hist}


def analyse_model_v(d: str, n: int, k: int, trials: int, seed: int) -> ModelV:
    trains = AR.model_v_trains(n, None if d == "gleichverteilt" else float(d), trials, seed)
    st = _passes_stats(trains, k, n)
    uniform = AR.model_v_trains(n, None, trials, seed + 1)
    ust = _passes_stats(uniform, k, n)
    s = EX.summary(n, k)
    return ModelV(n, k, d, trials, st["radix"], st["mean"], st["one_or_less"], st["below_radix"], st["mean_r"], tuple(st["hist"]), trains[0],
                  float(s.mean), (n + 1) / 2, ust["mean"])


def verdict_model_v(a: ModelV) -> tuple[str, str]:
    wo = "gleichverteilt (jede Folge gleich wahrscheinlich)" if a.d == "gleichverteilt" else f"D = {a.d.replace('.', ',')}"
    text = (f"n = {a.n}, k = {a.k}, Radix {a.radix}; {wo}: im Mittel **{de(a.mean_passes)} Durchgänge** (Mittel von R: {de(a.mean_r, 1)}), "
            f"{pct1(a.one_or_less)} der Folgen mit höchstens einem Durchgang, {pct1(a.below_radix)} unter Radix ({thousands(a.trials)} Folgen aus Modell V, ausgedacht). "
            f"Zum Vergleich gleichverteilt exakt: {de(a.uniform_exact_mean)} Durchgänge, Mittel von R {de(a.uniform_exact_mean_r, 1)}.")
    return ("success" if a.mean_passes + 0.5 <= a.radix else "info"), text


# ---------------------------------------------------------------- Experiment 5: Gruppen


def parse_word(text: str):
    """Text wie „3, 3, 2, 2, 1, 1“ → (Wort, None) oder (None, Meldung): Gruppen 1..7, 2 bis 40 Wagen."""
    if len(text) > 4 * C.E5_N_MAX:
        return None, "Der Eintrag ist zu lang."
    parts = [s for s in text.replace(";", " ").replace(",", " ").split() if s]
    try:
        word = tuple(int(s) for s in parts)
    except ValueError:
        return None, "Bitte ganze Zahlen eintragen, getrennt durch Komma oder Leerzeichen."
    if not 2 <= len(word) <= C.E5_N_MAX:
        return None, f"Der Zug braucht 2 bis {C.E5_N_MAX} Wagen (eingetragen: {len(word)})."
    if min(word) < 1 or max(word) > C.E5_M_MAX:
        return None, f"Die Gruppennummern müssen zwischen 1 und {C.E5_M_MAX} liegen."
    return word, None


@dataclass(frozen=True)
class WordExample:
    word: tuple
    m: int
    order: str
    k: int
    passes_fixed: int
    passes_free: int
    radix_present: int
    plan: tuple
    final: tuple
    goal_ok: bool
    best_ranks: tuple                 # Rang je Gruppe 1..m der Reihenfolge, nach der der Plan arbeitet
    labels: tuple
    L: int
    source: str                       # "eingetragen" oder "Zufallszug"


def analyse_word(word, m: int, k: int, order: str, source: str) -> WordExample:
    fixed = W.passes_fixed(word, k)
    free, best_ranks, _ = W.passes_free(word, m, k)
    if order == C.E5_ORDER_FIXED:
        ranks_of_group = tuple(range(m))
    else:
        ranks_of_group = best_ranks
    car_ranks = [ranks_of_group[g - 1] for g in word]
    labels = W.labels_for_ranks(car_ranks)
    pl = M.plan_from_labels(tuple(word), labels, k)
    final = M.play(word, [x.assign for x in pl], k)
    goal_ok = W.is_sorted_word(final) if order == C.E5_ORDER_FIXED else W.is_grouped(final)
    return WordExample(tuple(word), m, order, k, fixed, free, W.radix_present(word, k), tuple(pl), final, goal_ok, ranks_of_group, labels, max(labels) + 1, source)


def verdict_word(e: WordExample) -> tuple[str, str]:
    return "info", (f"Beispielzug ({e.source}) {train_text(e.word)}: bei **fester** Reihenfolge der Gruppen {e.passes_fixed} Durchgänge (L = {W.label_count([g for g in e.word])}), "
                    f"bei **freier** Reihenfolge {e.passes_free}; Radix aus den vorhandenen Gruppen: {e.radix_present}. "
                    f"Der abgespielte Plan ({'fest' if e.order == C.E5_ORDER_FIXED else 'frei'}, {len(e.plan)} Durchgänge) erreicht das Ziel: {'ja' if e.goal_ok else 'NEIN'}.")


@dataclass(frozen=True)
class GroupStats:
    m: int
    n: int
    k: int
    trials: int
    asked_trials: int
    seed: int
    free_lt_present: int
    fixed_lt_present: int
    mean_radix: float
    mean_fixed: float
    mean_free: float


def analyse_groups(m: int, n: int, k: int, trials: int, seed: int) -> GroupStats:
    eff = min(trials, C.E5_TRIAL_CAP[m])
    rng = SplitMix64(seed)
    free_lt = fixed_lt = 0
    s_rad = s_fix = s_free = 0
    for _ in range(eff):
        word = AR.random_word(n, m, rng)
        fixed = W.passes_fixed(word, k)
        free, _, _ = W.passes_free(word, m, k)
        rad = W.radix_present(word, k)
        free_lt += free < rad
        fixed_lt += fixed < rad
        s_rad += rad
        s_fix += fixed
        s_free += free
    return GroupStats(m, n, k, eff, trials, seed, free_lt, fixed_lt, s_rad / eff, s_fix / eff, s_free / eff)


def verdict_groups(g: GroupStats) -> tuple[str, str]:
    text = (f"{g.m} Gruppen, {g.k} Gleise, {g.n} Wagen ({thousands(g.trials)} Züge, jeder Wagen gleichverteilt in eine Gruppe, Zufalls-Seed {g.seed}): "
            f"bei **freier** Reihenfolge unterbietet die exakte Mindestzahl Radix (aus den vorhandenen Gruppen) in {pct1(Fraction(g.free_lt_present, g.trials))} der Züge, "
            f"bei **fester** Reihenfolge (Sortieren) in {pct1(Fraction(g.fixed_lt_present, g.trials))}. "
            f"Mittel Durchgänge: Radix {de(g.mean_radix, 2)}, fest {de(g.mean_fixed, 2)}, frei {de(g.mean_free, 2)}.")
    if g.asked_trials > g.trials:
        text += f" (Bei {g.m} Gruppen rechnet die App höchstens {g.trials} Züge.)"
    return ("success" if g.free_lt_present > g.trials // 2 else "info"), text


# ---------------------------------------------------------------- Kernfragen


def kernfrage_texts(a1: OneTrain, d2: Distribution, g5: GroupStats) -> tuple[str, str, str]:
    """Kurzantworten der drei Kernfragen (Beschriftung der Metriken)."""
    q1 = "–" if a1.error else f"{a1.passes} Durchgänge bei R = {a1.r}"
    q2 = f"Mittel {de(float(d2.summary.mean), 3)} gegen Radix {d2.summary.radix}"
    q3 = f"{pct1(Fraction(g5.free_lt_present, g5.trials))} unter Radix (frei)"
    return q1, q2, q3
