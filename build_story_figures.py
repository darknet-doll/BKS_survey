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
    # 5-panel horizontal density distributions, one per OCEAN trait.
    # CGL+ (hero pink) vs CGL− (hairline gray) — distributions overlap almost perfectly.
    ocean_traits = [
        ("openness", "Openness"),
        ("consciensiousness", "Conscientiousness"),
        ("extroversion", "Extraversion"),
        ("neuroticism", "Neuroticism"),
        ("agreeableness", "Agreeableness"),
        ("powerlessness", "Powerlessness"),
    ]

    cgl_plus = df[df["cgl_flag"] == "True"]
    non      = df[df["cgl_flag"] == "False"]   # CGL− — apples-to-apples comparator
    rest     = non                              # comparison series = CGL− (Unknown excluded as a missing-data category)

    fig, axes = plt.subplots(1, 6, figsize=(16, 5.2), sharey=True, sharex=True)

    # Collapse the raw composite score into a 3-band scale at a per-construct
    # threshold, because OCEAN and powerlessness sit on different ranges:
    #   • OCEAN (thresh=1, range ±6): score ≥ +1 → Agree, 0 → Neutral, ≤ −1 → Disagree.
    #     Differenced item already nets opposing framings, so any nonzero residual is
    #     a directional lean worth counting (only an exact 0 is genuinely balanced).
    #   • Powerlessness (thresh=3, range ±9): score ≥ +3 → Agree, −2..+2 → Neutral,
    #     ≤ −3 → Disagree. A 3-item SUM runs to ±9, so per the BKS_Data_Review table
    #     ±3 is the comparable "clear endorsement" cut (±1/±2 is one mild item → neutral).
    # The shared y-axis shows word bands only (Disagree/Neutral/Agree); the numeric
    # cut-points live in the footnote, and powerlessness's wider ±3 band is flagged
    # there via a † so the differing scale isn't mislabelled on a shared axis.
    def to_agreement(series: pd.Series, thresh: int) -> np.ndarray:
        v = series.dropna().to_numpy()
        out = np.zeros_like(v, dtype=int)
        out[v >= thresh] = 1
        out[v <= -thresh] = -1
        return out

    bin_centres = np.array([-1, 0, 1])
    bar_h       = 0.38

    # First pass: compute all percentages so we can share an x-axis range
    panel_data = []
    x_max = 0.0
    for col, label in ocean_traits:
        thresh = 3 if col == "powerlessness" else 1   # powerlessness keeps the ±3 band
        cgl_a  = to_agreement(cgl_plus[col], thresh)
        rest_a = to_agreement(rest[col], thresh)
        cgl_pct  = np.array([100 * (cgl_a  == k).sum() / max(len(cgl_a),  1) for k in bin_centres])
        rest_pct = np.array([100 * (rest_a == k).sum() / max(len(rest_a), 1) for k in bin_centres])
        panel_data.append((col, label, cgl_pct, rest_pct))
        x_max = max(x_max, cgl_pct.max(), rest_pct.max())
    x_max = np.ceil(x_max / 10) * 10

    for ax, (col, label, cgl_pct, rest_pct) in zip(axes, panel_data):
        # Side-by-side horizontal bars: Rest below centre, CGL+ above centre
        ax.barh(bin_centres - bar_h / 2, rest_pct, height=bar_h,
                color=INK["hairline"], zorder=2,
                label="CGL−" if ax is axes[0] else None)
        ax.barh(bin_centres + bar_h / 2, cgl_pct, height=bar_h,
                color=ACCENT["hero"], zorder=3,
                label="CGL+" if ax is axes[0] else None)

        # Direct value labels at bar ends (Rule 4: strip value axis, label directly)
        for y, p in zip(bin_centres - bar_h / 2, rest_pct):
            ax.text(p + 1.5, y, f"{p:.0f}%", ha="left", va="center",
                    fontsize=9, color=INK["secondary"])
        for y, p in zip(bin_centres + bar_h / 2, cgl_pct):
            ax.text(p + 1.5, y, f"{p:.0f}%", ha="left", va="center",
                    fontsize=9, fontweight="bold", color=INK["primary"])

        d = cohens_d(cgl_plus[col], non[col])
        ax.text(
            0.5, -0.10,
            f"d = {d:+.3f}",
            transform=ax.transAxes, ha="center", va="top",
            fontsize=9, color=INK["tertiary"], style="italic",
        )

        title = f"{label} †" if col == "powerlessness" else label
        ax.set_title(title, fontsize=13.5, fontweight="bold",
                     color=INK["primary"], pad=8)
        ax.set_yticks(bin_centres)
        # Secondary hierarchy: band labels recede (regular weight, smaller, dimmer)
        # so the bold trait headers read as the primary level.
        ax.set_yticklabels(["Disagree", "Neutral", "Agree"],
                           fontsize=9.5, fontweight="normal", color=INK["secondary"])
        ax.set_xlim(0, x_max + 12)
        ax.tick_params(axis="y", colors=INK["secondary"])
        ax.tick_params(axis="x", labelsize=9, colors=INK["tertiary"])
        ax.spines[["top", "right", "bottom"]].set_visible(False)
        ax.spines["left"].set_color(INK["hairline"])
        ax.set_xticks([])  # Rule 4: strip value axis on bar charts

    axes[0].set_ylabel("Agreement Scale", fontsize=11, color=INK["secondary"])

    # Headline title — placed via fig.suptitle so layout reserves space for it.
    fig.suptitle(
        "Data distribution shows no significant difference\n"
        "as to whether someone identifies with the OCEAN personality test",
        x=0.005, y=0.995, ha="left", va="top",
        fontsize=18, fontweight="bold", color=INK["primary"],
    )

    # Legend below title, above axes (Rule 1)
    fig.legend(
        loc="upper left", bbox_to_anchor=(0.005, 0.86),
        ncol=2, frameon=False, labelcolor=INK["secondary"], fontsize=11,
    )

    # Source / context note at the bottom
    fig.text(
        0.005, 0.005,
        f"n CGL+ = {len(cgl_plus):,}   ·   n CGL− = {len(non):,}   "
        "(Unknown — did not answer the CGL item — excluded as a missing-data category)   ·   "
        "Cohen's d compares CGL+ vs CGL−; all values fall in the trivial band (|d| < 0.10)\n"
        "OCEAN bands (differenced items, range ±6): composite ≥ +1 = Agree, 0 = Neutral, ≤ −1 = Disagree.   "
        "† Powerlessness uses a ±3 band (≥ +3 Agree, −2…+2 Neutral, ≤ −3 Disagree) — its 3-item summed scale "
        "runs to ±9, so ±3 is the comparable 'clear endorsement' cut.",
        fontsize=9, color=INK["tertiary"], style="italic",
        ha="left", va="bottom",
    )

    fig.tight_layout(rect=[0.0, 0.07, 1.0, 0.82], w_pad=0.6)
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
        "False":   INK["secondary"],   # dark gray
        "Unknown": INK["hairline"],    # light gray
        "True":    ACCENT["hero"],     # pink
    }
    size_map = {"False": 90, "True": 120, "Unknown": 80}

    def panel(ax, pct, title, n_counts):
        y_pos = np.arange(len(pct))
        for i, cat in enumerate(pct.index):
            ax.plot(
                [pct.loc[cat, "False"], pct.loc[cat, "True"]],
                [i, i], color=INK["hairline"], lw=2.0, zorder=1,
            )
        for flag in ["False", "True"]:
            lbl = "CGL−" if flag == "False" else "CGL+"
            ax.scatter(
                pct[flag].values, y_pos,
                color=color_map[flag], s=size_map[flag], zorder=3,
                label=f"{lbl}  (n={int(n_counts.get(flag, 0)):,})",
                edgecolor=INK["canvas"], linewidth=1.2,
            )
        # Gap annotation — outside the right spine; colored by sign
        _trans = blended_transform_factory(ax.transAxes, ax.transData)
        for i, cat in enumerate(pct.index):
            gap = pct.loc[cat, "True"] - pct.loc[cat, "False"]
            if gap > 0:
                gap_color = SEMANTIC["good"]
            elif gap < 0:
                gap_color = SEMANTIC["bad"]
            else:
                gap_color = INK["secondary"]
            ax.text(1.02, i, f"{gap:+.1f}%",
                    transform=_trans,
                    ha="left", va="center", fontsize=9, fontweight="bold",
                    color=gap_color, family="monospace", clip_on=False)
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
                  ncol=2, frameon=False, fontsize=10, labelcolor=INK["secondary"])
        ax.text(0, 1.14, title, transform=ax.transAxes,
                fontweight="bold", fontsize=13, color=INK["primary"], va="bottom")

    panel(axes[0], pct_left, titles[0], n_left)
    panel(axes[1], pct_right, titles[1], n_right)

    fig.suptitle(
        "CGL respondents favor complementary, power-asymmetric emotions over mutual ones",
        fontweight="bold", fontsize=14, y=0.99,
    )
    fig.text(
        0.5, 0.94,
        "% choosing each emotion as most-wanted for self (left) or partner (right).  "
        "Both poles rise for the partner because pooled CGL+ mixes submissive and dominant "
        "respondents, who want mirror-image pairings — the asymmetry is per-couple, not one direction.",
        ha="center", va="top", fontsize=10, style="italic", color=INK["secondary"],
    )
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(FIG_DIR / "story_02_emotion.png", **SAVE_KW)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2 (Highlight 2 hero): complementary asymmetry, faceted by D/S role
# ---------------------------------------------------------------------------

