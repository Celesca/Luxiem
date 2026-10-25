"""Stage 1: build data/sources/iem_index.csv from squig.link and fetch each IEM's
frequency-response curves, a product image and a rendered FR graph.

Text review collection is still TODO (squig.link only has review links).
"""

import csv
import json
import math
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from lexiem import config

SQUIG_DATA = "https://squig.link/data/"
SQUIG_RIG = "clone IEC 711"
SHOP_INTERVAL = 1.5  # seconds between requests to the same shop host
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130 Safari/537.36 lexiem-research"
)
INDEX_FIELDS = [
    "iem_id", "brand", "model", "price_usd", "price_raw",
    "measurement_url", "measurement_rig", "channels",
    "image_url", "image_path", "graph_path",
    "shop_url", "review_url", "review_score",
]


_host_locks: dict[str, threading.Lock] = {}
_host_last: dict[str, float] = {}
_locks_guard = threading.Lock()


def _throttle(url: str) -> None:
    """Space out requests to shops (not squig.link or image CDNs) per host."""
    host = urllib.parse.urlparse(url).netloc
    if host in ("squig.link", "cdn.shopify.com"):
        return
    with _locks_guard:
        lock = _host_locks.setdefault(host, threading.Lock())
    with lock:
        wait = _host_last.get(host, 0) + SHOP_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _host_last[host] = time.monotonic()


def _get(url: str, retries: int = 4) -> bytes | None:
    """GET with backoff on 429/5xx. Returns None on 404 or persistent failure."""
    for attempt in range(retries):
        _throttle(url)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code not in (429, 500, 502, 503) or attempt == retries - 1:
                return None
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                return None
        time.sleep(5 * 2**attempt)
    return None


def _resolve(url: str) -> str:
    """Follow redirects (amzn.to, s.click.aliexpress.com) to the final URL."""
    _throttle(url)
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.url
    except (urllib.error.URLError, TimeoutError):
        return url


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_price(raw: str) -> float | None:
    m = re.search(r"[\d,]+(?:\.\d+)?", raw or "")
    if not m:
        return None
    value = float(m.group().replace(",", ""))
    return value or None


def base_file(phone: dict) -> str:
    """The raw measurement file: first variant that is not an EQ'd version."""
    files = phone["file"] if isinstance(phone["file"], list) else [phone["file"]]
    for f in files:
        if "EQ" not in f.split():
            return f
    return files[0]


def parse_curve(text: str) -> list[tuple[float, float]]:
    """REW text export: '*' comment lines, then 'freq spl [phase]' rows."""
    points = []
    for line in text.splitlines():
        parts = re.split(r"[\s,;]+", line.strip())
        if len(parts) < 2 or line.startswith("*"):
            continue
        try:
            points.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    return points


def render_graph(curves: dict[str, list[tuple[float, float]]], title: str) -> str:
    """Log-frequency SVG of the L/R curves, 20 Hz to 20 kHz."""
    w, h, ml, mr, mt, mb = 720, 360, 48, 16, 32, 32
    pw, ph = w - ml - mr, h - mt - mb
    pts = [p for c in curves.values() for p in c if 20 <= p[0] <= 20000]
    lo = math.floor(min(s for _, s in pts) / 10) * 10
    hi = math.ceil(max(s for _, s in pts) / 10) * 10

    def x(f: float) -> float:
        return ml + pw * (math.log10(f) - math.log10(20)) / 3

    def y(s: float) -> float:
        return mt + ph * (hi - s) / (hi - lo)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'font-family="sans-serif" font-size="11">',
        f'<rect width="{w}" height="{h}" fill="#fff"/>',
        f'<text x="{ml}" y="20" font-size="13" font-weight="bold">{title}</text>',
    ]
    for f in (20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000):
        label = f"{f // 1000}k" if f >= 1000 else str(f)
        out.append(f'<line x1="{x(f):.1f}" y1="{mt}" x2="{x(f):.1f}" y2="{mt + ph}" stroke="#ddd"/>')
        out.append(f'<text x="{x(f):.1f}" y="{h - 12}" text-anchor="middle" fill="#666">{label}</text>')
    for s in range(lo, hi + 1, 10):
        out.append(f'<line x1="{ml}" y1="{y(s):.1f}" x2="{ml + pw}" y2="{y(s):.1f}" stroke="#ddd"/>')
        out.append(f'<text x="{ml - 6}" y="{y(s) + 4:.1f}" text-anchor="end" fill="#666">{s}</text>')
    styles = {"L": 'stroke="#1f6feb"', "R": 'stroke="#d1242f" stroke-dasharray="5 3"'}
    for ch, curve in curves.items():
        path = " ".join(f"{x(f):.1f},{y(s):.1f}" for f, s in curve if 20 <= f <= 20000)
        out.append(f'<polyline fill="none" stroke-width="1.5" {styles[ch]} points="{path}"/>')
    out.append(f'<text x="{ml + pw}" y="20" text-anchor="end" fill="#666">{" / ".join(curves)} · dB SPL</text>')
    out.append("</svg>")
    return "\n".join(out)


