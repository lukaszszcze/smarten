"""Put the USA & Canada notebook's photos on the site, with the credit line each licence asks for.

The photos are PHOTOS in tools/usa_canada/usa_canada_art.py: key -> Wikimedia Commons file
name. For each, this asks Commons for the author, licence and a 960px copy (reusing copies
already downloaded into src/photos/raw/ and src/photos/full/), scales it to 640px wide, and
saves it as site/public/img/usa_kanada/<key>.jpg. The credits go to
tools/usa_canada/src/photos/credits.json, which the notebook's generator prints in its footer
and checks against the photos it uses.

Run: python3 -I tools/usa_canada/photo_prep.py
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from usa_canada_art import PHOTOS  # noqa: E402

ROOT = HERE / "src" / "photos"
FULL = ROOT / "full"
OUT = HERE.parents[1] / "site" / "public" / "img" / "usa_kanada"
UA = {"User-Agent": "notebook-photo-picker/1.0 (educational, non-commercial)"}
WIDTH = 640


def get(url):
    for wait in (20, 60, 120, None):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or wait is None:
                raise
            print("429, waiting", wait)
            time.sleep(wait)


def plain(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return " ".join(html.unescape(s).split())


def norm(name):
    return name.replace(" ", "_")


def cached_copies():
    """Commons file name -> a 960px copy already on disk."""
    have = {}
    cands = json.loads((ROOT / "candidates.json").read_text())
    for key, c in cands.items():
        for f in (ROOT / "raw").glob(f"{key}.*"):
            if c.get("file"):
                have[norm(c["file"])] = f
    return have


def main():
    FULL.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    have = cached_copies()
    files = list(PHOTOS.values())
    meta = {}
    for i in range(0, len(files), 40):
        q = {"action": "query", "prop": "imageinfo", "iiprop": "url|extmetadata",
             "iiurlwidth": 960, "format": "json",
             "titles": "|".join("File:" + f for f in files[i:i + 40])}
        res = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(q)))
        for page in res["query"]["pages"].values():
            if "imageinfo" not in page:
                raise SystemExit(f"not on Commons: {page['title']}")
            info = page["imageinfo"][0]
            em = info["extmetadata"]
            meta[norm(page["title"][5:])] = {
                "thumb": info["thumburl"], "page": info["descriptionurl"],
                "licence": plain(em.get("LicenseShortName", {}).get("value")),
                "licence_url": em.get("LicenseUrl", {}).get("value", ""),
                "artist": plain(em.get("Artist", {}).get("value")) or "unknown",
                "title": page["title"][5:]}
        time.sleep(2)
    credits = {}
    for key, fname in PHOTOS.items():
        m = meta[norm(fname)]
        lic = m["licence"]
        if lic.startswith("GFDL") or not lic:
            raise SystemExit(f"{key}: licence {lic!r} is not usable here")
        src = have.get(norm(fname)) or FULL / f"{key}.jpg"
        if not src.exists():
            src.write_bytes(get(m["thumb"]))
            print("downloaded", key)
            time.sleep(3)
        im = Image.open(src).convert("RGB")
        if im.width > WIDTH:
            im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
        dest = OUT / f"{key}.jpg"
        im.save(dest, quality=74, optimize=True, progressive=True)
        credits[key] = {**{k: m[k] for k in ("title", "page", "artist", "licence",
                                              "licence_url")},
                        "width": im.width, "height": im.height}
    (ROOT / "credits.json").write_text(json.dumps(credits, indent=1, ensure_ascii=False))
    stale = [p.name for p in OUT.glob("*.jpg") if p.stem not in PHOTOS]
    total = sum(p.stat().st_size for p in OUT.glob("*.jpg"))
    print(f"{len(credits)} photos, {total / 1e6:.1f} MB in {OUT}"
          + (f"; not in PHOTOS (delete by hand): {stale}" if stale else ""))


main()