def figure_emotion_mirror(df: pd.DataFrame) -> None:
    """Highlight-2 hero. The pooled two-panel (figure_emotion → appendix) hides the
    story: submissive and dominant CGL+ want MIRROR-IMAGE pairings, so pooling them
    lifts both power poles for the partner. Facet by D/S role to make the
    complementarity legible; add a strip showing both camps drop mutual emotions."""
    cgl = df[df["cgl_flag"] == "True"].copy()
    non = df[df["cgl_flag"] == "False"]

    def ds_bucket(s):
        s = str(s).lower()
        if "submissive" in s:
            return "sub"
        if "dominant" in s:
            return "dom"
        return "switch"
    cgl["ds"] = cgl["ds_preference"].map(ds_bucket)

    def pct(sub, col, val):
        # % among responders (NaN dropped) — matches the report's Chapter 2 convention
        s = sub[col].dropna()
        return 100 * (s == val).mean() if len(s) else 0.0

    POWERLESS = "Powerlessness or vulnerability"
    POWER = "Power or smugness"
    emo_rows = [(POWERLESS, "Powerlessness /\nvulnerability"),
                (POWER, "Power /\nsmugness")]
    roles = [("sub", "Submissive CGL+"), ("dom", "Dominant CGL+")]
    taglines = {
        "sub": "“I feel small · my partner feels big”",
        "dom": "“I feel big · my partner feels small”",
    }

    fig = plt.figure(figsize=(14, 7.9))
    gs = gridspec.GridSpec(2, 2, height_ratios=[2.7, 1.0], hspace=0.85, wspace=0.10)
    ax_sub = fig.add_subplot(gs[0, 0])
    ax_dom = fig.add_subplot(gs[0, 1], sharex=ax_sub, sharey=ax_sub)
    ax_mut = fig.add_subplot(gs[1, :])

    for ax, (key, title) in zip([ax_sub, ax_dom], roles):
        grp = cgl[cgl["ds"] == key]
        n = len(grp)
        for y, (emo, _) in zip([1, 0], emo_rows):
            self_x = pct(grp, "youfeelmost", emo)
            partner_x = pct(grp, "otherfeel1most", emo)
            ax.plot([partner_x, self_x], [y, y], color=INK["hairline"], lw=2.5, zorder=1)
            ax.scatter(partner_x, y, s=160, facecolor=INK["canvas"],
                       edgecolor=INK["secondary"], linewidth=2.0, zorder=3)
            ax.scatter(self_x, y, s=180, color=ACCENT["hero"],
                       edgecolor=INK["canvas"], linewidth=1.5, zorder=4)
            ax.text(self_x, y + 0.22, f"self {self_x:.0f}%", ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color=ACCENT["hero"])
            ax.text(partner_x, y - 0.22, f"partner {partner_x:.0f}%", ha="center", va="top",
                    fontsize=10, color=INK["secondary"])
        ax.set_yticks([1, 0])
        ax.set_yticklabels([emo_rows[0][1], emo_rows[1][1]],
                           fontsize=11, fontweight="bold", color=INK["primary"])
        ax.set_ylim(-0.75, 1.75)
        ax.set_xlim(-2, 30)
        ax.set_title(f"{title}   (n={n:,})", fontsize=13, fontweight="bold",
                     color=INK["primary"], pad=10)
        ax.text(0.5, -0.18, taglines[key], transform=ax.transAxes, ha="center", va="top",
                fontsize=11.5, style="italic", color=INK["secondary"])
        ax.set_xlabel("% choosing as their #1 feeling", fontsize=9.5, color=INK["tertiary"])
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(INK["hairline"])
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", linestyle=":", alpha=0.35, color=INK["hairline"])
    ax_dom.tick_params(labelleft=False)

    # Mutual-emotions strip: pooled CGL+ vs others — both fall (the one shared shift).
    for y, val in zip([1, 0], ["Eagerness or desire", "Love or romance"]):
        v_non = pct(non, "youfeelmost", val)
        v_cgl = pct(cgl, "youfeelmost", val)
        ax_mut.annotate("", xy=(v_cgl, y), xytext=(v_non, y),
                        arrowprops=dict(arrowstyle="-|>", color=SEMANTIC["bad"], lw=2.4))
        ax_mut.scatter(v_non, y, s=80, color=INK["tertiary"], zorder=3)
        ax_mut.text(v_non + 0.5, y + 0.30, f"others {v_non:.0f}%", ha="left", va="bottom",
                    fontsize=9, color=INK["tertiary"])
        ax_mut.text(v_cgl - 0.5, y + 0.30, f"CGL+ {v_cgl:.0f}%", ha="right", va="bottom",
                    fontsize=9, fontweight="bold", color=INK["primary"])
    ax_mut.set_yticks([1, 0])
    ax_mut.set_yticklabels(["Eagerness /\ndesire", "Love /\nromance"],
                           fontsize=10.5, fontweight="bold", color=INK["primary"])
    ax_mut.set_ylim(-0.8, 1.8)
    ax_mut.set_xlim(0, 42)
    ax_mut.set_xlabel("% choosing as their #1 feeling", fontsize=9.5, color=INK["tertiary"])
    ax_mut.set_title("Both camps agree on one thing: less pull toward mutual, shared emotions",
                     fontsize=12, fontweight="bold", color=INK["primary"], loc="left", pad=8)
    ax_mut.spines[["top", "right", "left"]].set_visible(False)
    ax_mut.spines["bottom"].set_color(INK["hairline"])
    ax_mut.tick_params(axis="y", length=0)
    ax_mut.grid(axis="x", linestyle=":", alpha=0.35, color=INK["hairline"])

    legend_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=ACCENT["hero"],
               markeredgecolor=INK["canvas"], markersize=13,
               label="what they want to feel (self)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=INK["canvas"],
               markeredgecolor=INK["secondary"], markeredgewidth=2, markersize=12,
               label="what they want their partner to feel"),
    ]
    fig.suptitle(
        "Submissive and dominant CGL respondents want mirror-image pairings",
        x=0.5, y=0.985, fontsize=15.5, fontweight="bold", color=INK["primary"],
    )
    fig.text(0.5, 0.94,
             "Each camp wants one partner powerless and the other powerful — they just take "
             "opposite ends. Pooled together this looks like “both poles up”; split by role, "
             "the complementarity is exact.",
             ha="center", va="top", fontsize=10, style="italic", color=INK["secondary"])
    fig.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, 0.885),
               ncol=2, frameon=False, fontsize=10.5, labelcolor=INK["secondary"])

    fig.subplots_adjust(left=0.13, right=0.97, top=0.78, bottom=0.085)
    plt.savefig(FIG_DIR / "story_02_emotion_mirror.png", **SAVE_KW)
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
    plot_df = plot_df[plot_df["cgl_flag"].isin(["False", "True"])]   # CGL+ vs CGL− only
    flag_order = ["False", "True"]
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
        flag_label = "CGL−" if flag == "False" else "CGL+"
        ax_chart.text(-0.01, i + 0.08, flag_label, transform=trans,
                      ha="right", va="bottom", fontsize=11, fontweight="bold")
        ax_chart.text(-0.01, i - 0.08, f"(n = {n:,})", transform=trans,
                      ha="right", va="top", fontsize=9)
    ax_chart.set_xticks([])
    ax_chart.set_xlabel("")
    ax_chart.tick_params(axis="x", length=0)
    ax_chart.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax_chart.set_title(
        "Dominance / Submission Preference by CGL Group",
        fontsize=16, fontweight="bold", loc="center", pad=70,
    )
    legend_handles = [Patch(color=ds_colors[i], label=ds_order[i]) for i in range(len(ds_order))]
    ax_chart.legend(
        handles=legend_handles, bbox_to_anchor=(0.5, 1.02), loc="lower center",
        ncol=4, frameon=False, fontsize=9,
    )

    # Stats panel — two-group test (CGL+ vs CGL−); Unknown excluded as missing-data.
    plot_df["ds_rank"] = plot_df["ds_preference"].map(ds_rank)
    g_pos = plot_df.loc[plot_df["cgl_flag"] == "True", "ds_rank"].values
    g_neg = plot_df.loc[plot_df["cgl_flag"] == "False", "ds_rank"].values
    U, p_mwu = mannwhitneyu(g_pos, g_neg, alternative="two-sided")
    rank_biserial = 1 - 2 * U / (len(g_pos) * len(g_neg))   # effect size, sample-size-independent

    def sig_marker(p):
        if p < 0.001: return "***"
        if p < 0.01: return "**"
        if p < 0.05: return "*"
        return "ns"

    stat_lines = [
        f"Mann-Whitney U (CGL+ vs CGL−): U = {U:,.0f}, "
        f"p = {p_mwu:.2g} ({sig_marker(p_mwu)})",
        f"Effect size: rank-biserial r = {rank_biserial:+.3f}  (negligible; |r| < 0.10)",
        f"n CGL+ = {len(g_pos):,}   ·   n CGL− = {len(g_neg):,}",
        "",
        "Interpretation: p < .001 means the groups differ.  "
        "r ≈ 0.08 means the magnitude is negligible — a real but small submissive tilt.",
    ]
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
    cgl = df[df["cgl_flag"] == "True"]
    non = df[df["cgl_flag"] == "False"]
    unk = df[df["cgl_flag"] == "Unknown"]
    n_cgl, n_non, n_unk = len(cgl), len(non), len(unk)
    rows = []
    for col in role_cols:
        name = col.replace("role_", "")
        p_cgl = cgl[col].sum() / n_cgl * 100
        p_non = non[col].sum() / n_non * 100
        p_unk = unk[col].sum() / n_unk * 100 if n_unk > 0 else 0.0
        rows.append({"role": name, "cgl": p_cgl, "non": p_non, "unk": p_unk,
                     "gap": p_cgl - p_non})
    plot = pd.DataFrame(rows)

    # Keep the 12 roles with the largest absolute CGL−CGL=False gap,
    # then order by CGL=True desire % (highest at top).
    plot = plot.iloc[plot["gap"].abs().sort_values(ascending=False).head(12).index]
    plot = plot.sort_values("cgl", ascending=True)   # ascending → top-of-chart = highest

    # Add the caretaker dynamic from soft_erotic_ for the callout
    care_col = "soft_erotic_caretaker/caretakee dynamics"
    care_cgl = cgl[care_col].sum() / n_cgl * 100 if care_col in df.columns else None
    care_non = non[care_col].sum() / n_non * 100 if care_col in df.columns else None

    color_map = {
        "False":   INK["secondary"],   # dark gray
        "Unknown": INK["hairline"],    # light gray
        "True":    ACCENT["hero"],     # pink
    }
    size_map = {"False": 90, "Unknown": 80, "True": 120}

    fig, ax = plt.subplots(figsize=(14, max(7, 0.5 * len(plot))))
    y = np.arange(len(plot))

    # Connector line spans CGL− .. CGL+ per row (Unknown excluded as missing-data)
    for i, (_, row) in enumerate(plot.iterrows()):
        lo = min(row["cgl"], row["non"])
        hi = max(row["cgl"], row["non"])
        ax.plot([lo, hi], [i, i], color=INK["hairline"], lw=2.0, zorder=1)

    # Draw CGL− then CGL+ (pink) on top
    ax.scatter(plot["non"], y, color=color_map["False"], s=size_map["False"],
               edgecolor=INK["canvas"], linewidth=1.2, zorder=3,
               label=f"CGL−  (n={n_non:,})")
    ax.scatter(plot["cgl"], y, color=color_map["True"], s=size_map["True"],
               edgecolor=INK["canvas"], linewidth=1.2, zorder=4,
               label=f"CGL+  (n={n_cgl:,})")

    # CGL=True direct % label (next to the pink hero dot)
    xmax = max(plot["cgl"].max(), plot["non"].max())
    for i, (_, row) in enumerate(plot.iterrows()):
        ax.text(row["cgl"] + 0.6, i, f"{row['cgl']:.1f}%",
                va="center", ha="left",
                fontsize=10, fontweight="bold", color=INK["primary"])

    # Gap annotation outside the right spine, colored by sign
    _trans = blended_transform_factory(ax.transAxes, ax.transData)
    for i, (_, row) in enumerate(plot.iterrows()):
        gap = row["gap"]
        if gap > 0:
            gap_color = SEMANTIC["good"]
        elif gap < 0:
            gap_color = SEMANTIC["bad"]
        else:
            gap_color = INK["secondary"]
        ax.text(1.02, i, f"{gap:+.1f}%",
                transform=_trans, ha="left", va="center",
                fontsize=10, fontweight="bold", family="monospace",
                color=gap_color, clip_on=False)

    ax.set_xlim(0, xmax * 1.18)
    ax.set_yticks(y)
    ax.set_yticklabels(plot["role"], fontsize=12, fontweight="bold", color=INK["secondary"])
    ax.set_xlabel("% of group endorsing role", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color(INK["hairline"])
    ax.spines["bottom"].set_color(INK["hairline"])
    ax.grid(axis="x", linestyle=":", alpha=0.4, color=INK["hairline"])

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0),
              ncol=2, frameon=False, fontsize=10, labelcolor=INK["secondary"])
    ax.text(0, 1.12,
            "Role desires: CGL respondents over-endorse caregiving-shaped roles",
            transform=ax.transAxes, fontsize=14, fontweight="bold",
            color=INK["primary"], va="bottom")
    subtitle = (
        "Top 12 of 21 surveyed roles by |Δ| (CGL=True − CGL=False); rows ordered by CGL=True %.  "
        "Across all 21 roles, CGL+ endorses every single one at a higher rate than CGL−."
    )
    if care_cgl is not None:
        subtitle += (
            f"\nCaretaker/caretakee dynamic (a separate soft-erotic item): "
            f"CGL+ = {care_cgl:.0f}%   vs   CGL− = {care_non:.0f}%   "
            f"(Δ = {care_cgl - care_non:+.0f}% — the structural signature of CGL)."
        )
    ax.text(0, 1.06, subtitle, transform=ax.transAxes,
            fontsize=10, style="italic", color=INK["secondary"], va="bottom")
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(FIG_DIR / "story_04_roles.png", **SAVE_KW)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Shared helper: build endorsement stats for any binary-column block
# ---------------------------------------------------------------------------

