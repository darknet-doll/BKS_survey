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
## Abnormal Fetish
** Uncommon things: Check all the following categories that contain a thing that arouses you.**
- **Abnormal bodies and body parts**: (massive bellies, tails/horns, giants, etc.)
- **Age**: nonstandard (age gaps, ageplay, unusual ages, etc.)
- **Bestiality/creatures**: (dogs, horses, dolphins, insects, squid, etc.)
- **Bodily secretions**: (farts, squirt, urine, blood, etc.)
- **Brutal/violent**: (gore, mutilation, amputations, drowning, etc.)
- **Creepy/horror**: (zombies, necrophilia, live insertions, etc.)
- **Dirtiness/disgust/messiness**: (cakesitting, STDs, soiling, etc.)
- **Genderplay**: (sissification, futa, crossdressing, etc.)
- **Mental Alteration**: (hypnotism/mind control, amnesia, cocaine, etc.)
- **Objects**: nonstandard (hairbrushes, rope, cars, etc.)
- **Reproduction**: (pregnancy, surrogacy, oviposition, etc.)
- **Transformations**:(growth/shrinking, bodyswapping, furries, etc.)
- **Vore**: (consuming/being consumed, usually whole)
