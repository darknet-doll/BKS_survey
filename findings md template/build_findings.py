"""
Build a public-facing, regenerable findings doc from the CGL EDA dataset.

Usage (from notebook or script):
    from findings.build_findings import render
    render(df, out="findings/1a_CGL_EDA_Findings.md")

Or end-to-end from CSV:
    python -m findings.build_findings
"""

from __future__ import annotations

import os
from datetime import date
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from matplotlib.patches import Patch
from scipy.stats import kruskal, mannwhitneyu, spearmanr

THIS_DIR = Path(__file__).parent
FIG_DIR = THIS_DIR / "figures"
TEMPLATE_PATH = THIS_DIR / "template.md.j2"

OCEAN_COLS = [
    "openness", "consciensiousness", "extroversion",
    "neuroticism", "agreeableness", "powerlessness",
]

DS_ORDER = [
    "Totally submissive", "Moderately submissive", "Slightly submissive",
    "Switch/equal/no preference",
    "Slightly dominant", "Moderately dominant", "Totally dominant",
]
DS_RANK = {cat: i + 1 for i, cat in enumerate(DS_ORDER)}

VARIETY_NUM_MAP = {
    "Very narrow": 1, "A little narrow": 2, "Somewhat narrow": 3,
    "Equally narrow and broad": 4,
    "A little broad": 5, "Somewhat broad": 6, "Very broad": 7,
}

FLAG_ORDER = ["False", "True", "Unknown"]
FLAG_PALETTE = {"False": "#d62728", "True": "#2ca02c", "Unknown": "#888888"}


# ---------- helpers ----------------------------------------------------------

def _add_cgl_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Add string-valued cgl_flag column ('True'/'False'/'Unknown')."""
    df = df.copy()
    df["cgl_flag"] = np.where(
        df["cgl"] >= 1, "True",
        np.where(df["cgl"] == 0, "False", "Unknown"),
    )
    return df


def _cohens_d(a: pd.Series, b: pd.Series) -> float:
    a = a.dropna()
    b = b.dropna()
    pooled = ((a.std() ** 2 + b.std() ** 2) / 2) ** 0.5
    return float((a.mean() - b.mean()) / pooled) if pooled else 0.0


def _interpret_d(d: float) -> str:
    ad = abs(d)
    if ad < 0.10: return "trivial"
    if ad < 0.20: return "very small"
    if ad < 0.50: return "small"
    if ad < 0.80: return "medium"
    return "large"


def _eta_squared_kw(h: float, k: int, n: int) -> float:
    return max(0.0, (h - k + 1) / (n - k)) if n > k else 0.0


def _interpret_eta(e: float) -> str:
    if e < 0.01: return "negligible"
    if e < 0.06: return "small"
    if e < 0.14: return "medium"
    return "large"


def _sig(p: float) -> str:
    if p < 0.001: return "***"
    if p < 0.01: return "**"
    if p < 0.05: return "*"
    return "ns"


def _fmt_p(p: float) -> str:
    return f"{p:.3g}" if p >= 0.001 else "<0.001"


def _save_fig(name: str) -> str:
    """Save current figure to figures/<name>.png. Return relative md path."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / f"{name}.png"
    plt.savefig(path, dpi=140, bbox_inches="tight")
    plt.close()
    return f"figures/{name}.png"


# ---------- chapter 1: personality null --------------------------------------

def chapter1_stats(df: pd.DataFrame) -> dict:
    rows = []
    for trait in OCEAN_COLS:
        cgl = df.loc[df.cgl_flag == "True", trait].dropna()
        non = df.loc[df.cgl_flag == "False", trait].dropna()
        d = _cohens_d(cgl, non)
        rows.append({
            "trait": trait,
            "mean_cgl": round(cgl.mean(), 2),
            "mean_non": round(non.mean(), 2),
            "diff": round(cgl.mean() - non.mean(), 2),
            "d": round(d, 3),
            "magnitude": _interpret_d(d),
            "n_cgl": int(len(cgl)),
            "n_non": int(len(non)),
        })
    table = pd.DataFrame(rows)
    max_abs_d = float(table["d"].abs().max())
    return {
        "trait_table": table,
        "max_abs_d": round(max_abs_d, 3),
        "all_trivial": all(t == "trivial" for t in table["magnitude"]),
        "n_cgl_total": int((df.cgl_flag == "True").sum()),
        "n_non_total": int((df.cgl_flag == "False").sum()),
        "n_unknown_total": int((df.cgl_flag == "Unknown").sum()),
        "n_total": int(len(df)),
    }