def _build_endorsement_stats(df: pd.DataFrame, var_cols, prefix_re: str) -> pd.DataFrame:
    """Return per-item endorsement % for CGL True / False / Unknown / Rest, plus
    gap (T−F), gap_rest (T−Rest), and Cohen's h on (T vs F)."""
    n_pos = (df["cgl_flag"] == "True").sum()
    n_neg = (df["cgl_flag"] == "False").sum()
    n_unk = (df["cgl_flag"] == "Unknown").sum()
    n_rest = n_neg + n_unk
    rest_mask = df["cgl_flag"] != "True"
    rows = []
    for col in var_cols:
        p_pos = df.loc[df["cgl_flag"] == "True", col].sum() / n_pos * 100 if n_pos else 0
        p_neg = df.loc[df["cgl_flag"] == "False", col].sum() / n_neg * 100 if n_neg else 0
        p_unk = df.loc[df["cgl_flag"] == "Unknown", col].sum() / n_unk * 100 if n_unk else 0
        p_rest = df.loc[rest_mask, col].sum() / n_rest * 100 if n_rest else 0
        h = cohens_h(p_pos / 100, p_neg / 100)
        name = re.sub(prefix_re, "", col)
        rows.append({
            "variable": name,
            "pos_pct": p_pos, "neg_pct": p_neg, "unk_pct": p_unk, "rest_pct": p_rest,
            "gap": p_pos - p_neg, "gap_rest": p_pos - p_rest, "h": h,
        })
    return pd.DataFrame(rows)


