"""
Generate the chart figures embedded in 1a_CGL_Story_and_Report.md.

Run from the BKS/ directory:
    python build_story_figures.py

Outputs PNG files into BKS/figures/ named story_<slug>.png.
Each figure corresponds to one highlight in the public section of the report.

Sources of statistics (kept consistent with 1a_CGL_EDA.ipynb):
    - cgl_BKS_data.csv         personality, D/S, roles, soft erotic, emotion items
    - BKS_nsfw_preferences.csv NSFW acts/positions/common/uncommon + arousal scale items
"""

from __future__ import annotations

import re
import warnings
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FixedFormatter
from matplotlib.transforms import blended_transform_factory
from scipy.stats import (
    chi2_contingency,
    fisher_exact,
    kruskal,
    mannwhitneyu,
)

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)
DATA_DIR = HERE.parent / "database"

SAVE_KW = dict(dpi=160, bbox_inches="tight", facecolor="white")

# ---------------------------------------------------------------------------
# Palette — mirrors CHART_STYLE.md / viz/examples/render_all_examples.py
# ---------------------------------------------------------------------------
INK = {
    "primary":   "#1C1C1E",
    "secondary": "#444444",
    "tertiary":  "#8E8E93",
    "hairline":  "#C7C7CC",
    "surface":   "#F2F2F7",
    "canvas":    "#FFFFFF",
}
ACCENT = {"hero": "#FF66C4", "mid": "#FF8FB1", "soft": "#FFC1CC"}
SEMANTIC = {"good": "#34C759", "bad": "#FF3B30", "caution": "#FF9500"}
DIVERGING_DS = [
    "#1F4E79",   # totally sub  — deep blue
    "#4A7AB5",   # mod sub
    "#9DBADA",   # slight sub
    "#E5E5EA",   # switch / equal
    "#A3D4B0",   # slight dom
    "#5BAA7C",   # mod dom
    "#1F6E45",   # totally dom — deep green
]
TIER = {
    "strong":   "#FF66C4",
    "moderate": "#FF8FB1",
    "weak":     "#FFC1CC",
    "ns":       "#C7C7CC",
}

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.labelsize":    11,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   11,
    "axes.edgecolor":    INK["hairline"],
    "axes.linewidth":    0.8,
    "axes.labelcolor":   INK["secondary"],
    "axes.titlecolor":   INK["primary"],
    "axes.facecolor":    INK["canvas"],
    "figure.facecolor":  INK["canvas"],
    "xtick.color":       INK["tertiary"],
    "ytick.color":       INK["primary"],
    "savefig.facecolor": INK["canvas"],
})


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def load_main_df() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "cgl_BKS_data.csv")
    if "role_Nazis" in df.columns:
        df = df.drop(columns="role_Nazis")
    df["cgl_flag"] = np.where(
        df["cgl"] >= 1, "True",
        np.where(df["cgl"] == 0, "False", "Unknown"),
    )
    return df


def load_nsfw_df() -> pd.DataFrame:
    nsfw = pd.read_csv(DATA_DIR / "BKS_nsfw_preferences.csv")
    nsfw["cgl_flag"] = np.where(
        nsfw["cgl"] >= 1, "True",
        np.where(nsfw["cgl"] == 0, "False", "Unknown"),
    )
    return nsfw


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def cohens_d(a: pd.Series, b: pd.Series) -> float:
    a, b = a.dropna(), b.dropna()
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return np.nan
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    s_pool = np.sqrt(((na - 1) * var_a + (nb - 1) * var_b) / (na + nb - 2))
    if s_pool == 0:
        return 0.0
    return (a.mean() - b.mean()) / s_pool


def cohens_h(p1: float, p2: float) -> float:
    phi1 = 2 * np.arcsin(np.sqrt(np.clip(p1, 0, 1)))
    phi2 = 2 * np.arcsin(np.sqrt(np.clip(p2, 0, 1)))
    return phi1 - phi2


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    pvals = np.asarray(pvals, dtype=float)
    n = len(pvals)
    order = np.argsort(pvals)
    ranks = np.arange(1, n + 1)
    q_sorted = pvals[order] * n / ranks
    q_sorted = np.minimum.accumulate(q_sorted[::-1])[::-1]
    q_sorted = np.clip(q_sorted, 0.0, 1.0)
    out = np.empty(n)
    out[order] = q_sorted
    return out


def or_with_ci(a, b, c, d, z=1.96):
    if min(a, b, c, d) == 0:
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    or_ = (a * d) / (b * c)
    se = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return or_, float(np.exp(np.log(or_) - z * se)), float(np.exp(np.log(or_) + z * se))


# ---------------------------------------------------------------------------
# Figure 1: OCEAN + powerlessness Cohen's d
# ---------------------------------------------------------------------------