def chapter1_figure(df: pd.DataFrame, stats: dict) -> str:
    """Forest-plot of Cohen's d per OCEAN trait (with the 'trivial' band shaded)."""
    table = stats["trait_table"].sort_values("d")
    fig, ax = plt.subplots(figsize=(9, 4.5))

    # Shaded "trivial" band (|d| < 0.1)
    ax.axvspan(-0.1, 0.1, color="#e7f5e1", alpha=0.8, zorder=0)
    ax.text(0, ax.get_ylim()[1] if ax.get_ylim()[1] != 1 else len(table) - 0.5,
            "trivial",
            ha="center", va="bottom", fontsize=9, color="#3a7a2c",
            fontweight="bold")

    y = np.arange(len(table))
    ax.scatter(table["d"], y, s=120, color="#2563eb",
               edgecolor="white", linewidth=1.5, zorder=3)
    for yi, d in zip(y, table["d"]):
        ax.plot([0, d], [yi, yi], color="#94a3b8", linewidth=2, zorder=2)

    ax.axvline(0, color="#475569", linewidth=0.8, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels(table["trait"])
    ax.set_xlabel("Cohen's d  (CGL − non-CGL,  pooled SD units)")
    ax.set_xlim(-0.5, 0.5)
    ax.set_title("Personality difference between CGL and non-CGL respondents",
                 fontweight="bold", loc="left", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle=":", alpha=0.4)

    return _save_fig("ch1_ocean_cohens_d")


# ---------- chapter 2: power dynamic structure -------------------------------

def chapter2_stats(df: pd.DataFrame) -> dict:
    # D/s 3-bucket distribution by cgl_flag
    sub_cats = DS_ORDER[:3]
    eq_cat = DS_ORDER[3]
    dom_cats = DS_ORDER[4:]
    sub = df.dropna(subset=["ds_preference"]).copy()
    pivot = (
        pd.crosstab(sub["cgl_flag"], sub["ds_preference"], normalize="index")
        .mul(100)
        .reindex(index=FLAG_ORDER, columns=DS_ORDER, fill_value=0)
    )
    bucket_pivot = pd.DataFrame({
        "Submissive %": pivot[sub_cats].sum(axis=1).round(1),
        "Switch/Equal %": pivot[eq_cat].round(1),
        "Dominant %": pivot[dom_cats].sum(axis=1).round(1),
    })
    bucket_pivot["n"] = sub.groupby("cgl_flag").size().reindex(FLAG_ORDER).fillna(0).astype(int)
    bucket_pivot = bucket_pivot[["n", "Submissive %", "Switch/Equal %", "Dominant %"]]

    # KW omnibus on the ordinal rank
    sub["ds_rank"] = sub["ds_preference"].map(DS_RANK)
    groups = {f: sub.loc[sub.cgl_flag == f, "ds_rank"].dropna().values for f in FLAG_ORDER}
    groups = {f: g for f, g in groups.items() if len(g) > 0}
    h_stat, p_kw = kruskal(*groups.values())
    n_total = sum(len(g) for g in groups.values())
    eta = _eta_squared_kw(h_stat, len(groups), n_total)

    # Pairwise Mann-Whitney + Bonferroni
    pairs = list(combinations(groups.keys(), 2))
    pair_rows = []
    for f1, f2 in pairs:
        _, p_pair = mannwhitneyu(groups[f1], groups[f2], alternative="two-sided")
        p_adj = min(p_pair * len(pairs), 1.0)
        pair_rows.append({"pair": f"{f1} vs {f2}", "p_adj": _fmt_p(p_adj), "sig": _sig(p_adj)})

    # Role interest by cgl_flag — % of each cgl_flag group that endorses each role
    role_cols = [c for c in df.columns if c.startswith("role_")]
    role_pct = df.groupby("cgl_flag")[role_cols].mean().mul(100).round(1).T
    role_pct.index = role_pct.index.str.replace("role_", "", regex=False)
    role_pct = role_pct.reindex(columns=FLAG_ORDER, fill_value=0)
    role_pct["gap_T_minus_F"] = (role_pct["True"] - role_pct["False"]).round(1)
    role_top = role_pct.sort_values("gap_T_minus_F", ascending=False).head(10)
    role_bottom = role_pct.sort_values("gap_T_minus_F", ascending=True).head(5)

    # Caretaker/caretakee soft-erotic dynamics — column-normalized %
    care_col = "soft_erotic_caretaker/caretakee dynamics"
    care_pivot = (
        pd.crosstab(df[care_col], df["cgl_flag"], normalize="columns")
        .mul(100).round(1)
        .reindex(columns=FLAG_ORDER, fill_value=0)
    )

    return {
        "bucket_pivot": bucket_pivot,
        "h_stat": round(h_stat, 1),
        "p_kw": _fmt_p(p_kw),
        "p_kw_sig": _sig(p_kw),
        "eta": round(eta, 4),
        "eta_label": _interpret_eta(eta),
        "n_kw": n_total,
        "pairs": pair_rows,
        "role_top": role_top,
        "role_bottom": role_bottom,
        "care_pivot": care_pivot,
    }


def chapter2_figure(df: pd.DataFrame, stats: dict) -> str:
    """Diverging Likert: D/S preference centred on Switch."""
    sub = df.dropna(subset=["ds_preference"]).copy()
    n_per_flag = sub["cgl_flag"].value_counts()
    pivot = (
        pd.crosstab(sub["cgl_flag"], sub["ds_preference"], normalize="index")
        .mul(100)
        .reindex(index=FLAG_ORDER, columns=DS_ORDER, fill_value=0)
    )

    ds_colors = ["#08306b", "#2171b5", "#6baed6",
                 "#bdbdbd",
                 "#fb6a4a", "#cb181d", "#67000d"]
    color_map = dict(zip(DS_ORDER, ds_colors))
    switch_idx = DS_ORDER.index("Switch/equal/no preference")

    fig, ax = plt.subplots(figsize=(11, 4.5))
    bar_h = 0.55
    for row_i, flag in enumerate(FLAG_ORDER):
        row = pivot.loc[flag]
        sub_total = row.iloc[:switch_idx].sum()
        eq_total = row.iloc[switch_idx]
        cursor = -eq_total / 2 - sub_total
        for cat in DS_ORDER:
            w = row[cat]
            ax.barh(row_i, w, left=cursor, height=bar_h,
                    color=color_map[cat], edgecolor="white", linewidth=0.5)
            if w > 4:
                ax.text(cursor + w / 2, row_i, f"{w:.0f}%",
                        ha="center", va="center", fontsize=8,
                        color="white" if cat != "Switch/equal/no preference" else "black",
                        fontweight="bold")
            cursor += w

    ax.set_yticks(range(len(FLAG_ORDER)))
    ax.set_yticklabels([f"{f}\n(n={int(n_per_flag.get(f,0)):,})" for f in FLAG_ORDER])
    ax.set_xlabel('Percentage points  (centred on "Switch/Equal")')
    ax.axvline(0, color="#475569", linewidth=0.8, linestyle="--")
    ax.set_title("D/S preference by CGL identification",
                 fontweight="bold", loc="left", pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    handles = [Patch(color=ds_colors[i], label=DS_ORDER[i]) for i in range(len(DS_ORDER))]
    ax.legend(handles=handles, bbox_to_anchor=(0.5, -0.25), loc="upper center",
              ncol=4, frameon=False, fontsize=8)

    return _save_fig("ch2_ds_preference")


# ---------- chapter 3: arousal content ---------------------------------------

def chapter3_stats(df: pd.DataFrame) -> dict:
    # CGL intensity distribution among CGL=True (cgl 1..5)
    cgl_only = df[df.cgl_flag == "True"]
    intensity = (
        cgl_only["cgl"].value_counts(normalize=True).mul(100)
        .round(1).sort_index()
    )
    intensity_table = pd.DataFrame({
        "Arousal Score": intensity.index.astype(int),
        "% of CGL=True": intensity.values,
    })

    # Age gap / regression / progression / older — % "Arousing" (>=1) by cgl_flag
    age_metrics = ["agegap", "regression", "progression", "older"]
    rows = []
    for col in age_metrics:
        sub = df.dropna(subset=[col]).copy()
        sub["arouse"] = (sub[col].astype(float) >= 1).astype(int)
        per_flag = sub.groupby("cgl_flag")["arouse"].mean().mul(100).round(1)
        rows.append({
            "metric": col,
            "True %": per_flag.get("True", 0),
            "False %": per_flag.get("False", 0),
            "Unknown %": per_flag.get("Unknown", 0),
            "Δ (T−F)": round(per_flag.get("True", 0) - per_flag.get("False", 0), 1),
            "n_total": int(len(sub)),
        })
    age_table = pd.DataFrame(rows)

    # Soft erotic preferences (excluding the caretaker dynamic — it's in Ch.2)
    soft_cols = [c for c in df.columns if c.startswith("soft_erotic_")
                 and "caretaker" not in c]
    soft_rows = []
    for col in soft_cols:
        sub = df.dropna(subset=[col])
        pct_T = sub.loc[sub.cgl_flag == "True", col].astype(float).mean() * 100 if (sub.cgl_flag == "True").any() else 0
        pct_F = sub.loc[sub.cgl_flag == "False", col].astype(float).mean() * 100 if (sub.cgl_flag == "False").any() else 0
        label = col.replace("soft_erotic_", "").strip()
        soft_rows.append({
            "preference": label,
            "True %": round(pct_T, 1),
            "False %": round(pct_F, 1),
            "Δ (T−F)": round(pct_T - pct_F, 1),
        })
    soft_table = pd.DataFrame(soft_rows).sort_values("Δ (T−F)", ascending=False)

    return {
        "intensity_table": intensity_table,
        "n_cgl_only": int(len(cgl_only)),
        "age_table": age_table,
        "soft_table": soft_table,
    }


def chapter3_figure(df: pd.DataFrame, stats: dict) -> str:
    """Stacked bars: % Arousing for age-related metrics, by cgl_flag."""
    age_metrics = ["agegap", "regression", "progression", "older"]
    pivot_rows = []
    for col in age_metrics:
        sub = df.dropna(subset=[col]).copy()
        sub["arouse"] = (sub[col].astype(float) >= 1).astype(int)
        for flag in ["True", "False"]:
            grp = sub[sub.cgl_flag == flag]
            if len(grp):
                pivot_rows.append({
                    "metric": col, "cgl_flag": flag,
                    "pct": grp["arouse"].mean() * 100,
                })
    long = pd.DataFrame(pivot_rows)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = {"True": "#2ca02c", "False": "#d62728"}
    width = 0.38
    x = np.arange(len(age_metrics))
    for i, flag in enumerate(["False", "True"]):
        sub = long[long.cgl_flag == flag].set_index("metric").reindex(age_metrics)
        bars = ax.bar(x + (i - 0.5) * width, sub["pct"], width=width,
                      color=colors[flag], label=f"CGL={flag}", edgecolor="white")
        for b, v in zip(bars, sub["pct"]):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}%",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(age_metrics)
    ax.set_ylabel("% finding it arousing (any score ≥ 1)")
    ax.set_title("Age-related themes: arousal by CGL identification",
                 fontweight="bold", loc="left", pad=10)
    ax.legend(frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.set_ylim(0, max(long["pct"].max() * 1.2, 50))
    return _save_fig("ch3_age_arousal")


# ---------- chapter 4: emotional desires -------------------------------------

def chapter4_stats(df: pd.DataFrame) -> dict:
    def by_flag(col):
        sub = df.dropna(subset=[col]).copy()
        pivot = pd.crosstab(sub[col], sub["cgl_flag"], normalize="columns").mul(100)
        pivot = pivot.reindex(columns=FLAG_ORDER, fill_value=0).round(1)
        pivot["Δ (T−F)"] = (pivot["True"] - pivot["False"]).round(1)
        # Filter out tiny rows
        pivot = pivot[pivot.max(axis=1) >= 2.0]
        return pivot.sort_values("Δ (T−F)", ascending=False)

    you = by_flag("youfeelmost")
    other = by_flag("otherfeel1most")
    return {
        "you_table": you,
        "other_table": other,
        "n_you": int(df["youfeelmost"].notna().sum()),
        "n_other": int(df["otherfeel1most"].notna().sum()),
        "top_you_cgl": you.sort_values("True", ascending=False).head(3).index.tolist(),
        "top_other_cgl": other.sort_values("True", ascending=False).head(3).index.tolist(),
    }


def chapter4_figure(df: pd.DataFrame, stats: dict) -> str:
    """Dumbbell: youfeelmost — CGL True vs False % per emotion category."""
    you = stats["you_table"].copy()
    you = you.loc[you.index.notnull()]
    you = you.iloc[::-1]  # ascending by Δ for barh-friendly order
    fig, ax = plt.subplots(figsize=(11, max(4.5, 0.45 * len(you))))
    y = np.arange(len(you))
    for yi, cat in enumerate(you.index):
        ax.plot([you.loc[cat, "False"], you.loc[cat, "True"]], [yi, yi],
                color="#cbd5e1", linewidth=2, zorder=1)
    ax.scatter(you["False"], y, color=FLAG_PALETTE["False"], s=110, zorder=3,
               edgecolor="white", linewidth=1.4, label="CGL=False")
    ax.scatter(you["True"], y, color=FLAG_PALETTE["True"], s=110, zorder=3,
               edgecolor="white", linewidth=1.4, label="CGL=True")
    ax.set_yticks(y)
    ax.set_yticklabels(you.index)
    ax.set_xlabel("% within group selecting this emotion as the one they most want to feel")
    ax.set_title("Emotion CGL respondents most want to feel (vs non-CGL)",
                 fontweight="bold", loc="left", pad=10)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    return _save_fig("ch4_youfeelmost")


# ---------- chapter 5: variety as a function of role count -------------------

def chapter5_stats(df: pd.DataFrame) -> dict:
    role_cols = [c for c in df.columns if c.startswith("role_")]
    df = df.copy()
    df["n_roles"] = df[role_cols].sum(axis=1)
    df["variety_num"] = df["sexual_interest_variety"].map(VARIETY_NUM_MAP)

    mask = df["n_roles"].notna() & df["variety_num"].notna()
    rho, p = spearmanr(df.loc[mask, "n_roles"], df.loc[mask, "variety_num"])

    by_n = df.groupby("n_roles")["variety_num"].agg(["mean", "count"]).round(2)
    by_n.columns = ["mean_variety", "n"]
    by_n = by_n.reset_index()
    # Bin sparsely-populated tail for the headline table
    head = by_n[by_n["n_roles"] <= 6].copy()
    tail = by_n[by_n["n_roles"] > 6]
    if len(tail):
        tail_row = pd.DataFrame([{
            "n_roles": "7+",
            "mean_variety": round(
                (tail["mean_variety"] * tail["n"]).sum() / tail["n"].sum(), 2),
            "n": int(tail["n"].sum()),
        }])
        head = pd.concat([head, tail_row], ignore_index=True)
    head["n_roles"] = head["n_roles"].astype(str)

    # Single-role Cohen's d on variety (role users vs non-role users)
    d_rows = []
    for r in role_cols:
        a = df.loc[df[r] == 1, "variety_num"].dropna()
        b = df.loc[df[r] == 0, "variety_num"].dropna()
        if len(a) > 30 and len(b) > 30:
            d_rows.append({
                "role": r.replace("role_", ""),
                "mean_with": round(a.mean(), 2),
                "mean_without": round(b.mean(), 2),
                "d": round(_cohens_d(a, b), 2),
                "n_with": int(len(a)),
            })
    d_table = pd.DataFrame(d_rows).sort_values("d", key=lambda s: s.abs(),
                                               ascending=False).head(8)

    # 0 roles vs any roles, mean variety
    zero_mean = df.loc[df.n_roles == 0, "variety_num"].mean()
    any_mean = df.loc[df.n_roles >= 1, "variety_num"].mean()
    return {
        "rho": round(rho, 3),
        "p_rho": _fmt_p(p),
        "p_rho_sig": _sig(p),
        "n_rho": int(mask.sum()),
        "by_n_roles": head,
        "d_table": d_table,
        "zero_mean": round(float(zero_mean), 2),
        "any_mean": round(float(any_mean), 2),
        "zero_any_diff": round(float(any_mean - zero_mean), 2),
    }


def chapter5_figure(df: pd.DataFrame, stats: dict) -> str:
    """Mean variety preference vs n_roles."""
    role_cols = [c for c in df.columns if c.startswith("role_")]
    df = df.copy()
    df["n_roles"] = df[role_cols].sum(axis=1)
    df["variety_num"] = df["sexual_interest_variety"].map(VARIETY_NUM_MAP)
    grp = df.groupby("n_roles")["variety_num"].agg(["mean", "count"])
    grp = grp[grp["count"] >= 30]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.scatter(grp.index, grp["mean"], s=grp["count"] / 8,
               color="#2563eb", alpha=0.75, edgecolor="white", linewidth=1)
    ax.plot(grp.index, grp["mean"], color="#2563eb", linewidth=1, alpha=0.4)
    ax.axhline(grp["mean"].iloc[0], color="#94a3b8", linewidth=0.8,
               linestyle="--", label=f"baseline (0 roles): {grp['mean'].iloc[0]:.2f}")
    ax.set_xlabel("Number of roles endorsed (out of 21)")
    ax.set_ylabel("Mean variety preference  (1=very narrow → 7=very broad)")
    ax.set_title(
        f"Variety preference scales with role count  "
        f"(Spearman ρ = {stats['rho']}, n = {stats['n_rho']:,})",
        fontweight="bold", loc="left", pad=10,
    )
    ax.legend(frameon=False, loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(linestyle=":", alpha=0.5)
    return _save_fig("ch5_variety_vs_roles")


# ---------- render orchestrator ----------------------------------------------

def _df_to_md(df: pd.DataFrame, **kwargs) -> str:
    """Convert df to markdown without an index, with sensible float format."""
    if df is None or len(df) == 0:
        return "_no rows_"
    return df.to_markdown(index=kwargs.pop("index", False),
                          floatfmt=kwargs.pop("floatfmt", ".2f"),
                          **kwargs)


def render(df: pd.DataFrame | None = None,
           csv: str | None = None,
           out: str | os.PathLike = "1a_CGL_EDA_Findings.md") -> Path:
    """Render the findings markdown. Either pass a df or a csv path."""
    if df is None:
        if csv is None:
            csv = "../database/cgl_BKS_data.csv"
        df = pd.read_csv(csv)
        if "role_Nazis" in df.columns:
            df = df.drop(columns="role_Nazis")
    df = _add_cgl_flag(df)

    s1 = chapter1_stats(df); f1 = chapter1_figure(df, s1)
    s2 = chapter2_stats(df); f2 = chapter2_figure(df, s2)
    s3 = chapter3_stats(df); f3 = chapter3_figure(df, s3)
    s4 = chapter4_stats(df); f4 = chapter4_figure(df, s4)
    s5 = chapter5_stats(df); f5 = chapter5_figure(df, s5)

    env = Environment(
        loader=FileSystemLoader(THIS_DIR),
        undefined=StrictUndefined,
        trim_blocks=True, lstrip_blocks=True,
    )
    env.filters["mdtable"] = _df_to_md
    template = env.get_template(TEMPLATE_PATH.name)

    rendered = template.render(
        generated_on=date.today().isoformat(),
        n_total=int(len(df)),
        n_cgl_true=int((df.cgl_flag == "True").sum()),
        n_cgl_false=int((df.cgl_flag == "False").sum()),
        n_cgl_unknown=int((df.cgl_flag == "Unknown").sum()),
        ch1=s1, ch1_fig=f1,
        ch2=s2, ch2_fig=f2,
        ch3=s3, ch3_fig=f3,
        ch4=s4, ch4_fig=f4,
        ch5=s5, ch5_fig=f5,
    )
    out_path = Path(out)
    if not out_path.is_absolute():
        out_path = THIS_DIR.parent / out_path
    out_path.write_text(rendered)
    return out_path


if __name__ == "__main__":
    p = render()
    print(f"Wrote: {p}")