def _dumbbell_panel(ax, df, n_pos, n_neg, n_unk, *, max_x=None,
                    show_unknown=True, sort_ascending=True, pre_sorted=False,
                    group_separators=None, group_labels=None,
                    compare_mode="all_three"):
    """Standard dot-plot panel matching the Highlight 4/5 style.

    compare_mode:
      - "all_three": three dots per row — CGL=False (dark gray),
                     CGL=Unknown (light gray), CGL=True (pink). Gap = T − F.
      - "vs_rest":   two dots per row — Rest = False+Unknown (dark gray) vs
                     CGL=True (pink). Gap = T − Rest (uses df['gap_rest']).

    Connector spans min..max of the displayed group %s.  Gap shown as +X.X%
    colored green (positive) / red (negative).  Direct CGL=True % label
    sits next to the pink dot.
    """
    sort_col = "pos_pct"
    if not pre_sorted:
        df = df.sort_values(sort_col, ascending=sort_ascending).reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)
    y = np.arange(len(df))

    color_map = {
        "False":   INK["secondary"],   # dark gray
        "Unknown": INK["hairline"],    # light gray
        "True":    ACCENT["hero"],     # pink
        "Rest":    INK["secondary"],   # dark gray
    }
    size_map = {"False": 90, "Unknown": 80, "True": 120, "Rest": 100}

    # Connector spans the min..max of the displayed group %s on each row
    for i, row in df.iterrows():
        if compare_mode == "vs_rest":
            lo = min(row["pos_pct"], row["rest_pct"])
            hi = max(row["pos_pct"], row["rest_pct"])
        elif show_unknown:
            lo = min(row["pos_pct"], row["neg_pct"], row["unk_pct"])
            hi = max(row["pos_pct"], row["neg_pct"], row["unk_pct"])
        else:
            lo = min(row["pos_pct"], row["neg_pct"])
            hi = max(row["pos_pct"], row["neg_pct"])
        ax.plot([lo, hi], [i, i], color=INK["hairline"], lw=2.0, zorder=1)

    if compare_mode == "vs_rest":
        n_rest = n_neg + n_unk
        ax.scatter(df["rest_pct"], y, color=color_map["Rest"], s=size_map["Rest"],
                   edgecolor=INK["canvas"], lw=1.2, zorder=3,
                   label=f"Rest  (CGL=False + Unknown, n={n_rest:,})")
        ax.scatter(df["pos_pct"], y, color=color_map["True"], s=size_map["True"],
                   edgecolor=INK["canvas"], lw=1.2, zorder=4,
                   label=f"CGL = True  (n={n_pos:,})")
        gap_col = "gap_rest"
    else:
        if show_unknown:
            ax.scatter(df["unk_pct"], y, color=color_map["Unknown"], s=size_map["Unknown"],
                       edgecolor=INK["canvas"], lw=1.2, zorder=2,
                       label=f"CGL = Unknown  (n={n_unk:,})")
        ax.scatter(df["neg_pct"], y, color=color_map["False"], s=size_map["False"],
                   edgecolor=INK["canvas"], lw=1.2, zorder=3,
                   label=f"CGL−  (n={n_neg:,})")
        ax.scatter(df["pos_pct"], y, color=color_map["True"], s=size_map["True"],
                   edgecolor=INK["canvas"], lw=1.2, zorder=4,
                   label=f"CGL+  (n={n_pos:,})")
        gap_col = "gap"

    # Direct CGL+ % label, centered just above the pink dot (on top of the dot).
    for i, row in df.iterrows():
        ax.text(row["pos_pct"], i + 0.28, f"{row['pos_pct']:.0f}%",
                va="bottom", ha="center", zorder=6,
                fontsize=10, fontweight="bold", color=INK["primary"])

    # Gap annotation outside the right spine, colored by sign
    if max_x is None:
        if compare_mode == "vs_rest":
            max_x = max(df["pos_pct"].max(), df["rest_pct"].max()) * 1.18
        else:
            max_x = max(df["pos_pct"].max(), df["neg_pct"].max(), df["unk_pct"].max()) * 1.18
    _trans = blended_transform_factory(ax.transAxes, ax.transData)
    # Every gap is the same measure (CGL+ − CGL−), so every gap is one colour:
    # green = CGL+ higher, red = CGL− higher. "Which gaps matter" lives in the
    # summary table's Strength column, NOT in the gap colour.
    for i, row in df.iterrows():
        gap = row[gap_col]
        if gap > 0:
            gap_color = SEMANTIC["good"]
        elif gap < 0:
            gap_color = SEMANTIC["bad"]
        else:
            gap_color = INK["secondary"]
        ax.text(1.02, i, f"{gap:+.0f}%",
                transform=_trans, va="center", ha="left",
                fontsize=10, fontweight="bold", family="monospace",
                color=gap_color, clip_on=False)

    ax.set_yticks(y)
    ax.set_yticklabels(df["variable"], fontsize=12, fontweight="normal",
                       color=INK["primary"])
    ax.set_xlim(0, max_x)
    ax.set_xlabel("% of group endorsing", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color(INK["hairline"])
    ax.spines["bottom"].set_color(INK["hairline"])
    ax.grid(axis="x", linestyle=":", alpha=0.4, color=INK["hairline"])

    if compare_mode == "vs_rest":
        n_legend = 2
    else:
        n_legend = 3 if show_unknown else 2
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0),
              ncol=n_legend, frameon=False, fontsize=10,
              labelcolor=INK["secondary"])

    if group_separators:
        for sep_after in group_separators:
            ax.axhline(
                y=sep_after + 0.5,
                color=INK["tertiary"], lw=1.2, ls="--", alpha=0.6, zorder=0,
            )

    if group_labels:
        for text, y_pos in group_labels:
            # Family label OUTSIDE the chart, to the left of the data labels.
            ax.text(
                -0.34, y_pos, text,
                transform=ax.get_yaxis_transform(),
                ha="center", va="center", rotation=90, rotation_mode="anchor",
                fontsize=12, fontweight="bold", color=INK["primary"], zorder=5,
                clip_on=False,
            )


