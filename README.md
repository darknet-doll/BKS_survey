# BKS — Big Kink Survey Analyses

Exploratory analyses of the **Big Kink Survey** public dataset.

## About the dataset

The Big Kink Survey was created and administered by [Aella](https://aella.substack.com/p/heres-my-big-kink-survey-dataset), collecting responses from ~970,000 participants. Topics span sexual interests and kinks, personality traits (OCEAN model), demographics, political orientation, relationship structures, and psychological characteristics. The survey is still open.

The publicly released dataset is an **anonymized subset** of the original responses. To protect participant privacy, the published data is limited to respondents **aged 18–32 from Western countries** (US, Canada, and Europe), and has been processed with:

- aggressive binning,
- demographic column removal, and
- noise injection.

### What this means for analysis

These privacy measures **attenuate correlations by roughly 15–30%** compared to the original, depending on the variable. Treat the dataset as supporting **directional exploration and pattern discovery, not precise point estimates** — effect sizes here are lower bounds on what exists in the underlying population, and small effects may be washed out entirely.

## Contents
- [BKS Review.md](BKS%20Review.md) — reference for the OCEAN (Big Five) `*variable` columns: scoring, interpretation, and acquiescence-bias notes.
- [1_EDA.ipynb](1_EDA.ipynb) — initial exploratory data analysis.
