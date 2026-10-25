# Data sources

One row per source. Record the terms-of-use check before scraping.

| Source | Provides | Terms checked (date) | Notes |
|---|---|---|---|
| squig.link (Super* Review) | measurements | 2026-10-18: robots.txt has only the content-signal template comment, with no `Content-Signal`, `Allow` or `Disallow` directives, so it restricts nothing. No site ToS found. Measurement data licence undocumented. | See "squig.link access" below. |
| TODO | reviews | | |

## squig.link access

squig.link is a static Graphtool site, not the `api.squig.link` server (that returns 404). Found by reading `graphtool.js` and `config.js`; the Chrome extension was not connected, so no live network capture was done.

- **Index:** `GET https://squig.link/data/phone_book.json`, about 300 KB. A list of `{name: brand, phones: [...]}`; 156 entries (including an `_EQ` pseudo-brand) and 611 phones as of 2026-10-18.
- **Phone fields:** `name`, `file`, `reviewScore` (string, `"0"` means none), `reviewLink` (mostly YouTube, 311 set), `price`, `shopLink`, and `suffix` (only when `file` is a list).
- **`file`:** a string (308 phones) or a list of variants (303 phones). Variants are mostly EQ'd or firmware/tip versions, with `suffix` giving the label. Use the first/base entry for the raw measurement, and skip variants whose name contains `EQ`.
- **Curves:** `GET https://squig.link/data/<file> L.txt` and `<file> R.txt`, URL-encoded. REW text export, with `*` comment lines then frequency/SPL rows (about 490 lines). The R channel can be missing (404), as for `Moondrop Aria`, so handle single-channel files.
- **Rig:** the `squig.link` root is `superreview`, whose rig is "clone IEC 711" (`config.js`). Other squiglinks use different rigs and compensation, so do not mix them without normalising.
- **Other squiglinks:** `GET https://squig.link/squigsites.json` lists 124 sites, each with its own `data/` folder. `squigsites.js` lists some as opted out of shop links (not of data).
- **Brand coverage on squig.link:** Moondrop 60, Tin Hifi 26 (the spelling used), KZ 20, ThieAudio 19, Letshuoer 17, Kiwi Ears 13, 7Hz 8, Truthear 8, Simgot 7, Hisenior 5, CCA 4, Tangzu 4.
- **Review text:** squig.link only has links (`reviewLink`) and a score, no review text. Stage 1 still needs a review-text source.
