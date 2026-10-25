<!--
DRAFT. See the marker legend at the top of 01_introduction.md.
This section describes the repo as scaffolded on 2026-10-25 (src/lexiem/* are still stubs; configs/features.yaml,
configs/llm.yaml, prompts/extract_descriptors_v1.md and listening_study/* contain TODOs).
Anything beyond the README, configs and docs/data_sources.md is tagged [PROPOSED].
Update this file whenever a config value is decided or the prompt is frozen.
-->

# 3 Method

## 3.1 Overview

Lexiem is a six-stage pipeline (Table 1). Each stage reads the previous stage's output and writes to a fixed location, so any stage can be rerun or inspected on its own. Prompts, model settings, band definitions and descriptor groupings live in versioned files, not in code.

**Table 1.** Pipeline stages.

| # | Stage | Input | Output |
|---|---|---|---|
| 1 | Collect | IEM index (`data/sources/iem_index.csv`) | raw measurements, raw review text |
| 2 | Extract | review text, prompt, LLM settings | cached LLM responses, raw descriptor list |
| 3 | Normalize | raw descriptor list | cleaned descriptors, descriptor groups |
| 4 | Features | raw measurements, band settings | band features per IEM |
| 5 | Model | descriptors, features | co-occurrence tables, predictors, inverse maps, baselines |
| 6 | Evaluate | model outputs, listening-study responses | tables and figures |

[TODO: Figure 1, a pipeline diagram.]

## 3.2 Measurements

Measurements come from squig.link, the Super\* Review site, a static Graphtool site whose index (`phone_book.json`) listed 611 entries on 2026-10-18 [SquigLink]. Each entry has a base measurement, and some have variants (EQ-processed, firmware or ear-tip versions). We use the base measurement and skip variants whose name contains "EQ". Curves are REW text exports of the left and right channels. Some IEMs have only one channel, in which case we use the one available. [TODO: state how the two channels are combined, e.g. average in dB.]

The site's configuration lists its measurement rig as a clone IEC 711 coupler. Other squig.link-style sites use different rigs and compensation, so we do not mix sources without normalization, and we record the rig for every IEM (`measurement_rig` in `iem_index.csv`) so rig effects can be examined. The final sample contains [N] IEMs that have both a usable measurement and review text. [TODO: list inclusion and exclusion criteria, e.g. minimum review length, one entry per model, exclusion of EQ variants and non-IEM entries.]

## 3.3 Review text

> **[DECISION NEEDED: review text source.]** squig.link provides a review link (mostly YouTube; 311 of 611 entries) and a review score, but no review text [SquigLink]. Stage 1 therefore needs a separate source of review text, and the choice shapes the study. Options include transcripts of the linked videos (these carry speech-recognition errors and need a terms-of-use check), written reviews on other sites, or retailer or forum reviews (different reviewer populations and terms). Record the choice and the terms-of-use check in `docs/data_sources.md`, and replace this box with a description of the source, the number of reviews per IEM, the language filter, and how multiple reviews of one IEM are combined.

Review text is used only to extract descriptors. It is not redistributed (Section 3.8). Reviews are written after sighted listening, so brand, price and hype may influence the vocabulary; this is a limitation (Section 3.9) rather than something the pipeline removes.

## 3.4 Descriptor extraction

An LLM turns each review into a structured list of sound descriptors. The prompt (`prompts/extract_descriptors_v1.md`) asks for descriptors only, as short lowercase words or phrases, with no quoted sentences. It excludes comparisons with other products and asks for the region each descriptor refers to (`bass`, `mids`, `treble`, or `overall`), returned as JSON of the form `{"descriptors": [{"term": ..., "region": ...}]}`. Responses that do not match the schema are retried (up to 3 times) and then logged and excluded [TODO: confirm behaviour once implemented].

Model settings are recorded in `configs/llm.yaml`: provider Anthropic, model [TODO: exact model ID], temperature 0, maximum 1024 output tokens. Every response is cached under a key that hashes the prompt file contents, model, settings and input text, so a rerun returns the stored output. This makes reported numbers reproducible even if the model changes later. The prompt is not yet frozen [TODO: finalize wording and examples, then freeze and describe v1 here; any change creates a new file version].

[PROPOSED: To measure extraction quality, two annotators manually list descriptors for a random sample of [n] reviews, and we report agreement between the LLM and the annotators (precision, recall) and between the annotators.]

## 3.5 Normalization and grouping

Raw descriptors are lowercased and lemmatized, and spelling or inflection variants are merged (for example "muddy" and "muddied"). Descriptors are then grouped into sets of near-synonyms. The grouping is stored explicitly in `data/processed/descriptor_groups.csv`, so each decision can be inspected and changed. Descriptors that appear in fewer than [k] IEMs are dropped from modelling [TODO: choose k]. [PROPOSED: report how the grouping was made, and the agreement between two people grouping the same terms independently.]

## 3.6 Measurement features

Each response is smoothed ([TODO: e.g. 1/3 octave]) and level-matched at [TODO: 1 kHz is the current placeholder in `configs/features.yaml`]. It is then reduced to features for three regions: a bass region, an upper-midrange region around 3 kHz, and a treble region. This mirrors the three adjustable regions in a recent preferred-target study on in-ear headphones, which used a bass shelf, an upper-midrange peak or dip centred at 3 kHz, and a treble shelf [Olive2025]. The band edges in the configuration (bass 20–200 Hz, upper mid 2–5 kHz, treble 5–10 kHz) are placeholders. [TODO: replace them with the values from the cited work (full text needed; only the abstract has been read) and cite it in `configs/features.yaml`.] Each feature is the band's mean level relative to the level-match point, in dB [TODO: decide whether to add band slope, or deviation from a reference curve].

Two cautions apply. First, the cited study set its baseline on a B&K 5128 simulator, whereas our measurements come from a clone IEC 711 coupler, so its preferred offsets (in dB) do not transfer directly. We use the three-region structure, not its numbers. Second, for a reference curve we need one defined for the same rig class [TODO: choose, e.g. the Harman in-ear target, and confirm its compatibility with the rig].

## 3.7 Models and baselines

**Co-occurrence analysis (RQ1).** For each descriptor group and each feature, we estimate the association between having the descriptor and the feature value, with bootstrap confidence intervals [TODO: choose the statistic, e.g. a logistic-regression coefficient or a standardized difference in means]. The extraction step's region tag is used to compare, for example, bass-region descriptors with the bass feature. A descriptor counts as consistent if its cross-validated predictive performance and the interval on its main association pass thresholds fixed in advance [PROPOSED: define the thresholds before running the analysis].

**Forward model (RQ2).** A multi-label model predicts the probability of each descriptor group from the band features. We start with one regularized logistic regression per descriptor, which keeps the model interpretable [TODO: add other model families if justified]. Cross-validation holds out whole brands, since IEMs from one brand often share a tuning, and results report per-descriptor discrimination (for example ROC-AUC) and calibration [PROPOSED].

**Inverse map.** For each descriptor group we compute the typical feature vector and response curve of IEMs described with it, relative to IEMs described without it, with uncertainty bands. This is the "word to graph shape" view for beginners.

**Baselines.**
- *B0, base rate.* Predict each descriptor's overall frequency.
- *B1, rule-based heuristics.* Hand-written rules such as "more bass means warm", taken from community guides [Reddit2013; MobileAudiophile] and implemented in `src/lexiem/model/heuristics.py`.
- *B2, zero-shot LLM* [PROPOSED]. An LLM reads the band features (numbers, with no IEM name or brand to prevent recall of reviews) and outputs a probability for each descriptor in the fixed list. Each IEM is queried [k] times to measure run-to-run agreement. The model and prompt are cached and recorded as in Section 3.4.

## 3.8 Listening check (RQ3)

[N] beginner listeners hear one IEM equalized in several ways and, for each descriptor tested, pick the version that best matches it. Variants are defined in `listening_study/eq_recipes.yaml` [TODO: derive the EQ recipes from the model's predicted shapes and the descriptors chosen, using changes on the scale of those found preference-relevant in [Olive2025], and fix the number of variants k]. We report agreement between the listeners' choices and the model's prediction, compared with chance (1/k), together with the consistency of each listener across repeated trials and the agreement among listeners. The protocol will specify level matching, randomized order, and repeated trials, and will use one fit per listener [PROPOSED: with repeated insertions to estimate fit variability]. [TODO: complete `listening_study/PROTOCOL.md` with participants, recruitment and inclusion criteria, test IEM and music, and ethics approval and consent.] Only anonymized choices are stored.

## 3.9 Reproducibility, data release and limitations

The repository publishes the code, source URLs and IDs, prompts, model name and settings, cached raw LLM outputs, derived data (descriptors and features), the listening-study protocol, EQ recipes and anonymized responses. It does not publish scraped review text, raw measurement files (re-fetched by `make collect`), API keys, or listener personal data. The extraction prompt asks for descriptors rather than quotes, and each new cache is checked for review text before release. `make reproduce` rebuilds all reported numbers from the cache and derived data without an API key or scraping, and `make all` reruns the whole pipeline. The environment is pinned in `requirements.txt`. Terms of use of each source are checked and dated in `docs/data_sources.md`. [TODO: add the Zenodo DOI for the tagged release.]

Known limitations of the design:

- **Sighted reviews.** Reviewers know the brand and price, which can shape the words they use.
- **Review and IEM selection.** Popular IEMs are reviewed more and by more reviewers, and the sample depends on which sites are used.
- **Rig dependence.** Features come from one coupler type, and the word-to-graph map may shift with the rig and with fit.
- **Description is not preference.** A descriptor says nothing about whether an IEM is liked.
- **LLM extraction error.** The extraction can miss or invent descriptors; [PROPOSED: this is measured against human annotation].
- **Small listening sample.** The listening check is a validation, not a population estimate.
- **Language.** The study uses [English] review text only [TODO: confirm].
