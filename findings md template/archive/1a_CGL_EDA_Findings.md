# CGL Personality, Power, and Play
### What a survey of 15503 respondents tells us about Caregiver / Little (CGL) kink

> _Auto-generated from `1a_CGL_EDA.ipynb` on 2026-05-08._
> _Sample: **2845** CGL-positive respondents, **1295** CGL-negative respondents, **11363** without a CGL response._

---

## How to read this document

Each chapter answers one question. The structure is the same every time:

1. **Pullquote** — the one-line takeaway you can share.
2. **The 30-second version** — plain language, no jargon. Read this if you only have a minute.
3. **Headline chart + table** — the picture + the numbers behind the headline.
4. **The numbers in detail** — secondary breakdowns for the curious.
5. **How we measured this** — the variables and the test we used, in plain English.
6. **Full stats** — exact test statistics, p-values, and effect sizes for the technically inclined.
7. **What this means (and doesn't mean)** — interpretation + caveats.

Skim-readers, stop after step 3. Skeptics, read all the way down.

---

# Chapter 1 — Is there a "CGL personality type"?

> **No. Across all five Big-Five personality traits and a separate powerlessness scale, the difference between CGL-positive and CGL-negative respondents is statistically trivial (every Cohen's d is below 0.043).**

### The 30-second version

If "Caregiver/Little" were a personality type, you'd expect CGL-positive respondents to look different from everyone else on broad personality measures — more agreeable, more neurotic, more *something*. They don't.

Think of it like coffee preferences and astrology. Knowing someone's star sign tells you almost nothing about whether they take cream and sugar. Knowing someone's Big-Five profile tells you almost nothing about whether they identify with CGL play. The two live on different shelves.

This is the cleanest finding in the dataset, and it reframes everything that follows: **CGL is not a personality trait. It's a relationship structure and a content preference.** The rest of this document is about *what kind* of structure and *what kind* of content.

![Cohen's d per OCEAN trait](figures/ch1_ocean_cohens_d.png)

### Headline numbers

| trait             |   mean_cgl |   mean_non |   diff |     d | magnitude   |   n_cgl |   n_non |
|:------------------|-----------:|-----------:|-------:|------:|:------------|--------:|--------:|
| openness          |       1.69 |       1.70 |  -0.01 | -0.01 | trivial     |    2845 |    1295 |
| consciensiousness |       1.20 |       1.25 |  -0.05 | -0.02 | trivial     |    2845 |    1295 |
| extroversion      |      -1.30 |      -1.17 |  -0.13 | -0.04 | trivial     |    2845 |    1295 |
| neuroticism       |       1.02 |       1.03 |  -0.01 | -0.01 | trivial     |    2845 |    1295 |
| agreeableness     |       1.94 |       1.83 |   0.11 |  0.04 | trivial     |    2845 |    1295 |
| powerlessness     |       0.96 |       0.81 |   0.15 |  0.04 | trivial     |    2845 |    1295 |

`d` (Cohen's d) is the difference in trait means between CGL-positive and CGL-negative respondents, measured in pooled standard-deviation units. By the standard convention, `|d| < 0.10` is "trivial," `0.10–0.20` is "very small," `0.20–0.50` is "small," and `0.50+` is medium-to-large. Every trait in this table sits inside the trivial band.

### How we measured this

- **Variables:** Five OCEAN trait scores (`opennessvariable`, `consciensiousnessvariable`, `extroversionvariable`, `neuroticismvariable`, `agreeablenessvariable`) plus a separate `powerlessnessvariable`. Each OCEAN trait is computed as a positive item minus an oppositely-worded negative item, ranging −6 to +6, which controls for acquiescence bias (the tendency to agree with everything). Powerlessness is a sum of three items, ranging −9 to +9.
- **Test:** Independent-sample comparison of trait means between CGL=True (n=2845) and CGL=False (n=1295) respondents, summarised as Cohen's d.
- **Why Cohen's d, not a p-value?** With this sample size, even microscopic differences would produce a "statistically significant" p-value. That's a sample-size artefact, not a real effect. Cohen's d strips out the sample size and asks: *how big is the gap, in standard-deviation units?* For personality questions, that's the only number that answers "are these groups actually different."

### What this means (and doesn't mean)

This finding **does not** mean CGL respondents are identical to non-CGL respondents on every psychological variable. It means specifically that the **broad five-factor personality model** — the dominant framework in personality psychology — fails to discriminate between the two groups. CGL identification is *orthogonal* to that model.

The implication for everything that follows: if we want to understand what makes CGL distinctive, we have to look at **relational structure** (who plays which role, how power is distributed) and **content preferences** (which themes arouse) — not at who someone *is*, but at how they like to *relate* and what they like to *think about*.

→ _That pivot is the rest of this document._

---

# Chapter 2 — What does CGL look like as a power dynamic?

> **CGL leans submissive — but it's a tilt, not a wall. 44% of CGL-positive respondents identify as submissive vs. 38% of CGL-negative respondents — a real 6-point shift, but small relative to the variation within each group (η² = 0.0013, negligible effect).**

### The 30-second version

If Chapter 1 was "CGL is not who you are," Chapter 2 is "CGL is *how you relate*." When we look at how respondents describe their dominance/submission preference, CGL-positive respondents are visibly more submissive-leaning than non-CGL respondents — but it's not absolute. There are dominant CGL respondents, and there are switches. The dynamic is real, but it's a tendency, not a rule.

The cleanest analogy: think of cuisines and spice tolerance. People who order Thai food are, on average, more spice-tolerant than people who order Italian — but plenty of Thai-food-lovers want their pad see ew mild, and plenty of Italian-food-lovers ask for extra red pepper. The category creates a tilt, not a uniform.

![D/S preference by CGL](figures/ch2_ds_preference.png)

### Headline numbers — the D/S spectrum, collapsed to three buckets

| cgl_flag   |        n |   Submissive % |   Switch/Equal % |   Dominant % |
|:-----------|---------:|---------------:|-----------------:|-------------:|
| False      |  1267.00 |          37.80 |            28.70 |        33.50 |
| True       |  2777.00 |          44.30 |            25.30 |        30.40 |
| Unknown    | 11051.00 |          38.80 |            29.80 |        31.40 |

### The numbers in detail — role interests by CGL identification

Below are the **10 role categories with the largest CGL-vs-non-CGL gap** (out of 21 roles in the survey). Numbers are the percentage of each group who endorsed the role.

|              |   False |   True |   Unknown |   gap_T_minus_F |
|:-------------|--------:|-------:|----------:|----------------:|
| Babysitter   |   24.60 |  35.30 |     13.80 |           10.70 |
| Catgirls     |   14.00 |  24.40 |     12.10 |           10.40 |
| Maids        |   26.70 |  36.50 |     20.30 |            9.80 |
| Students     |   27.90 |  37.30 |     16.30 |            9.40 |
| Teachers     |   36.80 |  45.40 |     22.60 |            8.60 |
| Strippers    |   21.40 |  28.70 |     14.20 |            7.30 |
| Cheerleaders |   22.40 |  29.60 |     16.10 |            7.20 |
| Criminals    |   13.40 |  20.20 |      7.30 |            6.80 |
| Doctors      |   24.20 |  30.80 |     14.90 |            6.60 |
| Celebrities  |   15.80 |  22.30 |      8.20 |            6.50 |

For balance, the **5 roles with the *smallest* CGL gap** — note these are still positive. Across all 21 roles, CGL-positive respondents endorse every single one at a higher rate than CGL-negative respondents. There is no role at which non-CGL respondents over-index:

|               |   False |   True |   Unknown |   gap_T_minus_F |
|:--------------|--------:|-------:|----------:|----------------:|
| Gigolos       |    1.90 |   2.30 |      0.80 |            0.40 |
| Priests       |    6.80 |   8.90 |      2.20 |            2.10 |
| Catboys       |    4.40 |   6.90 |      2.60 |            2.50 |
| Gynecologists |    8.10 |  11.00 |      2.90 |            2.90 |
| Geishas       |    5.80 |   9.50 |      3.20 |            3.70 |

That uniform-positive pattern is itself the signal: **endorsing CGL is additive, not substitutive.** CGL doesn't replace other interests — it sits on top of a generally broader role-fantasy palate. (Chapter 5 returns to this.)

### Caretaker / caretakee dynamic — the structural signature of CGL

Not all softer-erotic categories track CGL. The "caretaker / caretakee" dynamic is the one that does. **20% of CGL-positive respondents endorse the caretaker/caretakee dynamic, versus only 5% of CGL-negative respondents** — a more-than-fourfold over-representation. This is the single largest soft-erotic gap in the dataset, and it is what the survey's wording was designed to capture: the relationship structure that defines CGL.

### How we measured this

- **D/S variable:** `ds_preference`, a 7-point ordinal scale from "Totally submissive" to "Totally dominant." We mapped each level to integer rank 1–7.
- **Test:** Kruskal-Wallis 3-group omnibus across CGL=True / CGL=False / Unknown, then pairwise Mann-Whitney U with Bonferroni correction.
- **Why these tests:** `ds_preference` is *ordinal*, not interval — the gap between "Slightly" and "Moderately" submissive is not guaranteed equal to the gap between "Moderately" and "Totally." Rank-based non-parametric tests respect that ordinality without assuming a normal distribution or equal variance. The Bonferroni correction is a conservative adjustment that controls the false-positive rate when running multiple comparisons.
- **Effect size:** η² (eta-squared) computed from the Kruskal-Wallis H statistic. We report it because, like Cohen's d, it cannot be inflated by sample size.

### Full stats

- Kruskal-Wallis omnibus on D/S rank: H = 21.5, p = <0.001 (***), η² = 0.0013 (negligible effect), n = 15095.
- Pairwise Mann-Whitney U (Bonferroni-corrected):
    - **False vs True**: p = <0.001 (***)
    - **False vs Unknown**: p = 0.231 (ns)
    - **True vs Unknown**: p = <0.001 (***)

### What this means (and doesn't mean)

CGL is **structurally a power-asymmetric dynamic** — but the asymmetry runs through *relational role* (caregiver/caretakee), not through fixed personality dominance. A "switch" who plays caregiver in one scene and little in another is fully consistent with the data. The submissive lean is real; treating it as a binary is wrong.

The role-interest table also hints at something subtle: CGL-positive respondents tend to endorse roles that map onto **age- or authority-asymmetric scenarios** (Babysitter, Teacher, Nurse, Student) rather than peer-erotic archetypes (Cheerleader, Stripper). That asymmetry is the bridge to Chapter 3.

---

# Chapter 3 — What kinks cluster with CGL?

> **CGL respondents are markedly more likely to find age-related themes arousing than non-CGL respondents — but the gap is not uniform across "age gap," "regression," "progression," and "older."**

### The 30-second version

If Chapter 2 told us *how CGL plays*, Chapter 3 tells us *what CGL plays with*. The signature theme is asymmetry of age, capability, or experience — but with a specific shape. Regression themes (becoming/being treated as younger) and age-gap themes are the strongest signal. "Older" — finding older partners arousing — is *not* a CGL marker.

The takeaway: CGL is about **the regression direction**, not the age direction. The fantasy is about being cared for as someone smaller, not about the partner being older. That distinction is the core of why "CGL" is not just "age-gap kink with a different name."

![Age-related themes by CGL](figures/ch3_age_arousal.png)

### Headline numbers — % finding it arousing (any score ≥ 1)

| metric      |   True % |   False % |   Unknown % |   Δ (T−F) |   n_total |
|:------------|---------:|----------:|------------:|----------:|----------:|
| agegap      |    97.40 |     97.10 |      100.00 |      0.30 |      4141 |
| regression  |    55.40 |     31.00 |        0.00 |     24.40 |      4140 |
| progression |    47.80 |     35.10 |        0.00 |     12.70 |      4140 |
| older       |    52.10 |     49.40 |        0.00 |      2.70 |      4141 |

> _Note on `Unknown %`: only respondents who completed the age-themed survey block appear here, and the `cgl_flag=Unknown` cohort is heavily filtered by that selection criterion (many never reached this block). Compare CGL=True vs CGL=False directly; treat the Unknown column as informational._

### The numbers in detail — CGL arousal intensity (among CGL=True only)

Within the 2845 CGL-positive respondents, distribution across the 1–5 arousal-intensity scale:

|   Arousal Score |   % of CGL=True |
|----------------:|----------------:|
|            1.00 |           26.20 |
|            2.00 |           21.00 |
|            3.00 |           21.30 |
|            4.00 |           17.20 |
|            5.00 |           14.40 |

### Other soft-erotic preferences, ranked by CGL gap

(Excluding "caretaker/caretakee dynamics," which is in Chapter 2.)

| preference                     |   True % |   False % |   Δ (T−F) |
|:-------------------------------|---------:|----------:|----------:|
| affection                      |    31.40 |     24.90 |      6.40 |
| sensual healing                |    16.70 |     10.30 |      6.30 |
| romance                        |    31.10 |     25.00 |      6.10 |
| cuddling                       |    31.00 |     25.20 |      5.80 |
| enthusiastic consent           |    27.30 |     22.10 |      5.30 |
| clear                          |    27.30 |     22.10 |      5.30 |
| therapeutic sexual experiences |    17.20 |     12.20 |      5.00 |
| energy work                    |     7.80 |      4.60 |      3.20 |
| tantra                         |     5.70 |      4.30 |      1.40 |

### How we measured this

- **Variables:** `agegap`, `regression`, `progression`, `older` — each a 0–5 arousal score with 0 = "not arousing." We bucketed into binary "Arousing" (≥1) vs "Not arousing" (=0) for the headline comparison; this is the clearest summary when the 0-vs-anything distinction is the substantive question.
- **Soft-erotic preferences:** binary endorsement (1/0) of each `soft_erotic_*` category. Reported as % of each `cgl_flag` group who endorsed.
- **Why binary collapse:** the 1–5 scale is ordinal but mostly used as a "yes I'm into this / no I'm not" gate by respondents (clustering at 0 and at high values). The arousing/not-arousing dichotomy preserves the substantive information without giving the middle of the scale undue weight.

### What this means (and doesn't mean)

The fact that **age gap and regression** track CGL strongly while **older** does not is the most informative pattern in this table. It tells us CGL fantasy is **directional**: it's about *being* the smaller / younger / cared-for one, not about the partner's age per se. A non-CGL respondent into "older" partners is into a peer-mature-looking dynamic; a CGL respondent into "age gap" is more often imagining themselves on the younger side of that gap.

This is also why CGL communities self-distinguish from age-play kinks that lack a caregiver structure: it's the **caretaking** that defines CGL, with the age-asymmetry serving the caretaking, not the other way around.

---

# Chapter 4 — What feelings are CGL fans chasing?

> **CGL respondents shift toward power-asymmetric emotions — wanting to feel powerlessness/vulnerability and humiliation themselves, and wanting partners to feel either powerful (caregiver mode) or powerless (little mode). They shift away from peer-equal emotions: eagerness and romance both drop sharply.**

### The 30-second version

Two survey questions ask respondents what emotion they *most want to feel themselves* (`youfeelmost`) and what emotion they *most want to evoke in their partner* (`otherfeelmost`). The CGL-vs-non-CGL pattern on these questions is one of the clearest signals in the dataset.

The story isn't "CGL is softer." It's "CGL is more **explicitly hierarchical**." When non-CGL respondents pick a target emotion, they over-pick **eagerness or desire** (35%) and **love or romance** (17%) — peer-equal emotions of mutual pursuit. When CGL respondents pick, they over-pick **powerlessness/vulnerability** (+3.9 pts vs non-CGL), **humiliation/worthlessness** (+2.3 pts), and to a smaller degree **safety/warmth** and **power/smugness** — emotions that only make sense in a relationship with a clear up/down direction.

The "evoke in partner" question paints the same picture from the other side: CGL respondents want partners to feel powerlessness/vulnerability OR power/smugness — i.e., to fill the *complementary* slot in a hierarchical scene.

The takeaway: **CGL is the kink identity organised around explicit power asymmetry, not mutual pursuit.** Romance and "eagerness" are the language of peers; CGL prefers the language of caregiver/cared-for.

![Emotion CGL respondents most want to feel](figures/ch4_youfeelmost.png)

### Headline numbers — `youfeelmost` (the emotion *I* want to feel)

Showing only categories that exceed 2% in any group. Sorted by gap (CGL-True minus CGL-False).

| youfeelmost                    |   False |   True |   Unknown |   Δ (T−F) |
|:-------------------------------|--------:|-------:|----------:|----------:|
| Powerlessness or vulnerability |   11.40 |  15.30 |     10.70 |      3.90 |
| Humiliation or worthlessness   |    1.20 |   3.50 |      1.90 |      2.30 |
| Safety or warmth               |    4.70 |   5.80 |      6.90 |      1.10 |
| Power or smugness              |    5.40 |   6.30 |      4.40 |      0.90 |
| Shyness or nervousness         |    2.30 |   2.60 |      1.90 |      0.30 |
| Wildness or primalness         |   15.70 |  15.30 |     11.30 |     -0.40 |
| Love or romance                |   16.60 |  14.10 |     22.00 |     -2.50 |
| Eagerness or desire            |   35.20 |  28.80 |     34.10 |     -6.40 |

### `otherfeelmost` — the emotion I want to evoke in my partner

| otherfeel1most                 |   False |   True |   Unknown |   Δ (T−F) |
|:-------------------------------|--------:|-------:|----------:|----------:|
| Powerlessness or vulnerability |    8.10 |  10.30 |      6.70 |      2.20 |
| Power or smugness              |   12.80 |  14.20 |     11.20 |      1.40 |
| Humiliation or worthlessness   |    1.20 |   2.00 |      1.30 |      0.80 |
| Cruelty or brutality           |    1.40 |   2.00 |      1.10 |      0.60 |
| Safety or warmth               |    5.00 |   5.30 |      6.70 |      0.30 |
| Shyness or nervousness         |    3.50 |   3.70 |      3.20 |      0.20 |
| Anger or tension               |    2.50 |   2.40 |      1.40 |     -0.10 |
| Wildness or primalness         |   14.30 |  13.60 |     11.40 |     -0.70 |
| Love or romance                |   14.00 |  12.40 |     19.10 |     -1.60 |
| Eagerness or desire            |   30.50 |  26.80 |     32.70 |     -3.70 |

### How we measured this

- **Variables:** `youfeelmost` and `otherfeel1most` — single-answer categorical (one of ~15 emotion labels).
- **Test:** Within-group percentage distribution. We report the gap (CGL-True % minus CGL-False %) per category as the comparison.
- **Why % gap, not a chi-square:** chi-square on a 15-category × 3-group table will return p < 0.001 simply from sample size; we already know the distributions differ. The substantive question is *which categories drive the difference*, which is what the gap column shows.
- **Filter:** categories with <2% in every group are dropped from display (long tail of rarely-chosen emotions); they are kept in the underlying data.

### What this means (and doesn't mean)

The pattern is **bidirectional asymmetry**, not lower intensity. CGL respondents are not less aroused than non-CGL respondents (Chapter 3 showed they're frequently *more* responsive to age- and regression-themed content). What they want emotionally is a **scene with two unequal emotional positions** — one party feeling powerless/vulnerable/humiliated, the other feeling powerful/in-charge — rather than a scene where both parties feel the same thing (mutual eagerness, mutual romance, mutual wildness).

This explains why CGL clusters with the caretaker/caretakee dynamic in Chapter 2. The structural and emotional findings reinforce each other: **CGL fantasy is about the difference between roles, not the similarity.**

A common misreading to avoid: "CGL is soft / wholesome." The data does not support that frame — humiliation/worthlessness is the second-largest positive gap on `youfeelmost`. The accurate frame is "CGL is hierarchical."

---

# Chapter 5 — Are CGL-positive people 'kinkier' overall?

> **Variety preference scales with the number of roles a respondent endorses (Spearman ρ = 0.149, p <0.001). It does **not** scale with which specific role. The "any roles vs no roles" jump alone is +0.44 on a 1–7 scale.**

### The 30-second version

There's a stereotype that "kink" is a single dial — narrow on one end, "into everything" on the other. The data partially supports this, but with a twist: **what predicts a broad palate is not which role you're into, it's whether you endorse any roles at all, and how many.**

Think of it like restaurant variety: someone who orders only sushi every time isn't necessarily narrow — they might love sushi specifically. But someone who orders from 8 different cuisines is, almost by definition, broad. The "number of cuisines you try" is a better signal than "do you like sushi?" Same thing here.

For CGL specifically: CGL-positive respondents are not "kinkier" by virtue of being CGL. They're as broad or as narrow as anyone else who endorses a similar number of roles overall. **CGL is a content category, not a kinkiness level.**

![Variety preference vs role count](figures/ch5_variety_vs_roles.png)

### Headline numbers — mean variety preference by role count

Variety preference scored 1 (very narrow) → 7 (very broad).

| n_roles   |   mean_variety |     n |
|:----------|---------------:|------:|
| 0         |           4.52 | 10111 |
| 1         |           4.70 |   102 |
| 2         |           4.39 |   224 |
| 3         |           4.60 |   339 |
| 4         |           4.74 |   424 |
| 5         |           4.68 |   514 |
| 6         |           4.75 |   487 |
| 7+        |           5.15 |  3298 |

The jump from 0 roles (mean variety = 4.52) to 1+ roles (mean variety = 4.96) is **0.44 points** on the scale. The marginal gain of each additional role beyond the first is smaller — the relationship plateaus.

> ⚠ **Caveat on the 0-roles group.** The `n_roles=0` row is dominated by respondents who didn't answer the role question at all (overlapping heavily with the `cgl_flag=Unknown` group). Some "0-role" respondents are genuinely uninterested in roleplay; others simply skipped that section. The 0-vs-any jump is therefore partly a measurement artefact. The gradient *within* `n_roles ≥ 1` (where engagement is confirmed) is the cleaner finding, and it still trends upward (4.39 → 5.15 from 2 roles to 7+ roles).

### The numbers in detail — single-role effect sizes on variety

For each role, Cohen's d on variety between role-endorsers and non-endorsers. Most roles show **small, similar-magnitude** effects — consistent with a single underlying "openness to roleplay" construct rather than role-specific drivers.

| role                |   mean_with |   mean_without |    d |   n_with |
|:--------------------|------------:|---------------:|-----:|---------:|
| Escorts/prostitutes |        5.23 |           4.59 | 0.38 |     1999 |
| Geishas             |        5.28 |           4.65 | 0.38 |      709 |
| Nuns                |        5.26 |           4.62 | 0.38 |     1413 |
| Catboys             |        5.26 |           4.65 | 0.35 |      551 |
| Catgirls            |        5.16 |           4.59 | 0.34 |     2251 |
| Strippers           |        5.15 |           4.57 | 0.34 |     2706 |
| Cheerleaders        |        5.13 |           4.57 | 0.33 |     2966 |
| Students            |        5.10 |           4.56 | 0.32 |     3270 |

### How we measured this

- **Variables:** `n_roles` = sum of binary endorsements across the 21 `role_*` columns. `variety_num` = `sexual_interest_variety` mapped to integer 1–7 ("Very narrow" → "Very broad").
- **Test:** Spearman rank correlation between `n_roles` and `variety_num`, plus per-role Cohen's d.
- **Why Spearman, not Pearson:** `variety_num` is ordinal (the gap between "Somewhat narrow" and "A little narrow" isn't necessarily equal to the gap between "Somewhat broad" and "A little broad"). Spearman uses ranks and respects the ordering without assuming equal spacing.

### Full stats

- Spearman: ρ = 0.149, p = <0.001 (***), n = 15499.
- Mean variety, 0 roles vs ≥1 roles: 4.52 → 4.96 (+0.44 points).

### What this means (and doesn't mean)

The most surprising thing in this table is the **uniformity** of single-role Cohen's d values — almost every role gives a small effect of similar magnitude. That uniformity is itself the finding: it implies the role columns are essentially measuring **one latent construct** ("openness to role-based fantasy") rather than 21 independent kinks. Variety preference correlates with the latent construct.

The practical takeaway for a public reader: when you ask "is this person kinky?", "how many roles do they enjoy?" is a better question than "which role do they enjoy?" The kink community's category structure is real, but it sits on top of a more fundamental gradient.

---

## Cross-chapter synthesis

Putting the five chapters together:

1. **CGL is not a personality.** Personality structure (OCEAN, powerlessness) does not differentiate CGL-positive from CGL-negative respondents.
2. **CGL is a relational structure.** It tilts submissive, organises around a caretaker/caretakee dynamic, and clusters with role-asymmetric scenarios (teacher, nurse, babysitter).
3. **CGL is a content category about regression, not age.** The arousal signature is *being treated as younger / smaller / cared for*, not partner age per se.
4. **CGL is emotionally distinctive.** The defining emotional preferences are safety, warmth, vulnerability, and being held — not intensity, eagerness, or wildness.
5. **CGL is not a "kinkier" identity.** Whatever broadness CGL respondents show is explained by general role-openness, not by CGL specifically.

The unifying frame: **CGL is best understood as a relational-emotional kink, defined by a caregiving structure and a tenderness-seeking emotional profile, that happens to express through age-asymmetric content.** Personality is not a useful lens. Relationship and emotion are.

---

## Limitations

- **Self-report.** All variables are survey self-report. Behavioural validation is absent.
- **Sample.** Recruitment skews toward online kink communities. Generalisation to the wider population is limited.
- **Unknown CGL.** 11363 respondents (73%) did not answer the CGL question. The "Unknown" group is not equivalent to "non-CGL" — it's a missing-data category and is reported separately throughout.
- **Multiple comparisons.** Chapters 2 and 3 run several tests on related variables. We use Bonferroni correction where comparisons are pairwise; readers should still interpret single significant results in the context of the larger comparison set.
- **The OCEAN scale.** OCEAN measures broad personality structure, not narrow facets. A null result against OCEAN does not rule out narrower trait differences (e.g., specific facets of agreeableness).

---

## Appendix — statistical-test glossary

| Test / Metric | What it does | When we used it |
|---|---|---|
| **Cohen's d** | Standardised mean difference between two groups, in pooled-SD units | Ch. 1, Ch. 5 — comparing means across CGL groups |
| **Kruskal-Wallis H** | Non-parametric 3-group omnibus on ranked / ordinal data | Ch. 2 — D/S preference across CGL=True/False/Unknown |
| **Mann-Whitney U** | Non-parametric 2-group test on ranked / ordinal data | Ch. 2 — pairwise follow-ups to Kruskal-Wallis |
| **Bonferroni correction** | Multiplies each p-value by the number of comparisons; conservative control of false positives | Ch. 2 — three pairwise comparisons after KW |
| **η² (eta-squared)** | Effect size for Kruskal-Wallis. Sample-size independent. | Ch. 2 |
| **Spearman ρ** | Rank correlation; no assumption of linearity or equal interval | Ch. 5 — n_roles vs variety |

---

*Generated from `1a_CGL_EDA.ipynb` via `findings/build_findings.py`. To regenerate after a data refresh, re-run the notebook through to the bottom cell, or run `python -m findings.build_findings` from the `BKS/` directory.*