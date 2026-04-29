# BKS Survey — OCEAN Variables

Reference for the five Big Five (OCEAN) `*variable` columns in `reddit/database/BKSPublic.csv`. Companion to [survey_review.ipynb](survey_review.ipynb).

## Big Five (OCEAN) personality variables

The five `*variable` columns (`opennessvariable`, `consciensiousnessvariable`, `extroversionvariable`, `neuroticismvariable`, `agreeablenessvariable`) each score on a **−6 to +6 scale**. **Positive = more of the trait, negative = less.** ±6 is the strongest possible endorsement either way; ±3 is the practical threshold for "this person clearly skews toward / away from the trait"; **0 means the items cancelled out** — could be a neutral respondent or a pure acquiescer (see below).

Each is computed as `positive_item − negative_item`, where both items are 7-point Likert (−3 to +3). Pairing oppositely-worded items controls for **acquiescence bias** (the tendency to agree with any statement regardless of content) — a respondent who agrees to both items lands near 0, leaving the score informative only for those who genuinely endorse the positive framing more than the negative. (Column names misspell "conscientiousness" as `consciensiousness` — preserve that when querying.) All five are 0% null — usable against any subset without denominator gymnastics.

| Variable | High score means | Positive item | Subtracted item |
|---|---|---|---|
| `opennessvariable` | More open | "I have excellent ideas" | "I have difficulty understanding abstract ideas" |
| `consciensiousnessvariable` | More conscientious | "I like order" | "I shirk my duties" |
| `extroversionvariable` | More extroverted | "I am the life of the party" | "I am quiet around strangers" |
| `neuroticismvariable` | More neurotic | "I worry about things" | "I am relaxed most of the time" |
| `agreeablenessvariable` | More agreeable | "I sympathize with others' feelings" | "I feel little concern for others" |

## Score interpretation by value

Use this table to read any single value you see in the data.

| Score | Interpretation |
|------:|---|
| +6 | Maximum: positive item totally agreed AND negative totally disagreed |
| +5 | Very strong endorsement of trait |
| +4 | Strong endorsement |
| +3 | Clear endorsement |
| +2 | Mild lean toward trait |
| +1 | Slight lean toward trait |
|  0 | **Ambiguous** — items cancelled (neutral, balanced, or pure acquiescence) |
| −1 | Slight lean against trait |
| −2 | Mild lean against trait |
| −3 | Clear disendorsement |
| −4 | Strong disendorsement |
| −5 | Very strong disendorsement |
| −6 | Maximum: positive item totally disagreed AND negative totally agreed |

**On this dataset** most scores cluster between −3 and +4 (extroversion shifted left, agreeableness shifted right), so values of ±5 or ±6 are distinctive.