def figure_personality(df: pd.DataFrame) -> None:
    # Two conceptually distinct constructs: OCEAN traits (Big Five personality)
    # and Powerlessness (a locus-of-belief measure, NOT a personality trait).
    # We plot them in the same chart with a visual separator and grouped labels.
    ocean_traits = [
        ("openness", "Openness"),
        ("consciensiousness", "Conscientiousness"),
        ("extroversion", "Extraversion"),
        ("neuroticism", "Neuroticism"),
        ("agreeableness", "Agreeableness"),
    ]
    belief = [
        ("powerlessness", "Powerlessness"),
    ]
    cgl = df[df["cgl_flag"] == "True"]
    non = df[df["cgl_flag"] == "False"]

    rows = []
    for col, label in ocean_traits:
        rows.append({"trait": label, "group": "OCEAN (personality)", "d": cohens_d(cgl[col], non[col])})
    for col, label in belief:
        rows.append({"trait": label, "group": "Powerlessness (locus of belief)",
                     "d": cohens_d(cgl[col], non[col])})
    plot = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(12, 6.5))

    # Shade the "trivial" band (|d| < 0.10)
    ax.axvspan(-0.10, 0.10, color=INK["surface"], alpha=0.8, zorder=0,
               label="Trivial-effect band  |d| < 0.10")
    ax.axvline(0, color=INK["secondary"], lw=1.0, ls="--", zorder=1)

    # Plot OCEAN first (top), then a visual separator, then powerlessness
    y_positions = []
    y_cursor = 0
    for _ in ocean_traits:
        y_positions.append(y_cursor); y_cursor += 1
    y_cursor += 0.6  # gap between groups
    for _ in belief:
        y_positions.append(y_cursor); y_cursor += 1

    # All effects are trivial here; hairline gray with hero pink if one ever exceeds threshold
    colors = [INK["hairline"] if abs(d) < 0.10 else ACCENT["hero"] for d in plot["d"]]
    bars = ax.barh(y_positions, plot["d"], color=colors, edgecolor=INK["canvas"], zorder=2)
    for bar, d, y in zip(bars, plot["d"], y_positions):
        x = bar.get_width()
        ax.text(
            x + (0.005 if x >= 0 else -0.005), y,
            f"d = {d:+.3f}",
            va="center", ha="left" if x >= 0 else "right",
            fontsize=10, fontweight="bold", color=INK["primary"],
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(plot["trait"], fontsize=12, fontweight="bold", color=INK["secondary"])
    ax.invert_yaxis()

    # Group labels — plain text, no colored boxes
    ax.text(
        0.99, 0.95,
        "OCEAN — personality traits",
        transform=ax.transAxes,
        ha="right", va="top", fontsize=10, fontweight="bold", color=INK["secondary"],
    )
    ax.text(
        0.99, 0.18,
        "Powerlessness — locus-of-belief\n(not a personality trait)",
        transform=ax.transAxes,
        ha="right", va="top", fontsize=10, fontweight="bold", color=INK["secondary"],
    )

    ax.set_xlim(-0.25, 0.25)
    ax.set_xlabel("Cohen's d   (CGL-positive minus CGL-negative, pooled-SD units)", fontsize=11)
    ax.text(0, 1.08,
            "Personality (OCEAN) and Powerlessness (locus of belief):\n"
            "every CGL-vs-non-CGL difference falls inside the trivial-effect band",
            transform=ax.transAxes,
            fontsize=18, fontweight="bold", color=INK["primary"], va="bottom", ha="left")
    ax.text(
        -0.245, max(y_positions) + 0.7,
        f"n CGL+ = {len(cgl):,}   ·   n CGL− = {len(non):,}   ·   "
        "shaded band = |d| < 0.10 (trivial)",
        fontsize=9, color=INK["tertiary"], style="italic",
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color(INK["hairline"])
    ax.spines["bottom"].set_color(INK["hairline"])
    ax.grid(axis="x", linestyle=":", alpha=0.4, color=INK["hairline"], zorder=0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "story_01_personality.png", **SAVE_KW)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2: Emotional desires (youfeelmost + otherfeel1most)
# ---------------------------------------------------------------------------

def figure_emotion(df: pd.DataFrame) -> None:
    fields = ["youfeelmost", "otherfeel1most"]
    titles = ["What I most want to FEEL myself", "What I most want my PARTNER to feel"]
    MIN_PCT = 2.0

    def build_pct(col):
        sub = df.dropna(subset=[col]).copy()
        sub["cgl_flag"] = sub["cgl_flag"].astype(str)
        pivot = pd.crosstab(sub[col], sub["cgl_flag"], normalize="columns").mul(100)
        return pivot.reindex(columns=["False", "True", "Unknown"], fill_value=0)

    pct_left = build_pct(fields[0])
    pct_right = build_pct(fields[1])
    all_cats = pct_left.index.union(pct_right.index)
    pct_left = pct_left.reindex(all_cats, fill_value=0)
    pct_right = pct_right.reindex(all_cats, fill_value=0)
    max_per_cat = pd.concat([pct_left, pct_right], axis=1).max(axis=1)
    kept = max_per_cat[max_per_cat >= MIN_PCT].index
    pct_left = pct_left.loc[kept]
    pct_right = pct_right.loc[kept]

    abs_diff = pd.concat(
        [
            (pct_left["True"] - pct_left["False"]).abs(),
            (pct_right["True"] - pct_right["False"]).abs(),
        ],
        axis=1,
    ).max(axis=1)
    sort_order = abs_diff.sort_values(ascending=True).index
    pct_left = pct_left.loc[sort_order]
    pct_right = pct_right.loc[sort_order]

    n_left = df.dropna(subset=[fields[0]])["cgl_flag"].astype(str).value_counts()
    n_right = df.dropna(subset=[fields[1]])["cgl_flag"].astype(str).value_counts()

    xmax = max(pct_left.values.max(), pct_right.values.max()) * 1.10
    fig, axes = plt.subplots(1, 2, figsize=(16, max(6, 0.5 * len(sort_order))), sharey=True)
    color_map = {
        "False":   SEMANTIC["bad"],
        "True":    SEMANTIC["good"],
        "Unknown": INK["tertiary"],
    }
    size_map = {"False": 90, "True": 120, "Unknown": 80}

    def panel(ax, pct, title, n_counts):
        y_pos = np.arange(len(pct))
        for i, cat in enumerate(pct.index):
            ax.plot(
                [pct.loc[cat, "False"], pct.loc[cat, "True"]],
                [i, i], color=INK["hairline"], lw=2.0, zorder=1,
            )
        for flag in ["Unknown", "False", "True"]:
            ax.scatter(
                pct[flag].values, y_pos,
                color=color_map[flag], s=size_map[flag], zorder=3,
                label=f"CGL = {flag}  (n={int(n_counts.get(flag, 0)):,})",
                edgecolor=INK["canvas"], linewidth=1.2,
            )
        # Gap annotation — outside the right spine, never overlapping data
        _trans = blended_transform_factory(ax.transAxes, ax.transData)
        for i, cat in enumerate(pct.index):
            gap = pct.loc[cat, "True"] - pct.loc[cat, "False"]
            ax.text(1.02, i, f"{gap:+.1f}pp",
                    transform=_trans,
                    ha="left", va="center", fontsize=9, fontweight="bold",
                    color=INK["primary"], family="monospace", clip_on=False)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(pct.index, fontsize=12, fontweight="bold", color=INK["secondary"])
        ax.set_xlabel("% within group", fontsize=11)
        ax.set_xlim(0, xmax)
        ax.grid(axis="x", linestyle=":", alpha=0.4, color=INK["hairline"])
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines["left"].set_color(INK["hairline"])
        ax.spines["bottom"].set_color(INK["hairline"])
        # Legend on top, title above it
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0),
                  ncol=3, frameon=False, fontsize=10, labelcolor=INK["secondary"])
        ax.text(0, 1.14, title, transform=ax.transAxes,
                fontweight="bold", fontsize=13, color=INK["primary"], va="bottom")

    panel(axes[0], pct_left, titles[0], n_left)
    panel(axes[1], pct_right, titles[1], n_right)

    fig.suptitle(
        "CGL respondents want complementary emotions — powerless for self, powerful for partner",
        fontweight="bold", fontsize=14, y=0.99,
    )
    fig.text(
        0.5, 0.94,
        "% choosing each emotion as most-wanted to feel (left) or most-wanted partner to feel (right)",
        ha="center", va="top", fontsize=10, style="italic", color=INK["secondary"],
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(FIG_DIR / "story_02_emotion.png", **SAVE_KW)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3: D/S preference diverging Likert
# ---------------------------------------------------------------------------

def figure_ds(df: pd.DataFrame) -> None:
    ds_order = [
        "Totally submissive",
        "Moderately submissive",
        "Slightly submissive",
        "Switch/equal/no preference",
        "Slightly dominant",
        "Moderately dominant",
        "Totally dominant",
    ]
    ds_rank = {cat: i + 1 for i, cat in enumerate(ds_order)}
    ds_colors = DIVERGING_DS
    color_map = dict(zip(ds_order, ds_colors))

    plot_df = df.copy()
    plot_df["cgl_flag"] = plot_df["cgl_flag"].astype(str)
    plot_df = plot_df.dropna(subset=["ds_preference"])
    flag_order = ["False", "True", "Unknown"]
    n_per_flag = plot_df["cgl_flag"].value_counts()
    pivot = (
        pd.crosstab(plot_df["cgl_flag"], plot_df["ds_preference"], normalize="index")
        .mul(100)
        .reindex(index=flag_order, columns=ds_order, fill_value=0)
    )
    switch_idx = ds_order.index("Switch/equal/no preference")

    fig, (ax_chart, ax_stats) = plt.subplots(
        2, 1, figsize=(14, 8.5),
        gridspec_kw={"height_ratios": [3, 1.3]},
    )
    bar_height = 0.55
    for row_i, flag in enumerate(flag_order):
        row = pivot.loc[flag]
        sub_total = row.iloc[:switch_idx].sum()
        equal_total = row.iloc[switch_idx]
        dom_total = row.iloc[switch_idx + 1:].sum()
        left_edge = -equal_total / 2 - sub_total
        cursor = left_edge
        for cat in ds_order:
            width = row[cat]
            ax_chart.barh(
                row_i, width, left=cursor, height=bar_height,
                color=color_map[cat], edgecolor="white", linewidth=0.5,
            )
            if width > 3:
                ax_chart.text(
                    cursor + width / 2, row_i, f"{width:.0f}%",
                    ha="center", va="center", fontsize=8, fontweight="bold",
                    color="white" if cat != "Switch/equal/no preference" else "black",
                )
            cursor += width
        sub_center = -equal_total / 2 - sub_total / 2
        dom_center = equal_total / 2 + dom_total / 2
        label_y = row_i + bar_height / 2 + 0.05
        ax_chart.text(sub_center, label_y, f"Sub  {sub_total:.0f}%", ha="center", va="bottom",
                      fontsize=14, fontweight="bold", color=DIVERGING_DS[0])
        ax_chart.text(0, label_y, f"Equal  {equal_total:.0f}%", ha="center", va="bottom",
                      fontsize=14, fontweight="bold", color=INK["tertiary"])
        ax_chart.text(dom_center, label_y, f"Dom  {dom_total:.0f}%", ha="center", va="bottom",
                      fontsize=14, fontweight="bold", color=DIVERGING_DS[6])

    y_pos = np.arange(len(flag_order))
    ax_chart.set_yticks(y_pos)
    ax_chart.set_yticklabels([])
    ax_chart.tick_params(axis="y", length=0)
    ax_chart.set_ylim(-0.6, len(flag_order) - 0.4)
    trans = ax_chart.get_yaxis_transform()
    for i, flag in enumerate(flag_order):
        n = int(n_per_flag.get(flag, 0))
        ax_chart.text(-0.01, i + 0.08, f"CGL = {flag}", transform=trans,
                      ha="right", va="bottom", fontsize=11, fontweight="bold")
        ax_chart.text(-0.01, i - 0.08, f"(n = {n:,})", transform=trans,
                      ha="right", va="top", fontsize=9)
    existing_ticks = ax_chart.get_xticks()
    ax_chart.xaxis.set_major_locator(FixedLocator([t for t in existing_ticks if t != 0]))
    ax_chart.set_xlabel('Percentage points (centered on "Switch/equal")')
    ax_chart.spines[["top", "right", "left"]].set_visible(False)
    ax_chart.set_title(
        "Dominance / Submission Preference by CGL Group",
        fontsize=16, fontweight="bold", loc="center", pad=70,
    )
    legend_handles = [Patch(color=ds_colors[i], label=ds_order[i]) for i in range(len(ds_order))]
    ax_chart.legend(
        handles=legend_handles, bbox_to_anchor=(0.5, 1.02), loc="lower center",
        ncol=4, frameon=False, fontsize=9,
    )

    # Stats panel
    plot_df["ds_rank"] = plot_df["ds_preference"].map(ds_rank)
    groups = {f: plot_df.loc[plot_df["cgl_flag"] == f, "ds_rank"].values for f in flag_order}
    groups = {f: g for f, g in groups.items() if len(g) > 0}
    stat, p_kw = kruskal(*groups.values())
    n_total = sum(len(g) for g in groups.values())
    k = len(groups)
    eta = max(0.0, (stat - k + 1) / (n_total - k)) if n_total > k else 0.0

    def sig_marker(p):
        if p < 0.001: return "***"
        if p < 0.01: return "**"
        if p < 0.05: return "*"
        return "ns"

    stat_lines = [
        f"Kruskal-Wallis omnibus (3 groups): H = {stat:.1f}, "
        f"p = {p_kw:.2g} ({sig_marker(p_kw)})   ·   η² = {eta:.4f}",
        "",
        "Pairwise Mann-Whitney U (Bonferroni-corrected):",
    ]
    pairs = list(combinations(groups.keys(), 2))
    for f1, f2 in pairs:
        _, p_pair = mannwhitneyu(groups[f1], groups[f2], alternative="two-sided")
        p_adj = min(p_pair * len(pairs), 1.0)
        stat_lines.append(f"    CGL={f1}  vs  CGL={f2}:  p = {p_adj:.2g}  ({sig_marker(p_adj)})")
    stat_lines.append("")
    stat_lines.append(
        "Interpretation: p < .001 means the groups differ.  "
        "η² ≈ 0.001 means the magnitude is negligible — a real but small tilt."
    )
    ax_stats.axis("off")
    ax_stats.text(0.0, 1.0, "Significance test", transform=ax_stats.transAxes,
                  ha="left", va="top", fontsize=12, fontweight="bold")
    ax_stats.text(0.0, 0.85, "\n".join(stat_lines), transform=ax_stats.transAxes,
                  ha="left", va="top", family="monospace", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "story_03_ds_preference.png", **SAVE_KW)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 4: Role desires - top gaps + caretaker callout
# ---------------------------------------------------------------------------

def figure_roles(df: pd.DataFrame) -> None:
    role_cols = [c for c in df.columns if c.startswith("role_")]
    rows = []
    cgl = df[df["cgl_flag"] == "True"]
    non = df[df["cgl_flag"] == "False"]
    n_cgl, n_non = len(cgl), len(non)
    for col in role_cols:
        name = col.replace("role_", "")
        p_cgl = cgl[col].sum() / n_cgl * 100
        p_non = non[col].sum() / n_non * 100
        rows.append({"role": name, "cgl": p_cgl, "non": p_non, "gap": p_cgl - p_non})
    plot = pd.DataFrame(rows).sort_values("gap", ascending=True)

    # Take the 12 roles with the largest absolute gap
    plot = plot.iloc[(plot["gap"].abs().sort_values(ascending=False).head(12)).index]
    plot = plot.sort_values("gap", ascending=True)

    # Add the caretaker dynamic from soft_erotic_ for the callout
    care_col = "soft_erotic_caretaker/caretakee dynamics"
    care_cgl = cgl[care_col].sum() / n_cgl * 100 if care_col in df.columns else None
    care_non = non[care_col].sum() / n_non * 100 if care_col in df.columns else None

    fig, ax = plt.subplots(figsize=(13, max(7, 0.5 * len(plot))))
    y = np.arange(len(plot))
    bar_h = 0.38
    ax.barh(y - bar_h / 2, plot["cgl"], height=bar_h,
            color=SEMANTIC["good"], edgecolor=INK["canvas"], label=f"CGL = True  (n={n_cgl:,})")
    ax.barh(y + bar_h / 2, plot["non"], height=bar_h,
            color=SEMANTIC["bad"], edgecolor=INK["canvas"], label=f"CGL = False  (n={n_non:,})")
    for i, (_, row) in enumerate(plot.iterrows()):
        ax.text(row["cgl"] + 0.4, i - bar_h / 2,
                f"{row['cgl']:.1f}%", va="center", fontsize=9, color=INK["primary"], fontweight="bold")
        ax.text(row["non"] + 0.4, i + bar_h / 2,
                f"{row['non']:.1f}%", va="center", fontsize=9, color=INK["primary"], fontweight="bold")
    xmax = max(plot["cgl"].max(), plot["non"].max())
    for i, (_, row) in enumerate(plot.iterrows()):
        ax.text(
            xmax * 1.18, i,
            f"{row['gap']:+.1f}pp",
            va="center", fontsize=10, fontweight="bold", color=INK["primary"],
            family="monospace",
        )
    ax.set_xlim(0, xmax * 1.30)
    ax.set_yticks(y)
    ax.set_yticklabels(plot["role"])
    ax.set_xlabel("% of group endorsing role", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle=":", alpha=0.4, color=INK["hairline"])
    # Legend on top, centered — title above it
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0),
              ncol=2, frameon=False, fontsize=10, labelcolor=INK["secondary"])
    ax.text(0, 1.14, "Role desires: CGL respondents over-endorse caregiving-shaped roles",
            transform=ax.transAxes, fontsize=14, fontweight="bold",
            color=INK["primary"], va="bottom")
    subtitle = (
        f"Top 12 of 21 surveyed roles by |gap|.  Across all 21 roles, CGL+ endorses "
        "every single one at a higher rate than CGL− — no role is non-CGL-tilted."
    )
    if care_cgl is not None:
        subtitle += (
            f"\nCaretaker/caretakee dynamic (a separate soft-erotic item): "
            f"CGL+ = {care_cgl:.0f}%   vs   CGL− = {care_non:.0f}%   "
            f"(Δ = {care_cgl - care_non:+.0f}pp — the structural signature of CGL)."
        )
    ax.text(0, 1.08, subtitle, transform=ax.transAxes,
            fontsize=10, style="italic", color=INK["secondary"], va="bottom")
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(FIG_DIR / "story_04_roles.png", **SAVE_KW)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Shared helper: build endorsement stats for any binary-column block
# ---------------------------------------------------------------------------

