# BKS Survey — OCEAN Variables

Reference for the five Big Five (OCEAN) `*variable` columns in `reddit/database/BKSPublic.csv`. Companion to [survey_review.ipynb](survey_review.ipynb).

## Big Five (OCEAN) personality variables

The five OCEAN `*variable` columns (`opennessvariable`, `consciensiousnessvariable`, `extroversionvariable`, `neuroticismvariable`, `agreeablenessvariable`) are computed as **differences between opposing items**, each scoring on a **−6 to +6 scale**. **Scores > 0 indicate endorsement of the trait; scores < 0 indicate disendorsement; 0 indicates ambiguity.** All five are 0% null — usable against any subset without denominator gymnastics. (Column names misspell "conscientiousness" as `consciensiousness` — preserve that when querying.)

## Agreement scale

All personality items use this 7-point agreement scale:

| Response | Score |
|---|---:|
| Totally agree | +3 |
| Agree | +2 |
| Somewhat agree | +1 |
| Neither agree nor disagree | 0 |
| Somewhat disagree | −1 |
| Disagree | −2 |
| Totally disagree | −3 |

## Score Computation & Interpretation

### Computation

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
| `powerlessnessvariable` | power3 + power2 + power | −9 to +9 |

### Interpretation

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

## Survey items used in OCEAN/powerlessness variables

Source: https://docs.google.com/document/d/1B3Itxfko-DzyzQlF4_Qc73aSTrcPyLpaySRRyD7-EY0/edit?tab=t.0

#### Openness
- **Positive** (openness2): "I have excellent ideas"
- **Negative** (openness): "I have difficulty understanding abstract ideas"

#### Conscientiousness
- **Positive** (consciensiousness2): "I like order"
- **Negative** (consciensiousness): "I shirk my duties"

#### Extroversion
- **Positive** (extroversion2): "I am the life of the party"
- **Negative** (extroversion): "I am quiet around strangers"

#### Neuroticism
- **Positive** (neuroticism2): "I worry about things"
- **Negative** (neuroticism): "I am relaxed most of the time"

#### Agreeableness
- **Positive** (agreeableness2): "I sympathize with others' feelings"
- **Negative** (agreeableness): "I feel little concern for others"

#### Powerlessness (computed as sum, not difference)
Unlike OCEAN traits (which subtract negative from positive), powerlessness sums three items:
- (power3): "If life is a game, then I'm losing"
- (power2): "I don't have very much power over those around me"
- (power): "I deserve more respect than I get"

**Interpretation:** Higher agreement = higher powerlessness (range −9 to +9).

### Survey items asked but NOT used in OCEAN/powerlessness
- "I am high powered, driven, successful"
- "I need to feel in control"
- "I've experienced a lot of sexual harassment"
