# Lexiem

**Mapping beginner sound descriptors to IEM frequency response from review text.**

Pronounced "LEK-see-em" (*lexeme* + *IEM*).

Newcomers to in-ear monitors (IEMs) are told an IEM is "warm", "bright" or "muddy", but nothing validated links those words to the measurement graph. Lexiem is an open, reproducible pipeline that connects the two:

1. collect public IEM frequency-response measurements and review text,
2. have an LLM extract sound descriptors from each review into a structured list,
3. reduce each measurement to a small set of band features,
4. model which descriptors co-occur with which features (word → typical graph shape, graph → descriptor probabilities),
5. compare the model against rule-based heuristics such as "more bass = warm",
6. check the mapping against a small listening study with beginner listeners.

> Status: early scaffold. The stages below are stubs; sample sizes (`[N]`) are not final. This README describes the intended workflow and will be updated as each stage lands.

Paper: *Lexiem: Mapping Beginner Sound Descriptors to IEM Frequency Response from Review Text* (Sawit Koseeyaumporn), prepared for AES Europe 2027. See [`paper/`](paper/).

---

## What is and isn't in this repo

| Published here | Not published |
|---|---|
| Collection and extraction code | Scraped review text (site terms and copyright) |
| Source URLs / IDs (`data/sources/`) | Raw measurement files (re-fetched by `make collect`) |
| Exact LLM prompts, model name/version, settings | API keys |
| Cached raw LLM outputs (`data/cache/llm/`) | Listener personal data |
| Derived data: descriptors and measurement features (`data/processed/`) | |
| Listening-study protocol, stimuli recipes, anonymized responses | |

LLM outputs can change between model versions, so the cache is what lets you reproduce the reported numbers without re-calling the API. The extraction prompt asks for descriptors only, never quotes, so cached outputs should not contain review text. Check this before publishing a new cache.

Before running `collect`, check each source site's terms of use. Keep only extracted words and measurement numbers in anything you redistribute.

---

## Quick start

```bash
git clone https://github.com/<user>/lexiem.git
cd lexiem
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .

# Reproduce reported numbers from the committed cache and derived data (no API key, no scraping):
make reproduce

# Run the whole pipeline from scratch (scrapes sources, calls the LLM):
cp .env.example .env      # add your API key
make all
```

Python 3.11+ is expected. `requirements.txt` pins exact versions.

## Pipeline

Each stage reads the previous stage's output and writes to a fixed location. Run all with `make all` or one at a time with `python -m lexiem <stage>`.

| # | Stage | Command | Reads | Writes |
|---|---|---|---|---|
| 1 | Collect | `make collect` | `data/sources/iem_index.csv` | `data/raw/measurements/`, `data/raw/reviews/` |
| 2 | Extract | `make extract` | `data/raw/reviews/`, `prompts/`, `configs/llm.yaml` | `data/cache/llm/`, `data/interim/descriptors_raw.jsonl` |
| 3 | Normalize | `make normalize` | `data/interim/descriptors_raw.jsonl` | `data/processed/descriptors.csv`, `data/processed/descriptor_groups.csv` |
| 4 | Features | `make features` | `data/raw/measurements/`, `configs/features.yaml` | `data/processed/features.csv` |
| 5 | Model | `make model` | `data/processed/` | `results/models/`, `results/tables/` |
| 6 | Evaluate | `make evaluate` | model outputs, `listening_study/responses/` | `results/tables/`, `results/figures/` |

### 1. Collect
Fetches the measurement for each IEM listed in `data/sources/iem_index.csv` and the matching review text. Records the measurement rig/source, since descriptors may depend on it.

### 2. Extract
An LLM turns each review into a structured per-IEM list of sound descriptors. The prompt is versioned in `prompts/`; the model, version and sampling settings live in `configs/llm.yaml`. Every response is cached by a hash of (prompt version, model, settings, input), so reruns are free and deterministic.

### 3. Normalize
Lowercases, lemmatizes and merges synonyms (e.g. "muddy" / "muddied"), then groups descriptors. The grouping is stored explicitly so it can be inspected and changed.

