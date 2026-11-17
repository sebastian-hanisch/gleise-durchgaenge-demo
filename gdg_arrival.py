"""Wie ein Zug ankommt: Zufallszug, Modell V (ausgedacht) und Zufallswörter mit Gruppen.

Das Modell ist **kein Fall und keine reale Ankunftsfolge**: n Wagen kommen zu den Zeiten 1, 2, …, n an; Wagen i bleibt eine exponentialverteilte
Verweilzeit (Mittel D, in Ankunftsabständen) und fährt zur Zeit i + Verweilzeit ab. Der Abfahrtsrang ist die Stelle in der Reihenfolge der
Abfahrtszeiten (Gleichstände stabil nach dem Index). Kleines D heißt fast sortiert, D → ∞ heißt jede Reihenfolge gleich wahrscheinlich.
Der Zufall kommt nur aus dem SplitMix64 (`gdg_rng.py`), also auf jeder Plattform bitgleich."""

from gdg_rng import SplitMix64


def random_train(n: int, seed: int) -> tuple[int, ...]:
    """Jede der n! Folgen gleich wahrscheinlich (Fisher-Yates mit SplitMix64)."""
    items = list(range(1, n + 1))
    SplitMix64(seed).shuffle(items)
    return tuple(items)


def ranks_from_times(times: list[float]) -> tuple[int, ...]:
    """Rang je Wagen in der Reihenfolge der Abfahrtszeiten; Gleichstände stabil nach dem Index (Ankunft)."""
    order = sorted(range(len(times)), key=lambda i: (times[i], i))
    ranks = [0] * len(times)
    for rank, i in enumerate(order, start=1):
        ranks[i] = rank
    return tuple(ranks)


def model_v_train(n: int, mean_dwell: float, rng: SplitMix64) -> tuple[int, ...]:
    """Ein Zug aus Modell V; `mean_dwell` ist D. Mit D <= 0 fahren die Wagen in Ankunftsreihenfolge ab (Identität)."""
    if mean_dwell <= 0:
        return tuple(range(1, n + 1))
    times = [i + rng.expovariate(mean_dwell) for i in range(1, n + 1)]
    return ranks_from_times(times)


def model_v_trains(n: int, mean_dwell: float | None, trials: int, seed: int) -> list[tuple[int, ...]]:
    """`trials` Züge aus einem Strom. `mean_dwell=None` heißt gleichverteilt (jede der n! Folgen gleich wahrscheinlich)."""
    rng = SplitMix64(seed)
    out = []
    for _ in range(trials):
        if mean_dwell is None:
            items = list(range(1, n + 1))
            rng.shuffle(items)
            out.append(tuple(items))
        else:
            out.append(model_v_train(n, mean_dwell, rng))
    return out


def random_word(n: int, m: int, rng: SplitMix64) -> tuple[int, ...]:
    """Ein Zug mit Zielgruppen 1..m: jeder der n Wagen unabhängig gleichverteilt in eine Gruppe."""
    return tuple(rng.below(m) + 1 for _ in range(n))