def _build_endorsement_stats(df: pd.DataFrame, var_cols, prefix_re: str) -> pd.DataFrame:
    """Return per-item endorsement % for CGL True / False / Unknown plus
    gap (T−F) and Cohen's h on (T vs F)."""
    n_pos = (df["cgl_flag"] == "True").sum()
    n_neg = (df["cgl_flag"] == "False").sum()
    n_unk = (df["cgl_flag"] == "Unknown").sum()
    rows = []
    for col in var_cols:
        p_pos = df.loc[df["cgl_flag"] == "True", col].sum() / n_pos * 100 if n_pos else 0
        p_neg = df.loc[df["cgl_flag"] == "False", col].sum() / n_neg * 100 if n_neg else 0
        p_unk = df.loc[df["cgl_flag"] == "Unknown", col].sum() / n_unk * 100 if n_unk else 0
        h = cohens_h(p_pos / 100, p_neg / 100)
        name = re.sub(prefix_re, "", col)
        rows.append({
            "variable": name,
            "pos_pct": p_pos, "neg_pct": p_neg, "unk_pct": p_unk,
            "gap": p_pos - p_neg, "h": h,
        })
    return pd.DataFrame(rows)


def _dumbbell_panel(ax, df, n_pos, n_neg, n_unk, *, max_x=None,
                    show_unknown=True, sort_ascending=True, pre_sorted=False,
                    group_separators=None, group_labels=None):
    """Standard dot-plot panel: CGL=True (green), CGL=False (red),
    optional CGL=Unknown (gray), connecting line, gap label on the right.

    Matches the 'Emotional Desire sliced by CG vs Non-CG' style from the notebook.

    Args:
        pre_sorted: if True, the caller has already arranged rows in display order
            (bottom row = df.iloc[0], top row = df.iloc[-1]) and the function will
            NOT resort by gap.
        group_separators: optional list of row indices (in display order) AFTER which
            to draw a horizontal divider — e.g. [9] divides rows 0–8 from 10+.
        group_labels: optional list of (text, y_position) pairs to label groups on
            the left margin.
    """
    if not pre_sorted:
        df = df.sort_values("gap", ascending=sort_ascending).reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)
    y = np.arange(len(df))

    # Connecting line between True and False
    for i, row in df.iterrows():
        ax.plot([row["pos_pct"], row["neg_pct"]], [i, i],
                color=INK["hairline"], lw=2, zorder=1)

    if show_unknown:
        ax.scatter(df["unk_pct"], y, color=INK["tertiary"], s=80, zorder=2,
                   edgecolor=INK["canvas"], lw=1.0,
                   label=f"CGL = Unknown (n={n_unk:,})")
    ax.scatter(df["neg_pct"], y, color=SEMANTIC["bad"], s=100, zorder=3,
               edgecolor=INK["canvas"], lw=1.2, label=f"CGL = False (n={n_neg:,})")
    ax.scatter(df["pos_pct"], y, color=SEMANTIC["good"], s=120, zorder=4,
               edgecolor=INK["canvas"], lw=1.5, label=f"CGL = True (n={n_pos:,})")

    # Gap annotation — placed outside the right spine so it never overlaps data
    if max_x is None:
        max_x = max(df["pos_pct"].max(), df["neg_pct"].max(), df["unk_pct"].max()) * 1.18
    _trans = blended_transform_factory(ax.transAxes, ax.transData)
    for i, row in df.iterrows():
        ax.text(1.02, i, f"{row['gap']:+.1f}pp",
                transform=_trans,
                va="center", ha="left", fontsize=9, fontweight="bold",
                color=INK["primary"], family="monospace", clip_on=False)

    ax.set_yticks(y)
    ax.set_yticklabels(df["variable"], fontsize=12, fontweight="bold",
                       color=INK["secondary"])
    ax.set_xlim(0, max_x)
    ax.set_xlabel("% of group endorsing", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle=":", alpha=0.4, color=INK["hairline"])
    # Legend centered just above axes — fig.suptitle + fig.text handle all titling
    n_legend = 3 if show_unknown else 2
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0),
              ncol=n_legend, frameon=False, fontsize=10,
              labelcolor=INK["secondary"])

    # Optional horizontal separators between family groups
    if group_separators:
        for sep_after in group_separators:
            ax.axhline(
                y=sep_after + 0.5,
                color=INK["tertiary"], lw=1.2, ls="--", alpha=0.6, zorder=0,
            )

    # Optional family-group labels on the right margin
    if group_labels:
        for text, y_pos in group_labels:
            ax.text(
                1.005, y_pos, text,
                transform=ax.get_yaxis_transform(),
                ha="left", va="center",
                fontsize=10, fontweight="bold", color="#444",
                rotation=90,
            )


