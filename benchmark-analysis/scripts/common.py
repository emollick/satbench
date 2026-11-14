"""Shared data layer and chart style for the Benchmark Almanac analyses.

Data: scripts/summaries.json, dumped from the site's own TypeScript data layer
(src/lib/data.ts benchSummary()) so every number matches benchmarkalmanac.com.
"""
import json
import os
from functools import lru_cache

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))  # benchmark-analysis/scripts
REPO = os.path.join(HERE, "repo")  # almanac clone, made by run.sh
SUMMARIES = os.path.join(HERE, "summaries.json")  # written by dump.ts
OUT = os.path.dirname(HERE)  # PNGs go to benchmark-analysis/<analysis>/

AREA_NAMES = {
    "knowledge": "Knowledge & language",
    "reasoning": "Math & science",
    "code": "Coding",
    "agents": "Agents & tools",
    "work": "Professional work",
    "multimodal": "Vision, audio & robotics",
    "safety": "Safety & security",
    "other": "Other",
}
# Fixed categorical order (validated reference palette, light mode). Color follows the area, always.
AREA_COLORS = {
    "knowledge": "#2a78d6",
    "reasoning": "#eb6834",
    "code": "#1baf7a",
    "agents": "#6250d6",
    "work": "#e87ba4",
    "multimodal": "#008300",
    "safety": "#e34948",
    "other": "#8a8984",
}
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e6e5e0"
SURFACE = "#fcfcfb"
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
DIVERGING = ("#2a78d6", "#f0efec", "#e34948")  # blue (neg) - gray - red (pos)

SOURCE_LINE = "Data: Benchmark Almanac (benchmarkalmanac.com), including Epoch AI Benchmarking Hub (CC BY 4.0). Data as of Nov 14, 2026."


# ---------------------------------------------------------------- data
@lru_cache
def raw():
    return json.load(open(SUMMARIES))


@lru_cache
def benches() -> pd.DataFrame:
    """One row per benchmark with metadata, launch-post status and saturation dates."""
    rows = []
    for b in raw()["benches"]:
        rows.append({
            "id": b["id"], "name": b["name"], "area": b["area"], "area_name": AREA_NAMES[b["area"]],
            "category": b.get("category"), "subcategory": b.get("subcategory"), "level": b.get("level"),
            "scoring": b.get("scoring"), "format": b.get("format"), "unit": b.get("unit") or "%",
            "better": b.get("better") or "higher", "released": b.get("released"), "family": b.get("family"),
            "successor": b.get("successor"), "status": b["status"], "why": b.get("why"),
            "first_cited": b.get("first"), "last_cited": b.get("last"), "n_cites": b["ncites"],
            "n_cite_labs": len(b["citeLabs"]), "n_doc_cites": b["ndoc"],
            "saturated_at": b.get("saturatedAt"), "near_ceiling_at": b.get("nearCeilingAt"),
            "board_source": b.get("boardSource"), "n_board": len(b["board"]), "n_scores_any": b["nScores"],
        })
    return pd.DataFrame(rows).set_index("id")


@lru_cache
def models() -> pd.DataFrame:
    m = pd.DataFrame(json.load(open(f"{REPO}/data/models.json"))).set_index("id")
    m["released"] = pd.to_datetime(m["released"], errors="coerce")
    return m


@lru_cache
def scores() -> pd.DataFrame:
    """Long table: one score per (benchmark, model), from the benchmark's lead board only.

    The lead board is the single source the site shows for that benchmark (its official leaderboard, else
    Epoch AI's runs, else a board Epoch copied, else labs' launch-post claims). Using one source per benchmark
    keeps every column internally consistent; it is best score per model across settings on that source.
    """
    rows = []
    for b in raw()["benches"]:
        for model, value, date, src in b["board"]:
            rows.append((b["id"], model, value, date, src))
    df = pd.DataFrame(rows, columns=["bench", "model", "value", "date", "source"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    mm = models()
    df["model_released"] = df["model"].map(mm["released"])
    df["lab"] = df["model"].map(mm["lab"])
    # orient so higher is always better
    lower = benches()["better"].eq("lower")
    df.loc[df["bench"].map(lower), "value"] *= -1
    return df


def matrix(min_models=20, min_benches=1, exclude_areas=(), units=None) -> pd.DataFrame:
    """Model x benchmark matrix (higher = better) of lead-board scores. NaN where missing (most cells)."""
    s = scores()
    b = benches()
    keep = b[(b["n_board"] >= min_models) & ~b["area"].isin(exclude_areas)]
    if units is not None:
        keep = keep[keep["unit"].isin(units)]
    s = s[s["bench"].isin(keep.index)]
    M = s.pivot_table(index="model", columns="bench", values="value", aggfunc="max")
    M = M.loc[M.notna().sum(axis=1) >= min_benches]
    return M


# ---------------------------------------------------------------- style
def setup_style():
    for f in font_manager.findSystemFonts():
        if "/inter/" in f.lower():
            try:
                font_manager.fontManager.addfont(f)
            except Exception:
                pass
    plt.rcParams.update({
        "font.family": "Inter",
        "font.size": 13,
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
        "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 12, "ytick.labelsize": 12,
        "axes.facecolor": SURFACE, "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "legend.frameon": False, "legend.fontsize": 12,
        "axes.titlesize": 14, "axes.labelsize": 13,
    })


def new_figure(width_in=12, height_in=6.75, top=0.80, bottom=0.12, left=0.08, right=0.97):
    """A figure with room for a two-line header and a footer. 12x6.75in at dpi=200 -> 2400x1350 (16:9).
    Use width_in=10, height_in=10 for a square (1080x1080-friendly) post, or 10x12.5 for 4:5."""
    setup_style()
    fig = plt.figure(figsize=(width_in, height_in))
    fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right)
    return fig


def header(fig, title, subtitle=None, x=0.04):
    fig.text(x, 0.965, title, ha="left", va="top", fontsize=22, fontweight="bold", color=INK)
    if subtitle:
        fig.text(x, 0.905, subtitle, ha="left", va="top", fontsize=13.5, color=INK2, linespacing=1.35)


def footer(fig, note=None, x=0.04):
    txt = SOURCE_LINE if not note else f"{note}\n{SOURCE_LINE}"
    fig.text(x, 0.018, txt, ha="left", va="bottom", fontsize=10, color=MUTED, linespacing=1.4)


def save(fig, path):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def area_legend_handles(areas):
    from matplotlib.lines import Line2D
    return [Line2D([0], [0], marker="o", lw=0, markersize=10, markerfacecolor=AREA_COLORS[a],
                   markeredgecolor="white", label=AREA_NAMES[a]) for a in areas]
