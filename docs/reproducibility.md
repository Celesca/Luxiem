# Reproducibility

- `make reproduce` rebuilds all reported numbers from `data/cache/llm/` and `data/processed/`. It needs no API key and does no scraping.
- `make all` reruns everything. Scraped sources may have changed, and LLM outputs can differ across model versions; compare against the committed cache.
- Cache key: hash of (prompt file contents, model, settings, input text hash).
- Before committing a new cache, confirm it contains descriptors only and no review text.
