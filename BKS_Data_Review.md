# BKS - Schema & Data Review
[references](https://docs.google.com/document/d/1B3Itxfko-DzyzQlF4_Qc73aSTrcPyLpaySRRyD7-EY0/edit?tab=t.0)

## Arousal Scale
| Scale | Represents |
|---:|---|
| 0 | Not arousing |
| 1 | Slightly arousing |
| 2 | Somewhat arousing |
| 3 | Moderately arousing |
| 4 | Very arousing |
| 5 | Extremely arousing |

## Agreement scale

Used by both OCEAN personality items and powerlessness items below.

| Response | Score |
|---|---:|
| Totally agree | +3 |
| Agree | +2 |
| Somewhat agree | +1 |
| Neither agree nor disagree | 0 |
| Somewhat disagree | −1 |
| Disagree | −2 |
| Totally disagree | −3 |

# Field Inventory & Exports

Single source of truth for every column written to [BKS_sfw_preferences.csv](../database/BKS_sfw_preferences.csv), [BKS_nsfw_preferences.csv](../database/BKS_nsfw_preferences.csv), and [cgl_BKS_data.csv](../database/cgl_BKS_data.csv) by the `Export` section of [1_EDA.ipynb](1_EDA.ipynb). For OCEAN/Powerlessness scale interpretation and survey-item wording, see the methodology sections above — not repeated here.

## Grouping glossary

Groupings describe **what kind of information the field captures**, not what answer type it uses. Many groupings span multiple answer types — e.g. *preferences* contains both single-pick Likerts (`ds_preference`) and exploded multi-select dummies (`bodyweight_*`).

| Grouping | What it captures |
|---|---|
| **Identifier** | Stable join key linking sub-dataframes back to `bks_df` |
| **Demographic** | Who the respondent is — age, sex, orientation, politics, body class, clinical self-description |
| **Personality** | Dispositional traits (Big Five OCEAN) and worldview (powerlessness). See [OCEAN Variables](#ocean-variables) and [Powerlessness](#powerlessness-perceived-agency) for computation |
| **Sexual** | Lifestyle / behavioral facts about the respondent's own sexuality — partner count, porn habits, self-rated breadth of interests |
| **Preferences** | Broad, mainstream things the respondent finds erotic — D/s self-id, vanilla act ratings, body type/weight, emotional states in scenarios, top-level kink categories |
| **Kink specific** | Specific kink interests with named labels — bondage tiers, voyeur/exhibition, worship dynamics, CGL age cluster, uncommon kink categories |

**"Exported to" column:** `SFW` = `BKS_sfw_preferences.csv` only. `NSFW` = `BKS_nsfw_preferences.csv` only. `Both` = attached to both via `attach_keys()`. `CGL` = also written to `cgl_BKS_data.csv` (a sub-slice for CGL-domain correlations, *not* its own grouping).

**Note on gating:** many kink Likerts (rows below marked `0..5 (n<15503)`) are *gated questions* — only shown to respondents who indicated some interest in that cluster. Non-gated respondents are `NaN`.

## Master inventory

| Grouping | Field | Answer type | Value / Range | Example | Exported to |
|---|---|---|---|---|---|
| Identifier | `respondent_id` | Integer key | 0..15502 | `0` | Both, CGL |
| Demographic | `age` | Categorical bucket | `14-17`, `18-20`, `21-24`, `25-28`, `29-32`, `33+` | `25-28` | Both, CGL |
| Demographic | `biomale` | Binary | 0.0 (female), 1.0 (male) | `1.0` | Both |
| Demographic | `straightness` | Categorical | `Straight`, `Not straight` | `Straight` | Both |
| Demographic | `politics` | Categorical | `Liberal`, `Moderate`, `Conservative` | `Liberal` | Both |
| Demographic | `bmi` | Categorical | `Not overweight`, `Overweight+` | `Not overweight` | (proposed) |
| Demographic | `diagnosis` | Categorical (string) | `Anxiety`, `ADHD`, `Social anxiety`, … | `Anxiety` | Both, CGL |
| Personality | `openness` | Differenced agreement scale | −6..+6 | `4` | Both |
| Personality | `consciensiousness` | Differenced agreement scale | −6..+6 | `-1` | Both |
| Personality | `extroversion` | Differenced agreement scale | −6..+6 | `-2` | Both |
| Personality | `neuroticism` | Differenced agreement scale | −6..+6 | `3` | Both |
| Personality | `agreeableness` | Differenced agreement scale | −6..+6 | `6` | Both |
| Personality | `powerlessness` | Summed agreement scale | −9..+9 | `2` | Both |
| Sexual | `sexcount` | Ordinal bucket | `0`, `1-2`, `3-7`, `8-15`, `16+` | `1-2` | Both |
| Sexual | `pornhabit` | Frequency scale | 0..7 | `5.0` | Both |
| Sexual | `sexual_interest_variety` | Ordered categorical | `Somewhat narrow` … `Extremely broad` | `Somewhat broad` | Both, CGL |
| Preferences | `ds_preference` | Ordered categorical | `Strongly submissive` … `Strongly dominant` | `Slightly submissive` | Both, CGL |
| Preferences | `"I am aroused by being dominant in sexual interactions" (6w3xquw)` | Agreement scale | −3..+3 | `1.0` | Both |
| Preferences | `"I am aroused by being submissive in sexual interactions" (xem7hbu)` | Agreement scale | −3..+3 | `2.0` | Both |
| Preferences | `normalsex` | Agreement-scale composite | signed (down to −8) | `-8.0` | Both |
| Preferences | `cunnilingus` | Agreement-scale composite | signed (down to −8) | `-5.0` | Both |
| Preferences | `eagerness` | Arousal scale | 0..5 (n=11759) | `4.0` | Both |
| Preferences | `teasing` | Arousal scale | 0..5 (n=11633) | `5.0` | Both |
| Preferences | `frustration` | Arousal scale | 0..5 (n=11633) | `3.0` | Both |
| Preferences | `gentleness` | Arousal scale | 0..5 (n=8837) | `3.0` | Both |
| Preferences | `multiplepartners` | Arousal scale | 0..5 (n=6264) | `3.0` | Both |
| Preferences | `powerdynamic` | Arousal scale | 0..5 (n=8799) | `4.0` | Both |
| Preferences | `toys` | Arousal scale | 0..5 (n=8408) | `4.0` | Both |
| Preferences | `clothing` | Arousal scale | 0..5 (n=8258) | `1.0` | Both |
| Preferences | `roles` | Arousal scale | 0..5 (n=6739) | `4.0` | Both, CGL |
| Preferences | `bodyweight_*` (6 cols) | Binary dummies | 0/1 | `bodyweight_average = 1` | SFW |
| Preferences | `bodytype_*` (6 cols) | Binary dummies | 0/1 | `bodytype_very tall people = 1` | SFW |
| Preferences | `feel_self_*` (22 cols) | Binary dummies | 0/1 | `feel_self_love or romance = 1` | SFW |
| Preferences | `feel_other_*` (22 cols) | Binary dummies | 0/1 | `feel_other_eagerness or desire = 1` | SFW |
| Preferences | `youfeelmost` | Top-pick string | one of the `feel_*` options | `Love or romance` | Both, CGL |
| Preferences | `otherfeel1most` | Top-pick string | one of the `feel_*` options | `Love or romance` | Both, CGL |
| Preferences | `pos_*` (8 cols) | Binary dummies | 0/1 | `pos_cowgirl = 1` | NSFW |
| Preferences | `act_*` (20 cols) | Binary dummies | 0/1 | `act_anal fingering = 1` | NSFW |
| Preferences | `bodypart_*` (29 cols) | Binary dummies | 0/1 | `bodypart_hair (head) = 1` | SFW |
| Preferences | `bodymod_*` (11 cols) | Binary dummies | 0/1 | `bodymod_tattoos (light) = 1` | SFW |
| Preferences | `common_*` (16 cols) | Binary dummies | 0/1 | `common_eagerness = 1` | Both (SFW + NSFW) |
| Preferences | `soft_erotic_*` (9 cols) | Binary dummies | 0/1 | `soft_erotic_cuddling = 1` | SFW, CGL |
| Preferences | `role_*` (22 cols) | Binary dummies | 0/1 | `role_teachers = 1` | SFW, CGL |
| Kink specific | `cgl` | Arousal scale | 0..5 (n=4140) | `5.0` | Both, CGL |
| Kink specific | `obedience` | Arousal scale | 0..5 (n=8743) | `3.0` | Both |
| Kink specific | `mindbreak` | Arousal scale | 0..5 (n=8743) | `2.0` | Both |
| Kink specific | `masterslave` | Arousal scale | 0..5 (n=8743) | `3.0` | Both |
| Kink specific | `fulltimepower` | Arousal scale | 0..5 (n=8743) | `1.0` | Both |
| Kink specific | `humiliation` | Arousal scale | 0..5 (n=3548) | `5.0` | Both |
| Kink specific | `lightbondage` | Arousal scale | 0..5 (n=8702) | `4.0` | Both |
| Kink specific | `mediumbondage` | Arousal scale | 0..5 (n=8701) | `5.0` | Both |
| Kink specific | `extremebondage` | Arousal scale | 0..5 (n=8701) | `1.0` | Both |
| Kink specific | `worshipping` | Arousal scale | 0..5 (n=11633) | `3.0` | Both |
| Kink specific | `worshipped` | Arousal scale | 0..5 (n=11633) | `2.0` | Both |
| Kink specific | `voyeurself` | Arousal scale | 0..5 (n=6723) | `4.0` | Both |
| Kink specific | `voyeurother` | Arousal scale | 0..5 (n=6723) | `2.0` | Both |
| Kink specific | `exhibitionself` | Arousal scale | 0..5 (n=6723) | `3.0` | Both |
| Kink specific | `exhibitionother` | Arousal scale | 0..5 (n=6723) | `1.0` | Both |
| Kink specific | `regression` | Arousal scale (CGL-gated) | 0..5 (n=4140) | `1.0` | Both, CGL |
| Kink specific | `progression` | Arousal scale (CGL-gated) | 0..5 (n=4140) | `3.0` | Both, CGL |
| Kink specific | `agegap` | Arousal scale (CGL-gated) | 0..5 (n=4141) | `5.0` | Both, CGL |
| Kink specific | `older` | Arousal scale (CGL-gated) | 0..5 (n=4141) | `3.0` | Both, CGL |
| Kink specific | `uncommon_*` (13 cols) | Binary dummies | 0/1 | `uncommon_genderplay = 1` | NSFW |
| Kink specific | `nonstandard_age_tag` | Derived binary | 0.0 / 1.0 / NaN | `1.0` if `Age: nonstandard` was checked in uncommon, NaN if uncommon left blank | NSFW, CGL |

### Source survey questions for multi-select prefixes

| Prefix | Survey question (verbatim) |
|---|---|
| `bodyweight_` | Which of the following body weights do you find most erotic? (1jq57nf) |
| `bodytype_` | Which of the following body types do you find significantly erotic? |
| `feel_self_` | Check all that apply: Scenarios you find erotic tend to involve *you* feeling |
| `feel_other_` | Check all that apply: Scenarios you find erotic tend to involve *the other person/people/creatures* feeling |
| `pos_` | Which of the following sexual positions do you find significantly erotic? |
| `act_` | Which of the following sex acts do you find significantly erotic? |
| `bodypart_` | Select all body parts you find significantly erotic |
| `bodymod_` | Which of the following body modifications do you find significantly erotic? |
| `common_` | Common things: Check all the following categories that contain a thing that arouses you. |
| `uncommon_` | Uncommon things: Check all the following categories that contain a thing that arouses you. |
| `role_` | Which of the following roles are erotic? |
| `soft_erotic_` | Which of the following do you find erotic? (vqogs86) |

### Final export shapes

| File | Rows | Columns | Composition |
|---|---:|---:|---|
| `BKS_sfw_preferences.csv` | 15503 | 193 | 143 multi-select dummies + 50 `attach_cols` |
| `BKS_nsfw_preferences.csv` | 15503 | 108 | 57 multi-select dummies + `nonstandard_age_tag` + 50 `attach_cols` |
| `cgl_BKS_data.csv` | 15503 | 52 | curated sub-slice for CGL analysis — every field is also in SFW or NSFW (note: `role_*` and `soft_erotic_*` columns in CGL use a legacy naive-comma-split and differ slightly in naming from the cleaned SFW/NSFW versions) |

**Set comparison between SFW and NSFW:**

| Bucket | Count | Contents |
|---|---:|---|
| Common (shared) | 66 | 50 `attach_cols` + 16 `common_*` dummies |
| SFW only | 127 | `bodyweight_*` (6) + `bodytype_*` (6) + `feel_self_*` (22) + `feel_other_*` (22) + `soft_erotic_*` (9) + `bodypart_*` (29) + `bodymod_*` (11) + `role_*` (22) |
| NSFW only | 42 | `pos_*` (8) + `act_*` (20) + `uncommon_*` (13) + `nonstandard_age_tag` (1) |

---

# Column Reference — Before / After

Reverse-lookup tables for the column-name changes applied in the `Export` section of [1_EDA.ipynb](1_EDA.ipynb). Use this when analyzing the CSVs: a column like `common_eagerness` doesn't carry its full meaning in its name — this table shows what the original survey label said (including the illustrative examples that were stripped) so you can interpret what the respondent was actually checking off.

The transformation code lives in the notebook; this section just documents *what changed*.

## Simple renames

Three BKSPublic columns get short, code-friendly names.

| Original (in BKSPublic.csv) | Renamed to |
|---|---|
| `Which describes you best? (cvc5b81)` | `ds_preference` |
| `Which of the following is the most severe for you? (trspees)` | `diagnosis` |
| `Your sexual interests feel (44qhm16)` | `sexual_interest_variety` |

## OCEAN suffix removal

The six personality columns have their `variable` suffix stripped and are cast to `int`.

| Original | Renamed to |
|---|---|
| `opennessvariable` | `openness` |
| `consciensiousnessvariable` | `consciensiousness` |
| `extroversionvariable` | `extroversion` |
| `neuroticismvariable` | `neuroticism` |
| `agreeablenessvariable` | `agreeableness` |
| `powerlessnessvariable` | `powerlessness` |

## Multi-select label shortenings

The `common_*` and `uncommon_*` survey questions presented categories with illustrative parenthetical examples (e.g. `Eagerness (begging, worshipping, teasing, etc.)`). At export, the parenthetical is stripped to keep the column name compact — but the parenthetical is what tells you *what's in the bucket*. The tables below preserve the original wording so you can look up what each column was capturing.

### `common_*` (16 cols) — "Common things: Check all the following categories that contain a thing that arouses you."

| Column in CSV | Original survey label |
|---|---|
| `common_eagerness` | Eagerness (begging, worshipping, teasing, etc.) |
| `common_appearance states: static` | Appearance states: static (tattoos, bodymods, skinniness, etc.) |
| `common_gentleness` | Gentleness (caretaking, healing, tantra, etc.) |
| `common_power dynamics & d/s` | Power dynamics & D/s (obedience, findom, petplay, choking, etc.) |
| `common_bondage` | Bondage (gags, shibari, handcuffs, etc.) |
| `common_toys` | Toys (anal beads, pussy pumps, showerheads, etc.) |
| `common_clothing` | Clothing (latex, shoes, too-small, miniskirts, cameltoe, etc.) |
| `common_body parts: normal, non-genital` | Body parts: normal, non-genital (elbows, knees, armpits, head hair, etc.) |
| `common_roles` | Roles (secretary, asians, catgirls, teachers, stoners, etc.) |
| `common_exhibitionism/voyeurism` | Exhibitionism/voyeurism (peeping tom, flashing, public sex, etc.) |
| `common_multiple partners` | Multiple partners (hotwifing, gangbangs, freeuse, threesomes, etc.) |
| `common_nonconsent` | Nonconsent (rapeplay, body control, kidnapping, etc.) |
| `common_sadomasochism` | Sadomasochism (spanking, needle play, clamps, torture, etc.) |
| `common_mythical/fictional creatures` | Mythical/fictional creatures (dragons, vampires, aliens, MLP, etc.) |
| `common_humiliation` | Humiliation (defilement, impotence, cuckoldry, ridicule, etc.) |
| `common_sensory` | Sensory (electricity, vacuums, ASMR, tickling, etc.) |

### `uncommon_*` (13 cols) — "Uncommon things: Check all the following categories that contain a thing that arouses you."

| Column in CSV | Original survey label |
|---|---|
| `uncommon_age: nonstandard` | Age: nonstandard (age gaps, ageplay, unusual ages, etc.) |
| `uncommon_objects: nonstandard` | Objects: nonstandard (hairbrushes, rope, cars, etc.) |
| `uncommon_bodily secretions` | Bodily secretions (farts, squirt, urine, blood, etc.) |
| `uncommon_reproduction` | Reproduction (pregnancy, surrogacy, oviposition, etc.) |
| `uncommon_mental alteration` | Mental Alteration (hypnotism/mind control, amnesia, cocaine, etc.) |
| `uncommon_genderplay` | Genderplay (sissification, futa, crossdressing, etc.) |
| `uncommon_abnormal bodies and body parts` | Abnormal bodies and body parts (massive bellies, tails/horns, giants, etc.) |
| `uncommon_transformations` | Transformations (growth/shrinking, bodyswapping, furries, etc.) |
| `uncommon_bestiality/creatures` | Bestiality/creatures (dogs, horses, dolphins, insects, squid, etc.) |
| `uncommon_brutal/violent` | Brutal/violent (gore, mutilation, amputations, drowning, etc.) |
| `uncommon_creepy/horror` | Creepy/horror (zombies, necrophilia, live insertions, etc.) |
| `uncommon_vore` | Vore (consuming/being consumed, usually whole) |
| `uncommon_dirtiness/disgust/messiness` | Dirtiness/disgust/messiness (cakesitting, STDs, soiling, etc.) |

## Multi-select prefixes with self-explanatory labels

These prefixes also come from exploded multi-selects, but the underlying labels are short and unambiguous — no shortening was needed. The column name is the label.

| Prefix | Survey question | Label style |
|---|---|---|
| `bodyweight_` | Which of the following body weights do you find most erotic? | flat words (e.g. `bodyweight_average`, `bodyweight_skinny`) |
| `bodytype_` | Which of the following body types do you find significantly erotic? | flat phrases (e.g. `bodytype_very tall people`) |
| `feel_self_` | Check all that apply: Scenarios you find erotic tend to involve *you* feeling | `X or Y` pairs (e.g. `feel_self_love or romance`) |
| `feel_other_` | Check all that apply: Scenarios you find erotic tend to involve *the other person/people/creatures* feeling | same as `feel_self_` |
| `pos_` | Which of the following sexual positions do you find significantly erotic? | flat (e.g. `pos_cowgirl`) |
| `act_` | Which of the following sex acts do you find significantly erotic? | flat (e.g. `act_anal fingering`) |
| `bodypart_` | Select all body parts you find significantly erotic | flat; two disambiguators kept — `bodypart_hair (head)` vs `bodypart_hair (pubic)` |
| `bodymod_` | Which of the following body modifications do you find significantly erotic? | flat; two disambiguators kept — `bodymod_tattoos (light)` vs `bodymod_tattoos (heavy)` |
| `role_` | Which of the following roles are erotic? | flat (e.g. `role_teachers`, `role_strippers`) |
| `soft_erotic_` | Which of the following do you find erotic? (vqogs86) | flat (e.g. `soft_erotic_cuddling`, `soft_erotic_clear, enthusiastic consent`) |
## Filtered-out categories (intentionally dropped)

Two filters remove columns at export time. If you're wondering why a category you'd expect isn't in the CSV, it's likely one of these.

| Filter | Trigger | Effect |
|---|---|---|
| **EXCLUDE** | column name contains any of: `incest`, `parent`, `sibling`, `grandparent`, `aunt`, `uncle`, `niece`, `nephew`, `cousin`, `13-17`, `0-14`, `ageplay` | dropped to keep the export free of under-age / familial themes. Affects `common_incest` (15.6% raw endorsement) and some incest sub-pairings. **Note:** `uncommon_age: nonstandard` is *kept* because its name no longer contains `ageplay` after parenthetical stripping — but the derived `nonstandard_age_tag` provides the same signal with proper NaN handling. |
| **FRENCH_DROP** | label contains ` ou `, or matches `jouets`, `vêtements`, `rôles`, `non-consentement`, `partenaires multiples`, `pièces de carrosserie`, `bestialité`, `menottes` | dropped because a small fraction of respondents got a French-translated survey; their French category labels appear as 0%-rate duplicate columns. The English equivalents capture all the signal. |
## OCEAN Variables
Reference for the five Big Five (OCEAN) `*variable` columns in `reddit/database/BKSPublic.csv`. Companion to [survey_review.ipynb](survey_review.ipynb).

### Big Five (OCEAN) personality variables

The five OCEAN `*variable` columns (`opennessvariable`, `consciensiousnessvariable`, `extroversionvariable`, `neuroticismvariable`, `agreeablenessvariable`) are computed as **differences between opposing items**, each scoring on a **−6 to +6 scale**.

### Score Computation & Interpretation

#### Computation

Each OCEAN variable is `positive_item − negative_item`. Both items are scored −3 to +3 from the agreement scale above.

- Positive difference (> 0) = stronger agreement with positive framing than negative → person endorses the trait
- Zero difference (= 0) = respondent balanced the items (could be genuinely neutral, or pure acquiescer who agrees with both)
- Negative difference (< 0) = stronger agreement with negative framing than positive → person lacks the trait

Pairing oppositely-worded items controls for **acquiescence bias** (the tendency to agree with any statement regardless of content). A pure acquiescer who agrees with both items lands near 0, making the scale informative only for those who genuinely differentiate between the positive and negative framings.

| Variable | Formula | Range |
|---|---|---|
| `opennessvariable` | openness2 − openness | −6 to +6 |
| `consciensiousnessvariable` | consciensiousness2 − consciensiousness | −6 to +6 |
| `extroversionvariable` | extroversion2 − extroversion | −6 to +6 |
| `neuroticismvariable` | neuroticism2 − neuroticism | −6 to +6 |
| `agreeablenessvariable` | agreeableness2 − agreeableness | −6 to +6 |

#### Interpretation

Use this table to read any single value you see in the data.

| Score | Interpretation | Trait endorsement? |
|------:|---|---|
| +6 | Maximum: positive item totally agreed AND negative totally disagreed | **Yes** |
| +5 | Very strong endorsement of trait | **Yes** |
| +4 | Strong endorsement | **Yes** |
| +3 | Clear endorsement | **Yes** |
| +2 | Mild lean toward trait | **Yes** |
| +1 | Slight lean toward trait | **Yes** |
|  0 | **Ambiguous** — items cancelled out | **No** (cannot determine) |
| −1 | Slight lean away from trait | **No** |
| −2 | Mild lean away from trait | **No** |
| −3 | Clear disendorsement | **No** |
| −4 | Strong disendorsement | **No** |
| −5 | Very strong disendorsement | **No** |
| −6 | Maximum: positive item totally disagreed AND negative totally agreed | **No** |

**On this dataset** most scores cluster between −3 and +4 (extroversion shifted left, agreeableness shifted right), so values of ±5 or ±6 are distinctive.

### Survey items used in OCEAN

Source: https://docs.google.com/document/d/1B3Itxfko-DzyzQlF4_Qc73aSTrcPyLpaySRRyD7-EY0/edit?tab=t.0

##### Openness
- **Positive** (openness2): "I have excellent ideas"
- **Negative** (openness): "I have difficulty understanding abstract ideas"

##### Conscientiousness
- **Positive** (consciensiousness2): "I like order"
- **Negative** (consciensiousness): "I shirk my duties"

##### Extroversion
- **Positive** (extroversion2): "I am the life of the party"
- **Negative** (extroversion): "I am quiet around strangers"

##### Neuroticism
- **Positive** (neuroticism2): "I worry about things"
- **Negative** (neuroticism): "I am relaxed most of the time"

##### Agreeableness
- **Positive** (agreeableness2): "I sympathize with others' feelings"
- **Negative** (agreeableness): "I feel little concern for others"

## Powerlessness (Perceived Agency)

`powerlessnessvariable` is **conceptually distinct from OCEAN** and should not be read as a sixth personality trait. It captures a **worldview / perceived locus of control** — how the respondent interprets their position relative to others — rather than a dispositional behaviour pattern. Closer in spirit to established constructs like Rotter's external locus of control, Seligman's learned helplessness, or just-world belief than to the Big Five.

Two methodological consequences follow:

1. **Items are summed, not differenced.** All three items point at the same belief (perceived powerlessness), so they are summed rather than paired into opposing-pole differences. As a result, the variable does **not** control for acquiescence bias the way OCEAN does — pure acquiescers will score high.
2. **Range is −9 to +9.** Three items × ±3 each. Higher = more agreement with the powerlessness frame.

### Computation

| Variable | Formula | Range |
|---|---|---|
| `powerlessnessvariable` | power + power2 + power3 | −9 to +9 |

### Interpretation

| Score | Interpretation |
|------:|---|
| +9 | Maximum: totally agreed with all three items |
| +6 to +8 | Strong powerlessness worldview |
| +3 to +5 | Clear powerlessness lean |
| +1 to +2 | Slight powerlessness lean |
|  0 | Neutral / ambiguous |
| −1 to −2 | Slight agency lean |
| −3 to −5 | Clear agency lean |
| −6 to −8 | Strong sense of agency |
| −9 | Maximum: totally disagreed with all three items |

### Survey items used in Powerlessness

- (power): "I deserve more respect than I get"
- (power2): "I don't have very much power over those around me"
- (power3): "If life is a game, then I'm losing"

## Survey items asked but NOT used in OCEAN/powerlessness
- "I am high powered, driven, successful"
- "I need to feel in control"
---
