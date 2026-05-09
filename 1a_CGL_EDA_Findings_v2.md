# Role × D/s × Powerlessness — A Deeper Look
### Where kink actually lives in the BKS survey

> _Companion to `1a_CGL_EDA_Findings.md`. Generated 2026-05-09 from `1a_CGL_EDA.ipynb`._
> _Sample: **2,845** CGL-positive, **1,295** CGL-negative, **11,363** without a CGL response (total **15,503**)._

---

## How to read this document

Same structure as the main findings doc. Each chapter has:

1. **Pullquote** — the one-line takeaway.
2. **30-second version** — plain language, no jargon.
3. **Headline chart + table** — the picture and the numbers behind it.
4. **The numbers in detail** — secondary breakdowns.
5. **How we measured this** — methods in plain English.
6. **Full stats** — the technical version.
7. **What this means (and doesn't mean)** — interpretation + caveats.

If you only have a minute, read the pullquote and the 30-second version. Skeptics, read all the way down.

---

# Chapter A — Roles aren't kink-neutral: each one has a D/s tilt

> **Across the 21 role categories in the survey, users self-report meaningfully different D/s preferences. Sub-leaning roles cluster around authority/professional archetypes (Gynecologists −0.41, Priests −0.31, Criminals −0.25); dom-leaning roles cluster around feminine/service archetypes (Geishas +0.49, Nuns +0.48, Cheerleaders +0.43). The total tilt range is just under one full step on the 7-point D/s scale.**

### The 30-second version

If you ask "do roles attract people of a particular dominance/submission preference?" the answer in this dataset is **yes, but mildly**. No role is exclusively for submissives or dominants — every role has all three groups in it. But the *center of gravity* shifts.

The cleanest way to see this is a single number per role: each role's average position on the 1–7 D/s scale, centered on "Switch/equal" so 0 means neutral. Submissives sit toward −3 and dominants toward +3.

**Cheerleaders, Nuns, Geishas, Catgirls, Nurses** all have positive lean — the users who endorse these roles tend dominant on average. **Gynecologists, Priests, Catboys, Criminals, Doctors** all have negative lean — those role-endorsers tend submissive.

The lean range (about 0.9 points end-to-end) is modest. This is a *tilt*, not a *category*. Don't read "Cheerleaders are for dominants" — read "if you grabbed a random Cheerleader-endorser and a random Gynecologist-endorser, the Cheerleader-endorser would on average be about half a D/s level more dominant."

![Role × D/s heatmap](figures/role_ds_heatmap.png)
_Notebook reference: cell labeled `Role vs D/s Preference (collapsed to 3 levels)` in `1a_CGL_EDA.ipynb`._

### Headline numbers — the lean ranking

Lean = mean D/s rank (1 = Totally submissive, 7 = Totally dominant) **minus 4** (Switch/equal). Negative = sub-leaning role; positive = dom-leaning role. Sorted ascending.

| role                | n     | sub % | equal % | dom % | lean   |
|:--------------------|------:|------:|--------:|------:|-------:|
| Gynecologists       |   729 |    45 |      29 |    26 | −0.41 |
| Priests             |   582 |    42 |      30 |    27 | −0.31 |
| Catboys             |   533 |    39 |      36 |    26 | −0.29 |
| Criminals           | 1,547 |    40 |      31 |    29 | −0.25 |
| Doctors             | 2,815 |    36 |      31 |    33 | −0.06 |
| Gigolos             |   174 |    36 |      30 |    34 | −0.04 |
| Teachers            | 4,255 |    33 |      31 |    36 | +0.06 |
| Athletes            | 2,250 |    30 |      33 |    37 | +0.12 |
| Scientists          | 1,296 |    29 |      33 |    38 | +0.16 |
| Students            | 3,201 |    28 |      31 |    41 | +0.25 |
| Maids               | 3,608 |    28 |      32 |    40 | +0.25 |
| Strippers           | 2,647 |    27 |      33 |    40 | +0.26 |
| Babysitter          | 2,827 |    28 |      31 |    41 | +0.27 |
| Librarians          | 2,118 |    26 |      32 |    41 | +0.29 |
| Celebrities         | 1,738 |    26 |      32 |    41 | +0.30 |
| Escorts/prostitutes | 1,956 |    27 |      31 |    42 | +0.32 |
| Nurses              | 3,172 |    25 |      32 |    43 | +0.35 |
| Catgirls            | 2,199 |    25 |      33 |    42 | +0.36 |
| Cheerleaders        | 2,890 |    24 |      31 |    45 | +0.43 |
| Nuns                | 1,379 |    23 |      32 |    45 | +0.48 |
| Geishas             |   697 |    21 |      33 |    45 | +0.49 |

### How we measured this

- **Variables.** 21 binary `role_*` flags (1 if the respondent endorsed that role, 0 otherwise) and the ordinal `ds_preference` field, mapped to a 1–7 rank.
- **Lean score.** For each role, restrict to respondents who endorsed it and have a D/s answer; take the mean rank; subtract 4. The result is in the same units as the original 1–7 scale, just centered on "Switch/equal." A value of +0.5 means "on average, half a level more dominant than the neutral midpoint."
- **Why a lean score and not a correlation coefficient?** The lean reads in original units: "+1.0 = one full D/s level more dominant on average." A point-biserial correlation would give the same direction but in standard-deviation-ish units (`r ≈ 0.04 - 0.17` for the roles in this table — see "Full stats" below) — abstract enough that most readers can't compare two of them.

### Full stats

For each role, the point-biserial correlation between the binary `role_*` flag and `ds_rank` (1–7), with significance at the conventional levels. Almost everything is significant given n; the magnitudes are what matter.

The strongest dom-pulling correlations: Cheerleaders r = +0.170, Nurses +0.157, Maids +0.140, Catgirls +0.128, Babysitter +0.124. The strongest sub-pulling: Doctors +0.032 (negligible), Gynecologists −0.030, Priests −0.016, Criminals −0.014, Catboys −0.013.

Sub-leaning roles have *smaller absolute* correlations than dom-leaning roles — this is because sub-leaning roles tend to be the smaller, niche categories with lower n. The lean score side-steps this issue by using the role mean directly.

### What this means (and doesn't mean)

The pattern in the dom-leaning column — Cheerleaders, Nuns, Catgirls, Geishas, Nurses, Escorts — is striking enough to flag, but it's also where over-interpretation is easiest. The survey doesn't separate "roles I want to be" from "roles I want to play with," so we can't tell from this data whether dom-leaning users want to *be* a Cheerleader (top from below, performative) or want to *be with* a Cheerleader (top a bratty submissive). Either reading is consistent with the numbers; only the survey designers can disambiguate.

What the data does say cleanly: **role choice is not orthogonal to D/s identity.** If we'd seen a flat lean column (all roles within ±0.05 of 0), we'd have to conclude role-fantasy and D/s preference are unrelated dimensions. We didn't see that. The roles spread across nearly a full D/s level, the spread is internally consistent (Chapter C below confirms it cross-validates with Powerlessness), and the sample sizes for the lean ranking are robust (smallest is Gigolos at n = 174; the rest are 500+).

---

# Chapter B — Powerlessness is the variable that knew

> **Powerlessness was bundled with the Big Five in the original analysis and is just as flat for CGL identification as the rest (gap = +0.15 points, Cohen's d = +0.04, η² = 0.0013 — all trivial). But unlike the Big Five, Powerlessness tracks the D/s scale: average rises from −0.12 at "Totally Dominant" to +1.51 at "Totally Submissive," a 1.6-point shift across the 7 levels (Spearman ρ = −0.137).**

### The 30-second version

The original analysis lumped Powerlessness in with OCEAN and reported the same flat finding for all six: "personality doesn't predict CGL." That conclusion was correct *for CGL*. But Powerlessness was being asked the wrong question.

Powerlessness isn't a personality dimension like Openness or Conscientiousness — it's a kink-adjacent self-report. The right question for it isn't "do CGL users score differently?" (they don't, meaningfully) but "does it line up with D/s preference?" (yes, it does).

When we plot mean Powerlessness against the seven D/s levels, the slope is monotone: every step toward "more submissive" raises the average by about 0.27 points. That's the kind of graded relationship you'd expect from a variable that's actually measuring something kink-relevant — not a binary flip, but a smooth gradient.

This is the headline reason to pull Powerlessness out of OCEAN: when you analyze it with the right comparison, it carries signal. When you analyze it as a personality trait, it disappears into the noise alongside Openness and Agreeableness.

![Powerlessness × D/s](figures/powerlessness_ds.png)
_Notebook reference: `Powerlessness × D/s Preference` cell in `1a_CGL_EDA.ipynb`._

### Headline numbers — Powerlessness across the 7 D/s levels

| D/s preference                |     n |  mean | 95 % CI |
|:------------------------------|------:|------:|--------:|
| Totally submissive            | 1,469 | +1.51 |   ±0.19 |
| Moderately submissive         | 2,767 | +1.16 |   ±0.13 |
| Slightly submissive           | 1,763 | +0.85 |   ±0.16 |
| Switch / equal / no pref      | 4,354 | +0.72 |   ±0.10 |
| Slightly dominant             | 1,476 | +0.31 |   ±0.18 |
| Moderately dominant           | 2,261 | +0.09 |   ±0.15 |
| Totally dominant              | 1,005 | −0.12 |   ±0.23 |

The 1.6-point spread across the 7 levels is on a scale that runs roughly −9 to +9 (sum of three Likert items). On that scale, 1.6 points is a real but moderate shift — comfortably bigger than the 0.15 CGL-vs-non-CGL gap, but smaller than the within-group spread (each group's standard deviation is around 3.7 points).

### The numbers in detail — Powerlessness vs CGL flag

This is the analysis that *was* in the OCEAN section and produced the trivial finding. We keep it here for completeness.

| group         |     n |  mean |  std |
|:--------------|------:|------:|-----:|
| CGL+ (True)   | 2,845 | +0.96 | 3.66 |
| CGL− (False)  | 1,295 | +0.81 | 3.69 |
| Unknown       | 11,363 | +0.62 |   —  |

- Gap CGL+ vs CGL− = **+0.15 points** (CGL+ scores marginally higher).
- Cohen's d = **+0.040** — well inside the "trivial" band (|d| < 0.10).
- Kruskal-Wallis omnibus across the 3 groups: H = 22.1, p ≈ 1.6 × 10⁻⁵, **η² = 0.0013** (negligible).

The KW p-value is "highly significant," but that's a sample-size artifact — with n > 15,000 even a 0.15-point gap clears the significance threshold. The η² and Cohen's d both say the practical effect is essentially zero. **Powerlessness does not differentiate CGL from non-CGL respondents.**

### How we measured this

- **Variable.** `powerlessness` — a sum of three Likert items, ranging roughly −9 to +9. Higher = stronger endorsement of feeling powerless / wanting disempowerment.
- **D/s comparison.** Spearman correlation between `powerlessness` (continuous) and `ds_rank` (1–7 ordinal); group means + 95 % CIs at each of the 7 levels.
- **CGL comparison.** Means and Cohen's d across the 3 CGL flag groups; Kruskal-Wallis omnibus; η² for effect size.
- **Why two different comparisons.** Powerlessness was hypothesized to capture kink-relevant attitudes. If it's well-aimed, it should track *what kind of kink someone reports* (D/s preference). It shouldn't necessarily track *whether someone identifies with a specific subculture* (CGL). The data confirms exactly this asymmetry.

### Full stats

- **Powerlessness × `ds_rank`:** Spearman ρ = **−0.137**, p ≈ 0 (essentially zero, n = 15,095). Negative because higher D/s rank = more dominant = lower Powerlessness.
- **Powerlessness × CGL flag:** KW H = **22.1**, p = 1.6 × 10⁻⁵, η² = **0.0013**, Cohen's d (T vs F) = **+0.040**.

### What this means (and doesn't mean)

This finding **upgrades** the original "Big Five doesn't predict CGL" claim rather than overturning it. CGL identification is still orthogonal to broad personality structure. What changes is the framing of Powerlessness specifically: it isn't a personality trait that happened to be flat — it's a kink-relevant self-report that's flat for the *wrong* comparison and informative for the *right* one.

The practical implication: when discussing the BKS survey's psychometrics, treat Powerlessness as **content-aligned with D/s, orthogonal to CGL.** It belongs in analyses about dominance/submission, not analyses about caregiver/little dynamics.

---

# Chapter C — Cross-validation: the two lenses agree

> **At the role-aggregate level, a role's D/s lean and its Powerlessness gap from baseline correlate at Spearman ρ = −0.685 across the 21 roles. Roles whose endorsers tend submissive also report higher-than-average Powerlessness; roles whose endorsers tend dominant report lower-than-average. The same group of users tells the same story across both scales.**

### The 30-second version

Chapter A measured each role's D/s tilt (lean score). Chapter B measured each role's Powerlessness tilt (gap from the overall mean). These come from two different parts of the survey, asked in two different ways. If they're both measuring *something real about the kind of user that endorses each role*, they should agree.

They do. Sort the 21 roles by D/s lean and the same ordering — almost — pops out for Powerlessness. The Spearman correlation across roles is **ρ = −0.685**, a strong negative relationship. (Negative because sub-leaning roles have *negative* lean and *positive* Powerlessness gap.)

This isn't a tautology — Chapter A used the categorical D/s preference, Chapter B used the standalone Powerlessness scale, and the two have only a moderate ρ = −0.137 at the individual level. The aggregation to role level pulls signal out of noise.

### Headline numbers — the agreement, role by role

Roles where sub-leaning users gravitate (D/s lean negative, Powerlessness gap positive):

| role          |   n   | D/s lean | Power gap |
|:--------------|------:|---------:|----------:|
| Priests       |   593 |   −0.31  |   +0.61  |
| Catboys       |   551 |   −0.29  |   +0.43  |
| Criminals     | 1,581 |   −0.25  |   +0.35  |
| Gigolos       |   177 |   −0.04  |   +0.30  |
| Gynecologists |   752 |   −0.41  |   +0.05  |

Roles where dom-leaning users gravitate (D/s lean positive, Powerlessness gap negative):

| role                |     n | D/s lean | Power gap |
|:--------------------|------:|---------:|----------:|
| Cheerleaders        | 2,966 |   +0.43  |   −0.28  |
| Nurses              | 3,247 |   +0.35  |   −0.23  |
| Babysitter          | 2,889 |   +0.27  |   −0.23  |
| Maids               | 3,691 |   +0.25  |   −0.18  |
| Escorts/prostitutes | 1,999 |   +0.32  |   −0.29  |

The one notable mismatch: **Gynecologists** show the strongest sub-lean (−0.41) but only a small positive Powerlessness gap (+0.05). Worth a closer look — possibly the role attracts a sub-leaning *but-not-disempowerment-seeking* subset of users.

### Full stats

Spearman correlation between role-level D/s lean and Powerlessness gap, across the 21 roles meeting the n ≥ 30 cutoff: **ρ = −0.685**, p ≈ 5.9 × 10⁻⁴, n = 21 roles.

For comparison, the same correlation at the individual-respondent level (Powerlessness vs ds_rank, Chapter B) is ρ = −0.137. The role-aggregate ρ is much larger because aggregation suppresses individual-level noise — it's measuring "what kind of user does this role attract on average," which is a tighter signal than "what does any one user score."

### What this means (and doesn't mean)

This is a sanity check, not a new finding. It says: **the two scales are measuring overlapping content, and that content has a coherent role-level signature.** Roles aren't sorting users on Powerlessness for some unrelated reason — they're sorting users on a D/s-aligned dimension that Powerlessness happens to capture.

This also explains why Powerlessness × CGL was flat (Chapter B): Powerlessness loads onto D/s identity, and CGL is only weakly aligned with D/s (per main findings doc, Chapter 2: ~6-point shift in submissive %, η² = 0.0013). A variable that tracks D/s won't track CGL with much intensity, because CGL itself doesn't track D/s with much intensity.

---

## Cross-doc note — relationship to `1a_CGL_EDA_Findings.md`

| Existing chapter                                  | What this supplement adds                                                                                       |
|:--------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|
| Ch. 1 — "No CGL personality type"                 | Refines: the Big Five was the right question and got the right (null) answer. Powerlessness was bundled in but should have been analyzed separately. When it is, it **does** carry signal — just on D/s, not CGL. |
| Ch. 2 — "What CGL looks like as a power dynamic"  | Extends the role-level analysis. Ch. 2 reports role-by-CGL gaps; this supplement reports role-by-D/s lean. The two are complementary: Ch. 2 says CGL+ users endorse more roles in general; this supplement says role choice has an internal D/s structure regardless of CGL. |
| Ch. 5 — "Are CGL fans 'kinkier' overall?"         | Strengthens the "broader fantasy palate" finding. Roles aren't all equivalent; they have D/s tilts. CGL+ users endorse more of *all* of them, but those roles internally divide into sub-attractor and dom-attractor flavors. |

---

## Limitations

- **Self-reported D/s preference.** All inferences in Chapters A and C rest on the `ds_preference` field. If the field is mismeasured (acquiescence bias, social desirability), the lean ranking inherits that error.
- **Role wording ambiguity.** "Endorsing a role" doesn't distinguish between *being* the role and *being with* the role. The dom-leaning cluster of feminine archetypes (Cheerleaders, Geishas, Nuns) is striking but the data can't tell us *which* mode of engagement is driving the tilt.
- **Excluded roles.** `role_Nazis` was dropped at notebook load time. Roles with n < 30 in the Powerlessness analysis (none, in practice — Gigolos at n = 177 was the smallest) would have been excluded for stability.
- **Aggregation effects.** The role-level ρ of −0.685 is much larger than the individual-level ρ of −0.137. This is real, but it tells you about role *populations*, not about predicting any individual respondent's Powerlessness from their D/s preference (where the effect is small).

---

## Appendix — methods reference

- **Lean score:** `mean(ds_rank | role) − 4`, where `ds_rank` is the 1–7 ordinal D/s scale and 4 is "Switch/equal/no preference."
- **Powerlessness gap:** `mean(powerlessness | role) − mean(powerlessness | full sample)`. Baseline `+0.70` for n = 15,095.
- **Spearman ρ at the individual level:** computed on every respondent who answered both `powerlessness` and `ds_preference`, n = 15,095.
- **Spearman ρ at the role level:** computed across the 21 role-aggregate values (one per role), n = 21.
- **Cohen's d:** `(mean_T − mean_F) / pooled_sd`. Conventional bands: |d| < 0.10 trivial, 0.10–0.20 very small, 0.20–0.50 small, 0.50+ medium-to-large.
- **η² for Kruskal-Wallis:** `(H − k + 1) / (n − k)`, where k = number of groups. Conventional bands: <0.01 negligible, <0.06 small, <0.14 medium, ≥0.14 large.
- **Significance shorthand:** `*` p<0.05, `**` p<0.01, `***` p<0.001. With this n, the markers are nearly always present; magnitude (effect size) is the more informative number.
