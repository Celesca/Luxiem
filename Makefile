PY ?= python -m lexiem

.PHONY: all reproduce collect extract normalize features model evaluate test

# Full run from scratch: scrapes sources and calls the LLM.
all: collect extract normalize features model evaluate

# Reproduce reported numbers from committed cache + derived data. No scraping, no API key.
reproduce:
	$(PY) model --from-processed
	$(PY) evaluate

collect:
	$(PY) collect

extract:
	$(PY) extract

normalize:
	$(PY) normalize

features:
	$(PY) features

model:
	$(PY) model

evaluate:
	$(PY) evaluate

test:
	python -m pytest tests