# ---------------------------------------------------------------------------
# Summary table drawn above a dumbbell chart (Highlight 6a / 6b)
# ---------------------------------------------------------------------------

def _h_band(h):
    """Plain-language strength band for a Cohen's h effect size."""
    a = abs(h)
    if a < 0.10:
        return "none"
    if a < 0.20:
        return "weak"
    if a < 0.50:
        return "moderate"
    return "strong"


_BAND_COLOR = {
    "none":     INK["hairline"],
    "weak":     ACCENT["soft"],
    "moderate": ACCENT["mid"],
    "strong":   ACCENT["hero"],
}


def _summary_table(ax, rows, first_header="Item"):
    """Compact summary table on its own blank axes, sitting above the chart.

    rows: list of (item, cgl_plus_str, cgl_minus_str, diff_str, strength_word),
    where strength_word is one of none/weak/moderate/strong (also the chip-colour key).
    Diff is green to match the chart's gap callout; Strength is a colour-coded chip.
    """
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    cols_x = [0.012, 0.44, 0.56, 0.68, 0.80]
    aligns = ["left", "center", "center", "center", "left"]
    headers = [first_header, "CGL+", "CGL−", "Diff", "Strength"]
    n = len(rows)
    top, bot = 0.92, 0.10
    step = (top - bot) / n
    for htext, x, a in zip(headers, cols_x, aligns):
        ax.text(x, top, htext, ha=a, va="center", fontsize=11,
                fontweight="bold", color=INK["primary"])
    ax.plot([0.0, 1.0], [top - step * 0.55] * 2, color=INK["secondary"], lw=1.1)
    for i, r in enumerate(rows):
        item, cp, cm, diff, strength = r
        y = top - step * (i + 1)
        ax.text(cols_x[0], y, item, ha="left", va="center",
                fontsize=10.5, color=INK["primary"])
        ax.text(cols_x[1], y, cp, ha="center", va="center",
                fontsize=10.5, color=INK["secondary"])
        ax.text(cols_x[2], y, cm, ha="center", va="center",
                fontsize=10.5, color=INK["secondary"])
        ax.text(cols_x[3], y, diff, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=SEMANTIC["good"])
        ax.text(cols_x[4], y, strength, ha="left", va="center",
                fontsize=10.5, fontweight="bold", color=INK["primary"],
                bbox=dict(boxstyle="round,pad=0.3", facecolor=_BAND_COLOR[strength],
                          alpha=0.5, edgecolor="none"))


