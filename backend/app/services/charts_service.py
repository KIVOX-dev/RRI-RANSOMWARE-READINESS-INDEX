"""Server-side chart rendering for PDF reports (matplotlib, Agg backend —
no display server required). Returns base64 PNG data URIs ready to embed in
Jinja2/WeasyPrint HTML."""
import base64
import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ACCENT = "#ecf95a"
BG = "#191314"
LIGHT = "#f4f4f4"


def _fig_to_data_uri(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()


def radar_chart(domain_scores: list[dict]) -> str:
    labels = [d["domain"] for d in domain_scores]
    values = [d["maturity_score"] for d in domain_scores]
    if not labels:
        labels, values = ["No data"], [0]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True}, facecolor=BG)
    ax.set_facecolor(BG)
    ax.plot(angles, values, color=ACCENT, linewidth=2)
    ax.fill(angles, values, color=ACCENT, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=LIGHT, size=8)
    ax.set_ylim(0, 5)
    ax.tick_params(colors=LIGHT)
    ax.spines["polar"].set_color(LIGHT)
    ax.set_title("Domain Maturity (0-5)", color=LIGHT, pad=20)
    return _fig_to_data_uri(fig)


def assurance_gauge(assurance_score: float) -> str:
    fig, ax = plt.subplots(figsize=(5, 5), facecolor=BG)
    ax.set_facecolor(BG)
    remainder = max(0, 100 - assurance_score)
    ax.pie(
        [assurance_score, remainder],
        colors=[ACCENT, "#3a3335"],
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.35, "edgecolor": BG},
    )
    ax.text(0, 0, f"{assurance_score:.0f}%", ha="center", va="center", color=LIGHT, fontsize=28, weight="bold")
    ax.set_title("Assurance Score", color=LIGHT, pad=10)
    return _fig_to_data_uri(fig)


def impact_effort_quadrant(remediation_items: list[dict]) -> str:
    fig, ax = plt.subplots(figsize=(6, 5), facecolor=BG)
    ax.set_facecolor(BG)
    effort_x = {"low": 0.25, "high": 0.75}
    impact_y = {"low": 0.2, "medium": 0.5, "high": 0.85}
    for item in remediation_items:
        x = effort_x.get(item["effort"], 0.5)
        y = impact_y.get(item["impact"], 0.5)
        ax.scatter(x + np.random.uniform(-0.08, 0.08), y + np.random.uniform(-0.05, 0.05), color=ACCENT, s=40, alpha=0.85)

    ax.axvline(0.5, color=LIGHT, linewidth=0.5, alpha=0.4)
    ax.axhline(0.5, color=LIGHT, linewidth=0.5, alpha=0.4)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([0.25, 0.75])
    ax.set_xticklabels(["Low Effort", "High Effort"], color=LIGHT)
    ax.set_yticks([0.25, 0.75])
    ax.set_yticklabels(["Low Impact", "High Impact"], color=LIGHT)
    ax.tick_params(colors=LIGHT)
    for spine in ax.spines.values():
        spine.set_color(LIGHT)
    ax.set_title("Remediation: Impact vs Effort", color=LIGHT)
    return _fig_to_data_uri(fig)
