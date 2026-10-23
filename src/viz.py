"""Figures for the Vietnam remittance study. Every function saves a PNG and returns its path."""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

from .analysis import vietnam
from .data import END_YEAR, START_YEAR

FIG_DIR = Path(__file__).resolve().parents[1] / "reports" / "figures"

REMIT = "#1f6feb"   # remittances
FDI = "#f0883e"     # FDI
VN = "#d1242f"      # Vietnam highlight
MUTED = "#8b949e"

sns.set_theme(style="whitegrid", context="talk", font_scale=0.7)
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 110, "savefig.dpi": 200,
                     "grid.color": "#e6e8eb", "grid.linewidth": 0.8, "axes.titleweight": "bold"})


def _save(fig, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _usd_axis(ax, axis="y"):
    fmt = mtick.FuncFormatter(lambda v, _: f"{v / 1000:,.0f}k" if v >= 1000 else f"{v:,.0f}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def vietnam_trend(panel):
    vn = vietnam(panel)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(vn.index, vn["Remittances"], color=REMIT, marker="o", lw=2.5)
    drops = vn[vn["Remit_YoY_pct"] < 0]
    ax.scatter(drops.index, drops["Remittances"], color=VN, zorder=5, s=70, label="Year-on-year decline")
    ax.annotate(f"{vn['Remittances'][START_YEAR]:,.0f}", (START_YEAR, vn["Remittances"][START_YEAR]),
                textcoords="offset points", xytext=(0, -22), ha="center", color=REMIT, fontweight="bold")
    ax.annotate(f"{vn['Remittances'][END_YEAR]:,.0f}", (END_YEAR, vn["Remittances"][END_YEAR]),
                textcoords="offset points", xytext=(-6, 10), ha="right", color=REMIT, fontweight="bold")
    ax.set(title="Remittance inflows to Vietnam grew ~10x between 2000 and 2024",
           xlabel="", ylabel="US$ million")
    ax.set_xticks(range(START_YEAR, END_YEAR + 1, 2))
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylim(0)
    ax.legend(frameon=False, loc="upper left")
    return _save(fig, "01_vietnam_remittance_trend")


def remittances_vs_fdi(panel):
    vn = vietnam(panel)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(vn.index, vn["Remittances"], color=REMIT, marker="o", lw=2.5, label="Remittances")
    ax.plot(vn.index, vn["FDI"], color=FDI, marker="o", lw=2.5, label="FDI net inflows")
    ax.fill_between(vn.index, vn["Remittances"], vn["FDI"], where=vn["Remittances"] >= vn["FDI"],
                    color=REMIT, alpha=0.15, interpolate=True, label="Remittances > FDI")
    ax.set(title="Remittances tracked FDI closely until 2014; FDI has pulled ahead since",
           xlabel="", ylabel="US$ million")
    ax.set_xticks(range(START_YEAR, END_YEAR + 1, 2))
    ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False, loc="upper left")
    return _save(fig, "02_remittances_vs_fdi")


def asean_trends(panel):
    data = panel.dropna(subset=["Remittances"])
    big = ["Philippines", "Vietnam", "Indonesia", "Thailand"]
    palette = {"Philippines": "#2da44e", "Vietnam": VN, "Indonesia": "#8250df", "Thailand": "#bf8700"}
    fig, ax = plt.subplots(figsize=(11.5, 6))
    for c, g in data.groupby("Country"):
        if c in big:
            ax.plot(g["Year"], g["Remittances"], color=palette[c], lw=3 if c == "Vietnam" else 2.2)
            dy = {"Indonesia": 9, "Vietnam": -9}.get(c, 0)  # separate the two overlapping end labels
            ax.annotate(c, (g["Year"].iloc[-1], g["Remittances"].iloc[-1]), xytext=(6, dy),
                        textcoords="offset points", va="center", color=palette[c], fontweight="bold")
        else:
            ax.plot(g["Year"], g["Remittances"], color=MUTED, lw=1.2, alpha=0.6)
    ax.annotate("Other ASEAN economies", (2011, 3300), color=MUTED, fontsize=10)
    ax.set(title="ASEAN remittance inflows: the Philippines leads, Vietnam is in the second tier",
           xlabel="", ylabel="US$ million", xlim=(START_YEAR, END_YEAR + 3), ylim=(0, None))
    ax.set_xticks(range(START_YEAR, END_YEAR + 1, 2))
    ax.tick_params(axis="x", rotation=45)
    _usd_axis(ax)
    return _save(fig, "03_asean_remittance_trends")


def asean_2024_ranking(snapshot):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = [VN if c == "Vietnam" else "#9ecbff" for c in snapshot["Country"]]
    bars = ax.barh(snapshot["Country"], snapshot["Remittances"], color=colors)
    ax.invert_yaxis()
    for b, v in zip(bars, snapshot["Remittances"]):
        ax.text(v + 300, b.get_y() + b.get_height() / 2, f"{v:,.0f}", va="center", fontsize=10)
    ax.set(title=f"ASEAN remittance inflows in {END_YEAR} (US$ million)", xlabel="", ylabel="")
    ax.set_xlim(0, snapshot["Remittances"].max() * 1.12)
    ax.grid(axis="y", visible=False)
    return _save(fig, "04_asean_2024_ranking")


def remittance_gdp_share(panel):
    data = panel.dropna(subset=["Remit_pct_GDP"])
    keep = ["Philippines", "Cambodia", "Vietnam", "Thailand", "Indonesia"]
    palette = dict(zip(keep, ["#2da44e", "#0969da", VN, "#bf8700", "#8250df"]))
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for c in keep:
        g = data[data["Country"] == c]
        ax.plot(g["Year"], g["Remit_pct_GDP"], color=palette[c], lw=3 if c == "Vietnam" else 2)
        ax.annotate(c, (g["Year"].iloc[-1], g["Remit_pct_GDP"].iloc[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", color=palette[c], fontweight="bold")
    ax.set(title="Remittances as a share of GDP, selected ASEAN economies",
           xlabel="", ylabel="% of GDP", xlim=(START_YEAR, END_YEAR + 3), ylim=(0, None))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xticks(range(START_YEAR, END_YEAR + 1, 2))
    ax.tick_params(axis="x", rotation=45)
    return _save(fig, "05_remittances_share_of_gdp")


def remittance_fdi_ratio(panel):
    vn = vietnam(panel)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.axhline(1, color=MUTED, ls="--", lw=1.2)
    ax.plot(vn.index, vn["Remit_to_FDI"], color=REMIT, marker="o", lw=2.5)
    ax.fill_between(vn.index, 1, vn["Remit_to_FDI"], where=vn["Remit_to_FDI"] >= 1,
                    color=REMIT, alpha=0.15, interpolate=True)
    ax.text(START_YEAR + 0.2, 1.03, "Remittances = FDI", color=MUTED, fontsize=10)
    ax.set(title="Vietnam: remittances per US$1 of FDI inflow", xlabel="", ylabel="Ratio")
    ax.set_xticks(range(START_YEAR, END_YEAR + 1, 2))
    ax.tick_params(axis="x", rotation=45)
    return _save(fig, "06_remittance_to_fdi_ratio")