# ---------------------------------------------------------------------------
# Figure 5: Soft erotic preferences (dumbbell, all items)
# ---------------------------------------------------------------------------

def figure_soft_erotic(df: pd.DataFrame) -> pd.DataFrame:
    # 'soft_erotic_clear' is a duplicate column of 'enthusiastic consent' (identical values) — drop one.
    soft_cols = [c for c in df.columns
                 if c.startswith("soft_erotic_") and c != "soft_erotic_clear"]
    stats = _build_endorsement_stats(df, soft_cols, r"^soft_erotic_")

    n_pos = (df["cgl_flag"] == "True").sum()
    n_neg = (df["cgl_flag"] == "False").sum()
    n_unk = (df["cgl_flag"] == "Unknown").sum()

    # Sort by CGL=True endorsement % (ascending → highest row sits at top)
    plot = stats.sort_values("pos_pct", ascending=True).reset_index(drop=True)

    color_map = {
        "False":   INK["secondary"],   # dark gray
        "Unknown": INK["hairline"],    # light gray
        "True":    ACCENT["hero"],     # pink
    }
    size_map = {"False": 90, "Unknown": 80, "True": 120}

    fig, ax = plt.subplots(figsize=(14, max(7, 0.55 * len(plot))))
    y = np.arange(len(plot))

    # Connector line spans CGL− .. CGL+ per row (Unknown excluded as missing-data)
    for i, row in plot.iterrows():
        lo = min(row["pos_pct"], row["neg_pct"])
        hi = max(row["pos_pct"], row["neg_pct"])
        ax.plot([lo, hi], [i, i], color=INK["hairline"], lw=2.0, zorder=1)

    ax.scatter(plot["neg_pct"], y, color=color_map["False"], s=size_map["False"],
               edgecolor=INK["canvas"], linewidth=1.2, zorder=3,
               label=f"CGL−  (n={n_neg:,})")
    ax.scatter(plot["pos_pct"], y, color=color_map["True"], s=size_map["True"],
               edgecolor=INK["canvas"], linewidth=1.2, zorder=4,
               label=f"CGL+  (n={n_pos:,})")

    # CGL=True direct % label next to the pink dot
    for i, row in plot.iterrows():
        ax.text(row["pos_pct"] + 0.6, i, f"{row['pos_pct']:.1f}%",
                va="center", ha="left",
                fontsize=10, fontweight="bold", color=INK["primary"])

    # Gap annotation outside the right spine, colored by sign
    _trans = blended_transform_factory(ax.transAxes, ax.transData)
    for i, row in plot.iterrows():
        gap = row["gap"]
        if gap > 0:
            gap_color = SEMANTIC["good"]
        elif gap < 0:
            gap_color = SEMANTIC["bad"]
        else:
            gap_color = INK["secondary"]
        ax.text(1.02, i, f"{gap:+.1f}%",
                transform=_trans, ha="left", va="center",
                fontsize=10, fontweight="bold", family="monospace",
                color=gap_color, clip_on=False)

    xmax = max(plot["pos_pct"].max(), plot["neg_pct"].max())
    ax.set_xlim(0, xmax * 1.18)
    ax.set_yticks(y)
    ax.set_yticklabels(plot["variable"], fontsize=12, fontweight="bold", color=INK["secondary"])
    ax.set_xlabel("% of group endorsing", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color(INK["hairline"])
    ax.spines["bottom"].set_color(INK["hairline"])
    ax.grid(axis="x", linestyle=":", alpha=0.4, color=INK["hairline"])

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0),
              ncol=2, frameon=False, fontsize=10, labelcolor=INK["secondary"])
    ax.text(0, 1.12,
            "Caretaker/caretakee dynamics: 4× more endorsed by CGL respondents (20% vs 5%)",
            transform=ax.transAxes, fontsize=14, fontweight="bold",
            color=INK["primary"], va="bottom")
    ax.text(0, 1.06,
            "Soft-erotic preferences by CGL group; rows ordered by CGL=True %.",
            transform=ax.transAxes, fontsize=10, style="italic",
            color=INK["secondary"], va="bottom")

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

    # Anchor rows — near-universal acts that are FLAT across CGL groups.
    # Auto-selected (NOT hardcoded): high endorsement + negligible gap. They are the
    # built-in control — if CGL just "said yes to everything," these would rise too.
    # They don't, so the spikes below are real signal, not a response-style artifact.
    anchor_mask = (acts_stats["pos_pct"] >= 60) & (acts_stats["gap"].abs() < 2.5)
    anchors = (acts_stats[anchor_mask]
               .sort_values("pos_pct", ascending=False).head(3).copy())
    anchor_names = set(anchors["variable"])

    # Distinctive acts = largest gaps, excluding the flat anchors.
    distinctive = (acts_stats[~acts_stats["variable"].isin(anchor_names)]
                   .sort_values("gap", ascending=False).head(6).copy())
    pos_top = pos_stats.sort_values("gap", ascending=False).head(min(6, len(pos_stats))).copy()

    # Stack bottom→top: positions · near-universal anchors (flat) · distinctive acts (on top).
    # Distinctive acts (facefucking etc.) sit ABOVE the near-universal anchors (handjobs etc.)
    # so CGL's real edge reads at the top. Within each block, order by gap (numeric
    # difference) — ascending sort puts the LARGEST gap at the TOP of its block
    # (fingering mouths leads the distinctive acts; handjobs leads the near-universal ones).
    pos_block = pos_top.sort_values("gap", ascending=True)
    dist_block = distinctive.sort_values("gap", ascending=True)
    anchor_block = anchors.sort_values("gap", ascending=True)
    plot_df = pd.concat([pos_block, anchor_block, dist_block], ignore_index=True)

    # Family-level geometry: keep both separators (acts vs positions, anchors vs
    # distinctive), but label each family ONCE, centered, on the left.
    sep_pos = len(pos_block) - 1
    sep_dist = len(pos_block) + len(anchor_block) - 1
    pos_label_y = (len(pos_block) - 1) / 2.0
    acts_label_y = (len(pos_block) + len(plot_df) - 1) / 2.0

    n_pos = (nsfw["cgl_flag"] == "True").sum()
    n_neg = (nsfw["cgl_flag"] == "False").sum()
    n_unk = (nsfw["cgl_flag"] == "Unknown").sum()

    fig = plt.figure(figsize=(14, max(7, 0.5 * len(plot_df)) + 2.4))
    ax = fig.add_subplot(111)
    max_x = max(plot_df["pos_pct"].max(), plot_df["neg_pct"].max()) * 1.22
    _dumbbell_panel(
        ax, plot_df, n_pos, n_neg, n_unk,
        max_x=max_x, pre_sorted=True, show_unknown=False,
        group_separators=[sep_pos, sep_dist],
        group_labels=[("POSITIONS", pos_label_y), ("ACTS", acts_label_y)],
    )
    ax.set_xticks([0, 20, 40, 60, 80, 100])

    # Highlight the top band — the distinctive face/mouth/control acts (CGL's real edge) — in red.
    # One continuous span (like 6b's cluster band), NOT a per-row loop — adjacent spans
    # leave faint seam lines between rows; a single span reads as one clean block.
    dist_lo = len(pos_block) + len(anchor_block)
    dist_hi = len(plot_df) - 1
    ax.axhspan(dist_lo - 0.5, dist_hi + 0.5, color=SEMANTIC["bad"], alpha=0.12, zorder=0)

    # Summary table (top): the few acts that lead + the flat baseline, with strength.
    top3 = distinctive.sort_values("gap", ascending=False).head(3)
    table_rows = [
        (r["variable"], f"{r['pos_pct']:.0f}%", f"{r['neg_pct']:.0f}%",
         f"+{r['gap']:.0f}", _h_band(r["h"]))
        for _, r in top3.iterrows()
    ]
    table_rows.append(("near-universal acts", "70–85%", "70–85%", "+0–2", "none"))

    fig.suptitle(
        "CGL's edge is a specific flavor — not 'more sex'",
        fontweight="bold", fontsize=15, y=0.985,
    )
    fig.text(
        0.5, 0.050,
        f"Big Kink Survey  ·  CGL+ n={n_pos:,} vs CGL− n={n_neg:,}  ·  dots = % endorsing  ·  "
        "Strength = effect size (Cohen's h): under .10 none · .10–.20 weak · .20–.50 moderate  ·  "
        "near-universal acts ≈ no gap → not just 'CGL endorses everything.'",
        ha="center", va="bottom", fontsize=8, color=INK["tertiary"], style="italic",
    )
    # Legend for the green callout — very bottom, in green to match the numbers.
    fig.text(
        0.5, 0.013,
        "Green +% on the right = the gap between the two dots (CGL+ minus CGL−) — "
        "how much MORE the CGL+ group endorses each item.",
        ha="center", va="bottom", fontsize=9, fontweight="bold", color=SEMANTIC["good"],
        bbox=dict(boxstyle="round,pad=0.3", facecolor=SEMANTIC["good"], alpha=0.12,
                  edgecolor="none"),
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.78])
    ax_tbl = fig.add_axes([0.07, 0.80, 0.86, 0.13])
    _summary_table(ax_tbl, table_rows, first_header="Act")
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
    n_com = min(8, len(com_stats))
    n_unc = min(6, len(unc_stats))
    com_top = com_stats.sort_values("gap", ascending=False).head(n_com).copy()
    unc_top = unc_stats.sort_values("gap", ascending=False).head(n_unc).copy()

    # Group the co-rising cluster CONTIGUOUSLY at the top of the common block, so it
    # reads as one signal (theme-grouped, not magnitude-sorted). The point of 6b is the
    # co-movement of these scenes, not any single bar — make that legible by adjacency.
    cluster_items = ["gentleness", "nonconsent", "power dynamics & d/s",
                     "humiliation", "sadomasochism"]
    cl_mask = com_top["variable"].isin(cluster_items)
    # Within each block, order by gap (numeric difference) — ascending sort puts the
    # LARGEST gap at the TOP of its block (gentleness leads the cluster, etc.).
    com_cluster = com_top[cl_mask].sort_values("gap", ascending=True)
    com_rest = com_top[~cl_mask].sort_values("gap", ascending=True)
    com_block = pd.concat([com_rest, com_cluster])           # cluster on top
    unc_block = unc_top.sort_values("gap", ascending=True)
    plot_df = pd.concat([unc_block, com_block], ignore_index=True)

    # Family-level geometry: keep both separators (cluster vs rest, common vs uncommon),
    # but label each family ONCE, centered, on the left.
    sep_unc = len(unc_block) - 1
    sep_rest = len(unc_block) + len(com_rest) - 1
    unc_label_y = (len(unc_block) - 1) / 2.0
    com_label_y = (len(unc_block) + len(plot_df) - 1) / 2.0
    cl_lo = len(unc_block) + len(com_rest)
    cl_hi = len(plot_df) - 1

    n_pos = (nsfw["cgl_flag"] == "True").sum()
    n_neg = (nsfw["cgl_flag"] == "False").sum()
    n_unk = (nsfw["cgl_flag"] == "Unknown").sum()

    fig = plt.figure(figsize=(14, max(7, 0.5 * len(plot_df)) + 2.4))
    ax = fig.add_subplot(111)
    max_x = max(plot_df["pos_pct"].max(), plot_df["neg_pct"].max()) * 1.22
    _dumbbell_panel(
        ax, plot_df, n_pos, n_neg, n_unk,
        max_x=max_x, pre_sorted=True, show_unknown=False,
        group_separators=[sep_unc, sep_rest],
        group_labels=[("UNCOMMON", unc_label_y), ("COMMON", com_label_y)],
    )
    ax.set_xticks([0, 20, 40, 60, 80, 100])

    # Shade the cluster band so "these rise together" reads at a glance.
    ax.axhspan(cl_lo - 0.5, cl_hi + 0.5, color=ACCENT["soft"], alpha=0.28, zorder=0)

    # Summary table (top): the cluster scenes that rise together, with strength.
    top4 = com_cluster.sort_values("gap", ascending=False).head(4)
    table_rows = [
        (r["variable"], f"{r['pos_pct']:.0f}%", f"{r['neg_pct']:.0f}%",
         f"+{r['gap']:.0f}", _h_band(r["h"]))
        for _, r in top4.iterrows()
    ]

    fig.suptitle(
        "The CGL scene signal is a cluster, not a single item",
        fontweight="bold", fontsize=15, y=0.985,
    )
    fig.text(
        0.5, 0.050,
        f"Big Kink Survey  ·  CGL+ n={n_pos:,} vs CGL− n={n_neg:,}  ·  dots = % endorsing  ·  "
        "Strength = effect size (Cohen's h): .10–.20 weak · .20–.50 moderate  ·  "
        "the cluster sits at moderate (h ≈ .25) — bigger than any single act.",
        ha="center", va="bottom", fontsize=8, color=INK["tertiary"], style="italic",
    )
    # Legend for the green callout — very bottom, in green to match the numbers.
    fig.text(
        0.5, 0.013,
        "Green +% on the right = the gap between the two dots (CGL+ minus CGL−) — "
        "how much MORE the CGL+ group endorses each item.",
        ha="center", va="bottom", fontsize=9, fontweight="bold", color=SEMANTIC["good"],
        bbox=dict(boxstyle="round,pad=0.3", facecolor=SEMANTIC["good"], alpha=0.12,
                  edgecolor="none"),
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.78])
    ax_tbl = fig.add_axes([0.07, 0.80, 0.86, 0.13])
    _summary_table(ax_tbl, table_rows, first_header="Scene")
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
    # Comparator is CGL+ vs CGL− (cgl==0). The Unknown cohort (~100% non-response on the
    # arousal block) is excluded: pooling it into a "Rest" group inflated several ORs via
    # differential, item-specific non-response. CGL+ and CGL− both answered these items.
    rows = []
    for col in kink_fields:
        pos = nsfw.loc[nsfw["cgl_flag"] == "True", col].dropna()
        neg = nsfw.loc[nsfw["cgl_flag"] == "False", col].dropna()
        a = int((pos >= 1).sum()); b = int((pos == 0).sum())
        c = int((neg >= 1).sum()); d = int((neg == 0).sum())
        n_pos_resp, n_neg_resp = a + b, c + d
        p_pos = a / n_pos_resp if n_pos_resp else np.nan
        p_neg = c / n_neg_resp if n_neg_resp else np.nan
        table = [[a, b], [c, d]]
        if min(n_pos_resp, n_neg_resp, a + c, b + d) == 0:
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
        h = cohens_h(p_pos, p_neg)
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

    # ----- Yes/No rates per group (denominator = each group's responders) -----
    pos_mask = nsfw["cgl_flag"] == "True"
    neg_mask = nsfw["cgl_flag"] == "False"
    n_pos = int(pos_mask.sum())
    n_neg = int(neg_mask.sum())
    # Rates computed over RESPONDERS (NaN dropped) so the bars match the OR/forest panel.
    # Both CGL+ and CGL− answered the arousal block at ~100% (they engaged the CGL item),
    # so unlike the old "Rest" comparator there is no differential-non-response artifact.
    rates = {}
    for k in res["variable"]:
        x = nsfw[k]
        pos_resp = int((x.notna() & pos_mask).sum())
        neg_resp = int((x.notna() & neg_mask).sum())
        rates[k] = dict(
            pos_yes=((x >= 1) & pos_mask).sum() / pos_resp if pos_resp else 0.0,
            pos_no=((x == 0) & pos_mask).sum() / pos_resp if pos_resp else 0.0,
            pos_resprate=pos_resp / n_pos if n_pos else 0.0,
            neg_yes=((x >= 1) & neg_mask).sum() / neg_resp if neg_resp else 0.0,
            neg_no=((x == 0) & neg_mask).sum() / neg_resp if neg_resp else 0.0,
            neg_resprate=neg_resp / n_neg if n_neg else 0.0,
        )

    # ----- Plot -----
    TIER_COLORS = TIER
    TIER_BADGE = {"strong": "★★★", "moderate": "★★", "weak": "★", "ns": ""}
    TIER_LABEL = {"strong": "★★★ strong", "moderate": "★★ moderate",
                  "weak": "★ weak", "ns": "n.s. after FDR"}
    C_YES  = SEMANTIC["good"]    # arousing — yes
    C_NO   = SEMANTIC["bad"]     # not arousing — no

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

        for y, prefix, alpha in [(y_top, "pos", 1.0), (y_bot, "neg", 0.78)]:
            yes = rates[k][f"{prefix}_yes"]
            no_ = rates[k][f"{prefix}_no"]
            axL.barh(y, yes, color=C_YES, alpha=alpha, edgecolor="white")
            axL.barh(y, no_, left=yes, color=C_NO, alpha=alpha, edgecolor="white")
            _pct_label(axL, yes / 2, y, yes, on_dark=True)
            _pct_label(axL, yes + no_ / 2, y, no_, on_dark=True)

        axL.text(-0.01, y_top, "CGL+", ha="right", va="center",
                 fontsize=8.5, fontweight="bold")
        axL.text(-0.01, y_bot, "CGL−", ha="right", va="center", fontsize=8.5)
        axL.text(0, y_top - 0.55, f"{k}   {TIER_BADGE[row['tier']]}",
                 ha="left", va="bottom", fontsize=10.5, fontweight="bold", color=c_tier)
        # Disclose how many of each group actually answered (both ~100% — no differential
        # non-response now that Unknown is excluded; shown for transparency).
        axL.text(1.0, y_top - 0.55,
                 f"answered:  CGL+ {rates[k]['pos_resprate']*100:.0f}%  ·  "
                 f"CGL− {rates[k]['neg_resprate']*100:.0f}%",
                 ha="right", va="bottom", fontsize=7.5, color=INK["tertiary"])

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
    axR.set_xlabel("Odds of endorsing  (CGL+ vs CGL−)", fontsize=9)
    axR.spines[["top", "right", "left"]].set_visible(False)

    # Header: title + sample sizes + caption
    fig.suptitle(
        "Kink-Specific Arousal: Response Distribution + Effect Size",
        fontsize=14, fontweight="bold", y=0.995,
    )
    fig.text(0.5, 0.965,
             f"CGL+ n = {n_pos:,}   ·   CGL− n = {n_neg:,}   ·   "
             "left bars = arousing vs not among respondents "
             "(both groups answered the arousal block at ~100% — no differential non-response)",
             ha="center", va="top", fontsize=10, style="italic", color="#555")
    caption = (
        "How to read each forest row:  OR  ·  h  ·  p\n"
        "  OR  (odds ratio, log axis) — odds of endorsing in CGL+ ÷ CGL−.  null = 1×.  "
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
    print("→ figure 2: emotion (mirror — Highlight 2 hero)")
    figure_emotion_mirror(df)
    print("→ figure 2 (appendix): full emotion distributions")
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