def find_image(shop_url: str) -> str | None:
    """Product image URL from the shop page. Shopify stores expose /products/x.json;
    otherwise fall back to the page's og:image. Amazon and AliExpress mostly block this."""
    if not shop_url:
        return None
    url = _resolve(shop_url)
    parsed = urllib.parse.urlparse(url)
    if "/products/" in parsed.path:
        handle = parsed.path.rstrip("/").split("/products/")[-1]
        body = _get(f"{parsed.scheme}://{parsed.netloc}/products/{handle}.json")
        if body:
            try:
                images = json.loads(body)["product"]["images"]
                if images:
                    return images[0]["src"].split("?")[0]
            except (ValueError, KeyError, TypeError):
                pass
    body = _get(url)
    if body:
        m = re.search(rb'property="og:image"\s+content="([^"]+)"', body) or re.search(
            rb'content="([^"]+)"\s+property="og:image"', body
        )
        if m:
            img = m.group(1).decode("utf-8", "replace").replace("&amp;", "&")
            return "https:" + img if img.startswith("//") else img
    return None


def collect_one(brand: str, phone: dict, paths: dict) -> dict:
    model = phone["name"]
    iem_id = slug(f"{brand} {model}")
    file = base_file(phone)
    row = {
        "iem_id": iem_id,
        "brand": brand,
        "model": model,
        "price_raw": phone.get("price", ""),
        "price_usd": parse_price(phone.get("price", "")) or "",
        "measurement_url": SQUIG_DATA + urllib.parse.quote(f"{file} L.txt"),
        "measurement_rig": SQUIG_RIG,
        "shop_url": phone.get("shopLink", ""),
        "review_url": phone.get("reviewLink", ""),
        "review_score": "" if phone.get("reviewScore") in (None, "", "0") else phone["reviewScore"],
    }

    curves = {}
    for ch in ("L", "R"):
        dest = paths["measurements"] / f"{iem_id}_{ch}.txt"
        if not dest.exists():
            body = _get(SQUIG_DATA + urllib.parse.quote(f"{file} {ch}.txt"))
            if body is None:
                continue
            dest.write_bytes(body)
        curve = parse_curve(dest.read_text(errors="replace"))
        if curve:
            curves[ch] = curve
    row["channels"] = "".join(curves)

    if curves:
        graph = paths["graphs"] / f"{iem_id}.svg"
        graph.write_text(render_graph(curves, f"{brand} {model}"))
        row["graph_path"] = str(graph)

    existing = next(paths["images"].glob(f"{iem_id}.*"), None)
    if existing:
        row["image_path"] = str(existing)
        row["image_url"] = paths["image_urls"].get(iem_id, "")
    else:
        img_url = find_image(row["shop_url"])
        if img_url:
            body = _get(img_url)
            if body:
                ext = Path(urllib.parse.urlparse(img_url).path).suffix.lower() or ".jpg"
                dest = paths["images"] / f"{iem_id}{ext}"
                dest.write_bytes(body)
                row["image_url"] = img_url
                row["image_path"] = str(dest)
    return row


def run(config_path: str, from_processed: bool = False) -> None:
    cfg = config.load(config_path)
    p = cfg["paths"]
    paths = {
        "measurements": Path(p["raw_measurements"]),
        "images": Path(p["raw_images"]),
        "graphs": Path(p["raw_graphs"]),
    }
    for d in paths.values():
        d.mkdir(parents=True, exist_ok=True)

    # Keep image URLs from a previous run so cached images keep their source.
    index_path = Path(p["sources"])
    paths["image_urls"] = {}
    if index_path.exists():
        with open(index_path) as f:
            paths["image_urls"] = {r["iem_id"]: r.get("image_url", "") for r in csv.DictReader(f)}

    phone_book = json.loads(_get(SQUIG_DATA + "phone_book.json"))
    # Skip the _EQ pseudo-brand and averaged curves like "KZ (average)".
    phones = [
        (b["name"], ph)
        for b in phone_book
        if b["name"] != "_EQ"
        for ph in b.get("phones", [])
        if not ph["name"].startswith("(")
    ]
    print(f"collect: {len(phones)} IEMs in squig.link phone book")

    with ThreadPoolExecutor(max_workers=cfg.get("collect", {}).get("workers", 4)) as pool:
        rows = list(pool.map(lambda bp: collect_one(bp[0], bp[1], paths), phones))

    # Brand/model pairs can collide after slugging; keep the first.
    seen, unique = set(), []
    for r in rows:
        if r["iem_id"] not in seen:
            seen.add(r["iem_id"])
            unique.append(r)

    with open(index_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(unique)

    n = len(unique)
    print(
        f"collect: wrote {n} rows to {index_path} | "
        f"price {sum(1 for r in unique if r['price_usd'])}/{n}, "
        f"curves {sum(1 for r in unique if r['channels'])}/{n}, "
        f"images {sum(1 for r in unique if r.get('image_path'))}/{n}"
    )
