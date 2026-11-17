"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import gdg_constants as C
from gdg_model import radix


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def color_for(index: int) -> str:
    return C.COLORS[index % len(C.COLORS)]


def build_states_figure(rows, color_index):
    """Der Zug vor dem ersten und nach jedem Durchgang: eine Zeile je Zustand, ein Kästchen je Wagen (Zahl = Rang bzw. Gruppe), Farbe = `color_index(Wert)`.

    `rows`: Liste von (Zeilenname, Folge). Beschriftung der Zeilen als Text auf der y-Achse (kategorisch, damit Plotly keine lineare Achse anlegt)."""
    fig = go.Figure()
    names = [name for name, _ in rows]
    longest = max((len(seq) for _, seq in rows), default=1)
    for name, seq in rows:
        fig.add_trace(go.Scatter(
            x=list(range(1, len(seq) + 1)), y=[name] * len(seq), mode="markers+text", text=[str(v) for v in seq], textposition="middle center",
            marker=dict(symbol="square", size=30, color=[color_for(color_index(v)) for v in seq], line=dict(width=1, color="rgba(0,0,0,0.35)")),
            textfont=dict(color="white", size=14), showlegend=False, hovertemplate="Stelle %{x}: %{text}<extra></extra>"))
    fig.update_xaxes(range=[0.4, longest + 0.6], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(categoryorder="array", categoryarray=names[::-1], showgrid=False)
    return _base(fig, height=70 + 62 * len(rows))


def build_distribution_figure(summary):
    """Anteil der Folgen je Zahl Durchgänge (alle n! Folgen gleich wahrscheinlich); die Radix-Zahl ist rot."""
    ts = sorted(summary.counts)
    shares = [summary.counts[t] / summary.total for t in ts]
    colors = [C.COLOR_RADIX if t == summary.radix else C.COLOR_BAR for t in ts]
    fig = go.Figure(go.Bar(x=[str(t) for t in ts], y=[100 * s for s in shares], marker_color=colors,
                           hovertemplate="%{x} Durchgänge: %{y:.4f} % der Folgen<extra></extra>"))
    fig.update_xaxes(title_text="Mindestzahl Durchgänge (rot: Radix)")
    fig.update_yaxes(title_text="Anteil der Folgen (%)", range=[0, 100])
    return _base(fig, height=320)


def build_sawtooth_figure(data, powers, k):
    """Anteil der Folgen mit weniger Durchgängen als Radix gegen n (exakt), Marken bei den Potenzen n = k^r."""
    ns = sorted(n for n in data if C.E3_N_FROM <= n <= C.E3_N_TO)
    fig = go.Figure(go.Scatter(x=ns, y=[data[n][0] for n in ns], mode="lines", line=dict(color=C.COLOR_BAR, width=2), name="Anteil unter Radix",
                               hovertemplate="n = %{x}: %{y:.4f}<extra></extra>"))
    if powers:
        fig.add_trace(go.Scatter(x=[n for n, _, _ in powers], y=[s for _, s, _ in powers], mode="markers", marker=dict(color=C.COLOR_RADIX, size=11, symbol="diamond"),
                                 name=f"n = {k}^r", hovertemplate="n = %{x}: %{y:.4f}<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Wagen n")
    fig.update_yaxes(title_text="Anteil der Folgen unter Radix", range=[-0.03, 1.03])
    return _base(fig)


def build_sawtooth_mean_figure(data, k):
    """Mittlere Zahl Durchgänge (exakt) gegen Radix, n = 20..200."""
    ns = sorted(n for n in data if C.E3_N_FROM <= n <= C.E3_N_TO)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[radix(n, k) for n in ns], mode="lines", line=dict(color=C.COLOR_RADIX, width=2, shape="hv"), name="Radix",
                             hovertemplate="n = %{x}: %{y}<extra></extra>"))
    fig.add_trace(go.Scatter(x=ns, y=[data[n][1] for n in ns], mode="lines", line=dict(color=C.COLOR_MEAN, width=3), name="Mittel (exakt)",
                             hovertemplate="n = %{x}: %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title_text="Zahl der Wagen n")
    fig.update_yaxes(title_text="Durchgänge")
    return _base(fig)


def build_r_histogram_figure(r_hist, expected_mean):
    """Verteilung von R (Zahl der steigenden Folgen) in den gezogenen Folgen; die Raute ist der Erwartungswert (n + 1)/2 bei gleichverteilten Folgen."""
    total = sum(r_hist)
    fig = go.Figure(go.Bar(x=list(range(1, len(r_hist) + 1)), y=[100 * c / total for c in r_hist], marker_color=C.COLOR_BAR, name="Modell V",
                           hovertemplate="R = %{x}: %{y:.1f} % der Folgen<extra></extra>"))
    fig.add_trace(go.Scatter(x=[expected_mean], y=[0], mode="markers", marker=dict(symbol="diamond", size=14, color=C.COLOR_RADIX), name="(n + 1)/2 bei gleichverteilten Folgen",
                             hovertemplate="Erwartung gleichverteilt: %{x}<extra></extra>"))
    fig.update_xaxes(title_text="Zahl R der steigenden Folgen")
    fig.update_yaxes(title_text="Anteil der Folgen (%)")
    return _base(fig, height=320)


def build_groups_figure(g):
    """Mittlere Zahl Durchgänge: Radix (vorhandene Gruppen), feste und freie Reihenfolge der Gruppen."""
    names = ["Radix", "exakt, feste Reihenfolge (Sortieren)", "exakt, freie Reihenfolge (Gruppieren)"]
    values = [g.mean_radix, g.mean_fixed, g.mean_free]
    fig = go.Figure(go.Bar(x=names, y=values, marker_color=[C.COLOR_RADIX, C.COLOR_BAR, C.COLOR_MEAN], text=[f"{v:.2f}".replace(".", ",") for v in values],
                           textposition="outside", hovertemplate="%{x}: %{y:.3f}<extra></extra>"))
    fig.update_yaxes(title_text="Durchgänge im Mittel", rangemode="tozero")
    return _base(fig, height=320)