### 4. Features
Reduces each frequency response to a small feature set over bass, upper-midrange and treble bands, following recent preferred-target research on in-ear headphones. Band edges and any normalization are set in `configs/features.yaml`. The edges there are placeholders until confirmed against the cited work.

### 5. Model
- Descriptor/feature co-occurrence analysis.
- A model predicting descriptor probabilities from features, and its inverse: the typical graph shape behind a word.
- Rule-based baselines ("more bass = warm" and similar) in `src/lexiem/model/heuristics.py`.

### 6. Evaluate
Compares model predictions with listening-study choices. Reports which descriptors map consistently to measurable features and which are ambiguous or depend on rig or listener.

## Listening study

Beginner listeners hear one IEM equalized in several ways and pick the version that best matches a given descriptor. The protocol, EQ recipes and anonymized responses are in [`listening_study/`](listening_study/). Participant sample size: `[N]`.

## Repository layout

```
lexiem/
├── README.md
├── LICENSE
├── CITATION.cff
├── pyproject.toml
├── requirements.txt          # pinned environment
├── Makefile                  # one-command pipeline: make all / make reproduce
├── .env.example              # API key placeholder, never commit .env
├── .gitignore
│
├── configs/
│   ├── pipeline.yaml         # paths and stage settings
│   ├── llm.yaml              # model name/version, temperature, seed, retries
│   └── features.yaml         # band edges, smoothing, normalization
│
├── prompts/
│   └── extract_descriptors_v1.md   # exact extraction prompt, versioned
│
├── data/
│   ├── sources/
│   │   └── iem_index.csv     # IEM IDs and source URLs (committed)
│   ├── raw/                  # gitignored: re-created by `make collect`
│   │   ├── measurements/
│   │   └── reviews/
│   ├── cache/
│   │   └── llm/              # raw LLM responses keyed by hash (committed)
│   ├── interim/              # gitignored: intermediate files
│   └── processed/            # committed derived data
│       ├── descriptors.csv
│       ├── descriptor_groups.csv
│       └── features.csv
│
├── src/lexiem/
│   ├── __init__.py
│   ├── __main__.py           # python -m lexiem <stage>
│   ├── cli.py
│   ├── config.py
│   ├── collect/              # measurement + review fetchers
│   ├── extract/              # LLM client, caching, output schema
│   ├── normalize/            # descriptor cleaning and grouping
│   ├── features/             # frequency-response -> band features
│   ├── model/                # co-occurrence, predictor, inverse, heuristics
│   └── evaluate/             # metrics and listening-study comparison
│
├── listening_study/
│   ├── PROTOCOL.md
│   ├── eq_recipes.yaml       # EQ variants applied to the test IEM
│   ├── stimuli/              # gitignored audio, recipes are enough to rebuild
│   └── responses/            # anonymized choices only
│
├── scripts/                  # one-off helpers (figures, checks)
├── tests/
├── results/
│   ├── figures/
│   └── tables/
├── paper/                    # abstract and manuscript source
└── docs/
    ├── data_sources.md       # sources, terms-of-use notes, access dates
    └── reproducibility.md    # what is cached, how to regenerate it
```

## Reproducibility checklist

- [x] Environment pinned (`requirements.txt`)
- [x] One command runs the pipeline (`make all`) and one reproduces results from cache (`make reproduce`)
- [x] Prompts, model name/version and settings recorded
- [x] Raw LLM outputs cached
- [x] Scraped review text excluded from the repo
- [ ] Zenodo DOI for the tagged release (add to `CITATION.cff` once minted)
- [ ] Final search for prior work (AES E-Library, Google Scholar) before the paper claims novelty

## Citing

See [`CITATION.cff`](CITATION.cff). A Zenodo DOI will be added for the tagged release that matches the paper.

## License

Code: MIT, see [`LICENSE`](LICENSE). Derived data in `data/processed/` and `listening_study/responses/`: license to be decided (CC BY 4.0 is a common choice). Source measurements and reviews remain the property of their original authors.