# ---------------------------------------------------------------------------
# Figure 5: Soft erotic preferences (dumbbell, all items)
# ---------------------------------------------------------------------------

def figure_soft_erotic(df: pd.DataFrame) -> pd.DataFrame:
    soft_cols = [c for c in df.columns if c.startswith("soft_erotic_")]
    stats = _build_endorsement_stats(df, soft_cols, r"^soft_erotic_")

    n_pos = (df["cgl_flag"] == "True").sum()
    n_neg = (df["cgl_flag"] == "False").sum()
    n_unk = (df["cgl_flag"] == "Unknown").sum()

    fig, ax = plt.subplots(figsize=(13, max(6, 0.55 * len(stats))))
    max_x = max(stats["pos_pct"].max(), stats["neg_pct"].max(), stats["unk_pct"].max()) * 1.20
    _dumbbell_panel(
        ax, stats, n_pos, n_neg, n_unk,
        max_x=max_x, sort_ascending=True,
    )
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30, 35, 40, 45])

    fig.suptitle(
        'Caretaker/caretakee dynamics: 4× more endorsed by CGL respondents (20% vs 5%)',
        fontweight="bold", fontsize=14, y=0.99,
    )
    fig.text(
        0.5, 0.94,
        "Soft-erotic preferences by CGL group, sorted by CGL+ vs CGL− gap",
        ha="center", va="top", fontsize=10, style="italic", color=INK["secondary"],
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(FIG_DIR / "story_05_soft_erotic.png", **SAVE_KW)
    plt.close(fig)
    return stats


# ---------------------------------------------------------------------------
# Figure 6a: NSFW endorsements — acts + positions combined
# ---------------------------------------------------------------------------

def figure_nsfw_acts_positions(nsfw: pd.DataFrame) -> pd.DataFrame:
    act_cols = [c for c in nsfw.columns if c.startswith("act_")]
    pos_cols = [c for c in nsfw.columns if c.startswith("pos_")]

    acts_stats = _build_endorsement_stats(nsfw, act_cols, r"^act_")
    acts_stats["family"] = "Acts"
    pos_stats = _build_endorsement_stats(nsfw, pos_cols, r"^pos_")
    pos_stats["family"] = "Positions"

    # Take top N from each family separately, by signed gap descending.
    n_acts = min(10, len(acts_stats))
    n_pos_items = min(10, len(pos_stats))
    acts_top = acts_stats.sort_values("gap", ascending=False).head(n_acts).copy()
    pos_top = pos_stats.sort_values("gap", ascending=False).head(n_pos_items).copy()

    # Pre-sort: positions block (gap ASC) at the bottom of df → bottom of chart;
    # acts block (gap ASC) above → visually at the top of the chart.
    # Within each block, the row with the *largest* gap ends up at the visual top
    # of that block.
    pos_block = pos_top.sort_values("gap", ascending=True)
    acts_block = acts_top.sort_values("gap", ascending=True)
    plot_df = pd.concat([pos_block, acts_block], ignore_index=True)

    # Prefix labels with family
    plot_df["variable"] = plot_df.apply(
        lambda r: f"[{r['family'][:3].lower()}] {r['variable']}", axis=1
    )

    # Family group geometry for separator + side labels (row indices in display order)
    sep_after = len(pos_block) - 1  # divider between positions (below) and acts (above)
    pos_label_y = (len(pos_block) - 1) / 2.0
    acts_label_y = len(pos_block) + (len(acts_block) - 1) / 2.0

    n_pos = (nsfw["cgl_flag"] == "True").sum()
    n_neg = (nsfw["cgl_flag"] == "False").sum()
    n_unk = (nsfw["cgl_flag"] == "Unknown").sum()

    fig, ax = plt.subplots(figsize=(14, max(7, 0.45 * len(plot_df))))
    max_x = max(plot_df["pos_pct"].max(), plot_df["neg_pct"].max(), plot_df["unk_pct"].max()) * 1.22
    _dumbbell_panel(
        ax, plot_df, n_pos, n_neg, n_unk,
        max_x=max_x, pre_sorted=True,
        group_separators=[sep_after],
        group_labels=[("ACTS", acts_label_y), ("POSITIONS", pos_label_y)],
    )
    ax.set_xticks([0, 20, 40, 60, 80, 100])

    fig.suptitle(
        "Face- and control-focused acts show the largest CGL gaps — fingering mouths leads (+8.5pp)",
        fontweight="bold", fontsize=14, y=0.99,
    )
    fig.text(
        0.5, 0.94,
        "Sexual acts (top) and positions (bottom) — each block sorted by CGL+ vs CGL− gap",
        ha="center", va="top", fontsize=10, style="italic", color=INK["secondary"],
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(FIG_DIR / "story_06a_nsfw_acts_positions.png", **SAVE_KW)
    plt.close(fig)
    return pd.concat([acts_stats, pos_stats], ignore_index=True)


# ---------------------------------------------------------------------------
# Figure 6b: NSFW endorsements — common + uncommon combined
# ---------------------------------------------------------------------------

def figure_nsfw_common_uncommon(nsfw: pd.DataFrame) -> pd.DataFrame:
    common_cols = [c for c in nsfw.columns if c.startswith("common_")]
    uncommon_cols = [c for c in nsfw.columns if c.startswith("uncommon_")]

    com_stats = _build_endorsement_stats(nsfw, common_cols, r"^common_")
    com_stats["family"] = "Common"
    unc_stats = _build_endorsement_stats(nsfw, uncommon_cols, r"^uncommon_")
    unc_stats["family"] = "Uncommon"

    # Top N from each family separately
    n_com = min(10, len(com_stats))
    n_unc = min(10, len(unc_stats))
    com_top = com_stats.sort_values("gap", ascending=False).head(n_com).copy()
    unc_top = unc_stats.sort_values("gap", ascending=False).head(n_unc).copy()

    # Common above (top of chart), Uncommon below (bottom of chart).
    # Build display order: uncommon block at the bottom of the df, common at the top.
    unc_block = unc_top.sort_values("gap", ascending=True)
    com_block = com_top.sort_values("gap", ascending=True)
    plot_df = pd.concat([unc_block, com_block], ignore_index=True)

    plot_df["variable"] = plot_df.apply(
        lambda r: f"[{r['family'][:3].lower()}] {r['variable']}", axis=1
    )

    sep_after = len(unc_block) - 1
    unc_label_y = (len(unc_block) - 1) / 2.0
    com_label_y = len(unc_block) + (len(com_block) - 1) / 2.0

    n_pos = (nsfw["cgl_flag"] == "True").sum()
    n_neg = (nsfw["cgl_flag"] == "False").sum()
    n_unk = (nsfw["cgl_flag"] == "Unknown").sum()

    fig, ax = plt.subplots(figsize=(14, max(7, 0.45 * len(plot_df))))
    max_x = max(plot_df["pos_pct"].max(), plot_df["neg_pct"].max(), plot_df["unk_pct"].max()) * 1.22
    _dumbbell_panel(
        ax, plot_df, n_pos, n_neg, n_unk,
        max_x=max_x, pre_sorted=True,
        group_separators=[sep_after],
        group_labels=[("COMMON", com_label_y), ("UNCOMMON", unc_label_y)],
    )
    ax.set_xticks([0, 20, 40, 60, 80, 100])

    fig.suptitle(
        "Gentleness and nonconsent lead the CGL scene signal — both elevated by ~13pp",
        fontweight="bold", fontsize=14, y=0.99,
    )
    fig.text(
        0.5, 0.94,
        "Common (top) and uncommon (bottom) NSFW preferences — each block sorted by CGL+ vs CGL− gap",
        ha="center", va="top", fontsize=10, style="italic", color=INK["secondary"],
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(FIG_DIR / "story_06b_nsfw_common_uncommon.png", **SAVE_KW)
    plt.close(fig)
    return pd.concat([com_stats, unc_stats], ignore_index=True)


# ---------------------------------------------------------------------------
# Figure 6c: Arousal scale — dual-panel (stacked bars + forest plot)
# Mirrors the notebook's `plot_kink_dual_panel` chart.
# ---------------------------------------------------------------------------

def figure_arousal_dual_panel(nsfw: pd.DataFrame) -> pd.DataFrame:
    kink_fields = [
        "obedience", "mindbreak", "masterslave", "fulltimepower", "humiliation",
        "lightbondage", "mediumbondage", "extremebondage", "worshipping", "worshipped",
        "voyeurself", "voyeurother", "exhibitionself", "exhibitionother",
        "regression", "progression", "agegap", "older",
    ]
    # ----- Stats per item -----
    rows = []
    for col in kink_fields:
        pos = nsfw.loc[nsfw["cgl_flag"] == "True", col].dropna()
        rest = nsfw.loc[nsfw["cgl_flag"] != "True", col].dropna()
        a = int((pos >= 1).sum()); b = int((pos == 0).sum())
        c = int((rest >= 1).sum()); d = int((rest == 0).sum())
        n_pos_resp, n_rest_resp = a + b, c + d
        p_pos = a / n_pos_resp if n_pos_resp else np.nan
        p_rest = c / n_rest_resp if n_rest_resp else np.nan
        table = [[a, b], [c, d]]
        if min(n_pos_resp, n_rest_resp, a + c, b + d) == 0:
            p_raw = np.nan
        else:
            row_tot = np.array([a + b, c + d])
            col_tot = np.array([a + c, b + d])
            expected = np.outer(row_tot, col_tot) / row_tot.sum()
            if expected.min() < 5:
                _, p_raw = fisher_exact(table)
            else:
                _, p_raw, _, _ = chi2_contingency(table, correction=True)
        or_, or_lo, or_hi = or_with_ci(a, b, c, d)
        h = cohens_h(p_pos, p_rest)
        rows.append({
            "variable": col,
            "cohens_h": h, "or": or_, "or_lo": or_lo, "or_hi": or_hi,
            "p_raw": p_raw,
        })
    res = pd.DataFrame(rows)
    valid = res["p_raw"].notna()
    res["p_fdr"] = np.nan
    res.loc[valid, "p_fdr"] = bh_fdr(res.loc[valid, "p_raw"].values)

    def tier(row):
        sig = row["p_fdr"] < 0.05
        ci_clean = (row["or_lo"] > 1) or (row["or_hi"] < 1)
        m = abs(row["cohens_h"])
        if sig and ci_clean and m >= 0.5: return "strong"
        if sig and ci_clean and m >= 0.2: return "moderate"
        if sig and ci_clean: return "weak"
        return "ns"

    res["tier"] = res.apply(tier, axis=1)
    res = res.reindex(res["cohens_h"].abs().sort_values(ascending=False).index).reset_index(drop=True)

    # ----- Yes/No/NaN rates per group (denominator = each group's total) -----
    pos_mask = nsfw["cgl_flag"] == "True"
    n_pos = int(pos_mask.sum())
    n_rest = int((~pos_mask).sum())
    rates = {}
    for k in res["variable"]:
        x = nsfw[k]
        rates[k] = dict(
            pos_yes=((x >= 1) & pos_mask).sum() / n_pos,
            pos_no=((x == 0) & pos_mask).sum() / n_pos,
            pos_nan=(x.isna() & pos_mask).sum() / n_pos,
            rest_yes=((x >= 1) & ~pos_mask).sum() / n_rest,
            rest_no=((x == 0) & ~pos_mask).sum() / n_rest,
            rest_nan=(x.isna() & ~pos_mask).sum() / n_rest,
        )

    # ----- Plot -----
    TIER_COLORS = TIER
    TIER_BADGE = {"strong": "★★★", "moderate": "★★", "weak": "★", "ns": ""}
    TIER_LABEL = {"strong": "★★★ strong", "moderate": "★★ moderate",
                  "weak": "★ weak", "ns": "n.s. after FDR"}
    C_YES  = SEMANTIC["good"]    # arousing — yes
    C_NO   = SEMANTIC["bad"]     # not arousing — no
    C_NAN  = INK["surface"]      # no response

    n = len(res)
    fig = plt.figure(figsize=(16, 0.95 * n + 3.6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[2.4, 1.0], wspace=0.18)
    axL = fig.add_subplot(gs[0])
    axR = fig.add_subplot(gs[1])

    MIN_LABEL_FRAC = 0.04

    def _pct_label(ax, x_center, y, frac, on_dark=True):
        if frac < MIN_LABEL_FRAC:
            return
        ax.text(x_center, y, f"{frac*100:.0f}%",
                ha="center", va="center", fontsize=8.5, fontweight="bold",
                color=INK["canvas"] if on_dark else INK["primary"])

    for i, k in enumerate(res["variable"]):
        row = res.iloc[i]
        c_tier = TIER_COLORS[row["tier"]]
        y_top, y_bot = i * 2 + 0.4, i * 2 + 1.1

        for y, prefix, alpha in [(y_top, "pos", 1.0), (y_bot, "rest", 0.78)]:
            yes = rates[k][f"{prefix}_yes"]
            no_ = rates[k][f"{prefix}_no"]
            nan_ = rates[k][f"{prefix}_nan"]
            axL.barh(y, yes, color=C_YES, alpha=alpha, edgecolor="white")
            axL.barh(y, no_, left=yes, color=C_NO, alpha=alpha, edgecolor="white")
            axL.barh(y, nan_, left=yes + no_, color=C_NAN, alpha=alpha, edgecolor="white")
            _pct_label(axL, yes / 2, y, yes, on_dark=True)
            _pct_label(axL, yes + no_ / 2, y, no_, on_dark=True)
            _pct_label(axL, yes + no_ + nan_ / 2, y, nan_, on_dark=False)

        axL.text(-0.01, y_top, "CGL+", ha="right", va="center",
                 fontsize=8.5, fontweight="bold")
        axL.text(-0.01, y_bot, "Rest", ha="right", va="center", fontsize=8.5)
        axL.text(0, y_top - 0.55, f"{k}   {TIER_BADGE[row['tier']]}",
                 ha="left", va="bottom", fontsize=10.5, fontweight="bold", color=c_tier)

        y_mid = (y_top + y_bot) / 2
        axR.plot([row["or_lo"], row["or_hi"]], [y_mid, y_mid], color=c_tier, lw=2)
        axR.plot(row["or"], y_mid, "o", color=c_tier, ms=7)
        p_text = "<0.001" if row["p_fdr"] < 0.001 else f"{row['p_fdr']:.3f}"
        axR.text(row["or_hi"] * 1.05, y_mid,
                 f"{row['or']:.2f}×   h={row['cohens_h']:+.2f}   p={p_text}",
                 va="center", fontsize=8.5, color=c_tier)

    axL.set_xlim(0, 1); axL.invert_yaxis(); axL.set_yticks([])
    axL.set_xticks([])
    axL.spines[["top", "right", "left", "bottom"]].set_visible(False)

    axR.set_xscale("log"); axR.axvline(1, color="black", lw=0.9, ls="--")
    axR.set_ylim(axL.get_ylim()); axR.set_yticks([])
    or_lo_lim = max(0.1, res["or_lo"].min() * 0.7)
    or_hi_lim = res["or_hi"].max() * 2.5
    axR.set_xlim(or_lo_lim, or_hi_lim)
    candidate_ticks = [0.5, 0.67, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
    ticks = [t for t in candidate_ticks if or_lo_lim <= t <= or_hi_lim]
    if 1.0 not in ticks: ticks.append(1.0); ticks.sort()
    axR.xaxis.set_major_locator(FixedLocator(ticks))
    axR.xaxis.set_major_formatter(FixedFormatter([
        "1×  (null)" if t == 1.0 else f"{t:g}×" for t in ticks
    ]))
    axR.xaxis.set_minor_locator(FixedLocator([]))
    axR.tick_params(axis="x", labelsize=9)
    axR.set_xlabel("Odds of endorsing  (CGL+ vs Rest)", fontsize=9)
    axR.spines[["top", "right", "left"]].set_visible(False)

    # Header: title + sample sizes + caption
    fig.suptitle(
        "Kink-Specific Arousal: Response Distribution + Effect Size",
        fontsize=14, fontweight="bold", y=0.995,
    )
    fig.text(0.5, 0.965,
             f"CGL+ n = {n_pos:,}   ·   Rest n = {n_rest:,}",
             ha="center", va="top", fontsize=10, style="italic", color="#555")
    caption = (
        "How to read each forest row:  OR  ·  h  ·  p\n"
        "  OR  (odds ratio, log axis) — odds of endorsing in CGL+ ÷ Rest.  null = 1×.  "
        "2× = twice as likely · 0.5× = half as likely.  CI crossing 1× → not significant.\n"
        "  h   (Cohen's h)            — base-rate-normalized effect size.  "
        "|h| 0.2 small · 0.5 medium · 0.8 large.  Sign = direction (+ = CGL+ higher).\n"
        "  p   (FDR-adjusted)         — Benjamini-Hochberg corrected across all items.  "
        "p < 0.05 = real signal (raw p inflates false positives over many tests).\n"
        "Tier (★★★ / ★★ / ★) requires p < 0.05 + OR CI excludes 1 + |h| above threshold.  "
        "Items sorted by |h|."
    )
    fig.text(0.5, 0.945, caption,
             ha="center", va="top", fontsize=9, color="#333", linespacing=1.5,
             family="monospace")

    response_handles = [
        Patch(facecolor=C_YES, label="Arousing (≥1)"),
        Patch(facecolor=C_NO, label="Not Arousing (=0)"),
        Patch(facecolor=C_NAN, label="No Response (NaN)"),
    ]
    axL.legend(handles=response_handles, loc="lower center",
               bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=9)
    tier_handles = [
        Line2D([0], [0], marker="o", color=TIER_COLORS[t], lw=2, ms=7, label=TIER_LABEL[t])
        for t in ["strong", "moderate", "weak", "ns"]
    ]
    axR.legend(handles=tier_handles, loc="lower center",
               bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False, fontsize=8.5)

    plt.tight_layout(rect=[0, 0, 1, 0.86])
    plt.savefig(FIG_DIR / "story_06c_arousal_dual_panel.png", **SAVE_KW)
    plt.close(fig)
    return res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Output dir: {FIG_DIR}")
    df = load_main_df()
    nsfw = load_nsfw_df()
    print(f"Loaded cgl_BKS_data.csv  shape={df.shape}")
    print(f"Loaded BKS_nsfw_preferences.csv  shape={nsfw.shape}")

    print("→ figure 1: personality")
    figure_personality(df)
    print("→ figure 2: emotion")
    figure_emotion(df)
    print("→ figure 3: D/S preference")
    figure_ds(df)
    print("→ figure 4: roles")
    figure_roles(df)
    print("→ figure 5: soft-erotic preferences")
    soft = figure_soft_erotic(df)
    print(soft.sort_values("gap", ascending=False)[
        ["variable", "pos_pct", "neg_pct", "gap", "h"]
    ].to_string(index=False))

    print("→ figure 6a: NSFW acts + positions")
    ap = figure_nsfw_acts_positions(nsfw)
    print(ap.sort_values("gap", ascending=False).head(10)[
        ["variable", "family", "pos_pct", "neg_pct", "gap", "h"]
    ].to_string(index=False))

    print("→ figure 6b: NSFW common + uncommon")
    cu = figure_nsfw_common_uncommon(nsfw)
    print(cu.sort_values("gap", ascending=False).head(10)[
        ["variable", "family", "pos_pct", "neg_pct", "gap", "h"]
    ].to_string(index=False))

    print("→ figure 6c: arousal dual panel")
    res = figure_arousal_dual_panel(nsfw)
    print(res[["variable", "or", "or_lo", "or_hi", "cohens_h", "p_fdr", "tier"]]
          .to_string(index=False))

    # Clean up old single-NSFW image
    old = FIG_DIR / "story_05_nsfw_endorsements.png"
    if old.exists():
        old.unlink()
        print(f"removed stale figure: {old.name}")
    old2 = FIG_DIR / "story_06_arousal_odds.png"
    if old2.exists():
        old2.unlink()
        print(f"removed stale figure: {old2.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
