"""Pictures for the USA & Canada notebook: maps, charts and timelines, drawn as inline SVG.

tools/usa_canada/gen_usa_canada_notes.py imports this module; each public function returns the
HTML of one <figure>. Map shapes come from tools/usa_canada/src/na_geo.json (Natural Earth,
public domain; built by tools/usa_canada/build_na_geo.py). Colours are CSS classes and
variables defined in ART_CSS, so every picture follows the page's light and dark themes. Photos
are listed in PHOTOS, with the credit line their licence asks for;
tools/usa_canada/photo_prep.py copies them into site/public/img/usa_kanada/.

Preview: python3 tools/usa_canada/usa_canada_art.py   # every figure, in tmp/_art_preview.html
"""
import html
import json
import math
from pathlib import Path

HERE = Path(__file__).parent
GEO = json.loads((HERE / "src" / "na_geo.json").read_text())
X = '<tspan class="x">*</tspan>'          # "not on the reading list", inside SVG text
XH = '<sup class="x" title="not on the reading list">*</sup>'
_ids = {"n": 0}


def uid(prefix):
    _ids["n"] += 1
    return f"{prefix}{_ids['n']}"


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- geometry
class LAEA:
    """Lambert azimuthal equal-area projection on the unit sphere, y pointing down."""

    def __init__(self, lon0, lat0):
        self.l0 = math.radians(lon0)
        p0 = math.radians(lat0)
        self.sp0, self.cp0 = math.sin(p0), math.cos(p0)

    def __call__(self, lon, lat):
        lam, phi = math.radians(lon) - self.l0, math.radians(lat)
        sp, cp, cl = math.sin(phi), math.cos(phi), math.cos(lam)
        k = math.sqrt(2 / (1 + self.sp0 * sp + self.cp0 * cp * cl))
        return k * cp * math.sin(lam), -k * (self.cp0 * sp - self.sp0 * cp * cl)


def simplify(points, tol):
    """Douglas-Peucker on screen points; a closed ring is measured from its start point."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = points[a]
        bx, by = points[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)
        best, idx = -1.0, None
        for i in range(a + 1, b):
            px, py = points[i]
            d = (abs(dy * (px - ax) - dx * (py - ay)) / norm if norm
                 else math.hypot(px - ax, py - ay))
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(points, keep) if k]


def _n(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    s = s.replace("0.", ".", 1) if s.startswith(("0.", "-0.")) else s
    return "0" if s in ("", "-0", "-") else s


def fmt(points, close):
    """An SVG path: the first point absolute, the rest as relative moves (shorter)."""
    x0, y0 = round(points[0][0], 1), round(points[0][1], 1)
    out, px, py = [], x0, y0
    for x, y in points[1:]:
        rx, ry = round(x, 1), round(y, 1)
        if rx == px and ry == py:
            continue
        out.append(f"{_n(rx - px)},{_n(ry - py)}")
        px, py = rx, ry
    s = f"M{_n(x0)},{_n(y0)}" + ("l" + " ".join(out) if out else "")
    return s + ("Z" if close else "")


class Map:
    """One projected view drawn into the box (x, y, w, h) of a figure."""

    def __init__(self, proj, fit, box, pad=8, scale=None, centre=None):
        self.proj, self.box = proj, box
        x, y, w, h = box
        if scale is not None:                      # pixels per unit-sphere unit
            cx, cy = proj(*centre)
            self.s = scale
            self.ox, self.oy = x + w / 2 - scale * cx, y + h / 2 - scale * cy
            return
        pts = [proj(lo, la) for lo, la in fit]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        s = min((w - 2 * pad) / (max(xs) - min(xs)), (h - 2 * pad) / (max(ys) - min(ys)))
        self.s = s
        self.ox = x + (w - s * (max(xs) - min(xs))) / 2 - s * min(xs)
        self.oy = y + (h - s * (max(ys) - min(ys))) / 2 - s * min(ys)

    def xy(self, lon, lat):
        px, py = self.proj(lon, lat)
        return self.ox + self.s * px, self.oy + self.s * py

    def km(self):
        """Pixels per kilometre at the projection centre."""
        return self.s / 6371.0

    def _visible(self, pts, margin=40):
        x, y, w, h = self.box
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return not (max(xs) < x - margin or min(xs) > x + w + margin
                    or max(ys) < y - margin or min(ys) > y + h + margin)

    def polys(self, polys, tol=0.7, min_size=1.5):
        out = []
        for poly in polys:
            for i, ring in enumerate(poly):
                pts = [self.xy(lo, la) for lo, la in ring]
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                small = max(xs) - min(xs) < min_size and max(ys) - min(ys) < min_size
                if small or not self._visible(pts):
                    if i == 0:
                        break
                    continue
                pts = simplify(pts, tol)
                if len(pts) >= 3:
                    out.append(fmt(pts, True))
        return "".join(out)

    def lines(self, lines, tol=0.6):
        out = []
        for line in lines:
            pts = [self.xy(lo, la) for lo, la in line]
            if self._visible(pts):
                out.append(fmt(simplify(pts, tol), False))
        return "".join(out)

    def path(self, d, cls, extra=""):
        return f'<path class="{cls}" d="{d}"{extra}/>' if d else ""

    def clip(self):
        """A clipPath for this map's box; returns (defs, attribute)."""
        cid = uid("clip")
        x, y, w, h = self.box
        return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" '
                f'rx="10"/></clipPath>', f' clip-path="url(#{cid})"')


def bbox(lon0, lat0, lon1, lat1, n=12):
    """Points along the edges of a lon/lat box, for fitting a projected view."""
    pts = []
    for i in range(n + 1):
        t = i / n
        lo, la = lon0 + (lon1 - lon0) * t, lat0 + (lat1 - lat0) * t
        pts += [(lo, lat0), (lo, lat1), (lon0, la), (lon1, la)]
    return pts


def state(name):
    return GEO["states"][name]["geom"]


def place(name, adm1=None):
    rows = GEO["places"][name]
    if adm1:
        rows = [r for r in rows if r["adm1"] == adm1]
    best = max(rows, key=lambda r: r["pop"] or 0)
    return best["lon"], best["lat"]


def capital_of(st):
    caps = [(n, r) for n, rows in GEO["places"].items() for r in rows
            if r["adm1"].replace("Québec", "Quebec") == st and r["cls"] in ("Admin-1 capital",)]
    if st == "Ontario":
        return "Toronto", place("Toronto")
    if len(caps) != 1:
        raise SystemExit(f"capital of {st}: {[c[0] for c in caps]}")
    n, r = caps[0]
    return n, (r["lon"], r["lat"])


# ---------------------------------------------------------------- svg pieces
def text(x, y, s, cls="lb", anchor="start", extra=""):
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}"{a}{extra}>{s}</text>'


def multiline(x, y, lines, cls="lb", anchor="start", lh=13):
    return "".join(text(x, y + i * lh, s, cls, anchor) for i, s in enumerate(lines))


def star(x, y, r=5.5, cls="cap"):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return f'<path class="{cls}" d="{fmt(pts, True)}"/>'


def dot(x, y, r=3.2, cls="city"):
    return f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'


def leader(x0, y0, x1, y1):
    return f'<path class="leader" d="M{x0:.1f},{y0:.1f} {x1:.1f},{y1:.1f}"/>'


def svg(w, h, body, label, defs="", cls="map"):
    d = f"<defs>{defs}</defs>" if defs else ""
    return (f'<svg viewBox="0 0 {w} {h}" class="{cls}" role="img" '
            f'aria-label="{esc(label)}">{d}{body}</svg>')


def figure(svg_html, caption, minw=0, cls=""):
    style = f' style="--minw:{minw}px"' if minw else ""
    return (f'<figure class="viz {cls}"><div class="scroll"><div class="inner"{style}>'
            f'{svg_html}</div></div><figcaption>{caption}</figcaption></figure>')


# ---------------------------------------------------------------- regions
US_REGIONS = {
    "Northeast": ["Maine", "Massachusetts", "Rhode Island", "Connecticut", "New Hampshire",
                  "Vermont", "New York", "Pennsylvania", "New Jersey", "Delaware", "Maryland"],
    "Southeast": ["West Virginia", "Virginia", "Kentucky", "Tennessee", "North Carolina",
                  "South Carolina", "Georgia", "Alabama", "Mississippi", "Arkansas", "Louisiana",
                  "Florida"],
    "Midwest": ["Ohio", "Indiana", "Michigan", "Illinois", "Missouri", "Wisconsin", "Minnesota",
                "Iowa", "Kansas", "Nebraska", "South Dakota", "North Dakota"],
    "Southwest": ["Texas", "Oklahoma", "New Mexico", "Arizona"],
    "West": ["Colorado", "Wyoming", "Montana", "Idaho", "Washington", "Oregon", "Utah", "Nevada",
             "California", "Alaska", "Hawaii"],
}
CA_REGIONS = {
    "East": ["Newfoundland and Labrador", "Nova Scotia", "Prince Edward Island", "New Brunswick"],
    "Central": ["Quebec", "Ontario"],
    "West": ["Manitoba", "Saskatchewan", "Alberta", "British Columbia"],
    "North": ["Yukon", "Northwest Territories", "Nunavut"],
}
REGION_CLS = {"Northeast": "r-ne", "Southeast": "r-se", "Midwest": "r-mw", "Southwest": "r-sw",
              "West": "r-w"}
CA_CLS = {"East": "r-ce", "Central": "r-cc", "West": "r-cw", "North": "r-cn"}
STATE_REGION = {s: r for r, ss in US_REGIONS.items() for s in ss}
PROV_REGION = {s: r for r, ss in CA_REGIONS.items() for s in ss}
OTHER = [c for c in GEO["countries"] if c not in ("USA", "CAN")]


def context_land(m):
    """Neighbouring countries, in grey."""
    return m.path("".join(m.polys(GEO["countries"][c]) for c in OTHER), "land0")


def lakes(m, min_size=2.5, names=None):
    polys = [p for n, ps in GEO["lakes"].items() if names is None or n in names for p in ps]
    return m.path(m.polys(polys, min_size=min_size), "lake")


def na_view(box, pad=6):
    proj = LAEA(-100, 52)
    return Map(proj, bbox(-168, 24, -52, 72) + [(-75, 83), (-95, 82)], box, pad=pad)


def hawaii_inset(box, fill_cls):
    m = Map(LAEA(-157, 20.5), bbox(-160.4, 18.8, -154.7, 22.3), box, pad=4)
    x, y, w, h = box
    return (f'<rect class="inset" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
            + m.path(m.polys(state("Hawaii"), min_size=0.5), fill_cls)
            + text(x + 5, y + 12, "Hawaii", "lb-s"))


# ---------------------------------------------------------------- shared pieces
# Natural Earth's river lines stop at Cornwall; below it the river is drawn through the towns on
# its banks: Kingston, Brockville, Cornwall, Montreal, Trois-Rivieres, Quebec City, to the Gulf.
ST_LAWRENCE = [(-76.45, 44.2), (-75.79, 44.5), (-75.27, 44.86), (-74.71, 45.0), (-73.95, 45.33),
               (-73.55, 45.52), (-73.1, 45.9), (-72.55, 46.35), (-71.95, 46.6), (-71.2, 46.82),
               (-70.6, 47.15), (-69.8, 47.75), (-69.0, 48.2), (-68.3, 48.65), (-67.4, 49.15)]
def land(m, us_cls="usa", can_cls="can", hawaii=False):
    usa = [p for s, d in GEO["states"].items()
           if d["country"] == "USA" and (hawaii or s != "Hawaii") for p in d["geom"]]
    can = [p for d in GEO["states"].values() if d["country"] == "CAN" for p in d["geom"]]
    return m.path(m.polys(usa), us_cls) + m.path(m.polys(can), can_cls)


def frame(W, H):
    return f'<rect class="sea" width="{W}" height="{H}" rx="12"/>'


def at(m, lon, lat, s, cls="lb", anchor="middle", dx=0, dy=0):
    x, y = m.xy(lon, lat)
    return text(x + dx, y + dy, s, cls, anchor)


def badge(x, y, n, cls="badge"):
    return (f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="9"/>'
            + text(x, y + 4, str(n), "lb-badge", "middle"))


def peak(x, y, size=7, cls="peak"):
    return (f'<path class="{cls}" d="M{x:.1f},{y - size:.1f} {x + size * .9:.1f},{y + size * .6:.1f} '
            f'{x - size * .9:.1f},{y + size * .6:.1f}Z"/>')


def callout(m, lon, lat, lines, dx, dy, anchor="start", cls="lb-s", lh=13, mark=None):
    """A mark at a place, a leader line and a label (dx, dy) pixels away."""
    x, y = m.xy(lon, lat)
    out = {"dot": dot(x, y, 3.2), "peak": peak(x, y), "star": star(x, y, 6),
           "ring": dot(x, y, 3.6, "city-x"), None: ""}[mark]
    tx, ty = x + dx, y + dy
    if abs(dx) > 12 or abs(dy) > 12:
        ex = tx - 3 if anchor == "start" else tx + 3 if anchor == "end" else tx
        ey = ty - 4 if dy >= 0 else ty + 2 + lh * (len(lines) - 1) - lh + 6
        out = leader(x, y, ex, ey) + out
    return out + multiline(tx, ty, lines, cls, anchor, lh)


def legend_box(x, y, items, w=190):
    """items: (svg-mark-at-(12, cy), label)."""
    h = 12 + 22 * len(items)
    rows = "".join(mk(14, 18 + 22 * i) + text(30, 22 + 22 * i, lb, "lb-s")
                   for i, (mk, lb) in enumerate(items))
    return (f'<g transform="translate({x},{y})"><rect class="legend-bg" width="{w}" '
            f'height="{h}" rx="8"/>{rows}</g>')


def nice(n):
    return f"{n:,}".replace(",", ",")


# ---------------------------------------------------------------- F1: the big picture
def where_map():
    W, H = 760, 600
    m = na_view((0, 0, W, H))
    body = [frame(W, H), context_land(m), land(m), lakes(m)]
    body.append(m.path(m.lines([[(lo, 66.56) for lo in range(-170, -40, 2)]]), "circle-line"))
    body.append(at(m, -160, 66.9, "Arctic Circle" + X, "lb-s lb-m", "start", dy=-3))
    body.append(m.path(m.lines(GEO["borders"]["USA-CAN"]), "border-hot"))
    body.append(m.path(m.lines(GEO["borders"]["USA-MEX"]), "border-warm"))
    for lon, lat, s, cls in [(-112, 58, "CANADA", "lb-big"), (-99, 38.5, "USA", "lb-big"),
                             (-104, 25.5, "MEXICO", "lb-mid lb-m"),
                             (-42, 75, "GREENLAND", "lb-mid lb-m"),
                             (-153, 65, "ALASKA (USA)", "lb-mid")]:
        body.append(at(m, lon, lat, s, cls))
    for lon, lat, lines in [(-135, 40, ["PACIFIC", "OCEAN"]), (-58, 36, ["ATLANTIC", "OCEAN"]),
                            (-140, 77.5, ["ARCTIC OCEAN"]), (-90, 25.3, ["Gulf of", "Mexico"]),
                            (-176, 58, ["Bering", "Sea"])]:
        x, y = m.xy(lon, lat)
        body.append(multiline(x, y, lines, "lb-sea", "middle", 15))
    for name, (lon, lat), dx, dy, anchor, kind in [
            ("Washington, D.C.", place("Washington, D.C."), 8, 14, "start", "cap"),
            ("Ottawa", place("Ottawa"), -4, -9, "end", "cap"),
            ("New York", place("New York"), 7, 4, "start", "city"),
            ("Toronto", place("Toronto"), -7, 12, "end", "city")]:
        x, y = m.xy(lon, lat)
        body.append(star(x, y, 6.5) if kind == "cap" else dot(x, y, 3.6))
        body.append(text(x + dx, y + dy, name, "lb-b" if kind == "cap" else "lb", anchor))
    body.append(callout(m, -101, 49, ["USA–Canada border: 8,891 km,",
                                      "the longest in the world"], 6, -34, "middle", "lb-b", 14))
    body.append(callout(m, -141, 64, ["the Alaska part:", "2,475 km"], 34, 34))
    body.append(callout(m, -106, 31.6, ["USA–Mexico border:", "3,145 km"], -34, 38, "end"))
    body.append(hawaii_inset((12, H - 112, 150, 100), "usa"))
    body.append(legend_box(W - 168, H - 90, [
        (lambda x, y: star(x, y, 6.5), "capital"), (lambda x, y: dot(x, y, 3.6), "largest city"),
        (lambda x, y: f'<path class="border-hot" d="M{x - 9},{y} {x + 9},{y}"/>',
         "USA–Canada border")], w=158))
    label = ("Map of North America: Canada in the north, the USA south of it with Alaska in the "
             "northwest, Mexico in the south; the Pacific, Atlantic and Arctic Oceans.")
    return figure(svg(W, H, "".join(body), label),
                  "Canada touches three oceans; the USA touches two, plus the Gulf of Mexico. "
                  "Their border is the longest in the world.", minw=560)


# ---------------------------------------------------------------- F2: regions
def regions_map():
    W, H = 760, 600
    m = na_view((0, 0, W, H))
    body = [frame(W, H), context_land(m)]
    for st, d in GEO["states"].items():
        if st in ("Hawaii", "District of Columbia"):
            continue
        cls = (REGION_CLS[STATE_REGION[st]] if d["country"] == "USA"
               else CA_CLS[PROV_REGION[st]])
        body.append(m.path(m.polys(d["geom"]), f"st {cls}"))
    body.append(lakes(m))
    body.append(m.path(m.lines(GEO["borders"]["USA-CAN"]), "border-nat"))
    for lon, lat, s in [(-74.5, 43.3, "NORTHEAST"), (-85.5, 33.3, "SOUTHEAST"),
                        (-93, 42.5, "MIDWEST"), (-104.5, 32.5, "SOUTHWEST"),
                        (-114, 42, "WEST"), (-151, 64.5, "WEST"),
                        (-61, 51.5, "EAST"), (-80, 51.5, "CENTRAL"), (-110, 53.5, "WEST"),
                        (-112, 66, "NORTH")]:
        body.append(at(m, lon, lat, s, "lb-reg"))
    for lon, lat, s in [(-100, 36, "USA"), (-97, 60, "CANADA")]:
        body.append(at(m, lon, lat, s, "lb-big lb-faint"))
    body.append(hawaii_inset((12, H - 112, 150, 100), "st r-w"))
    label = ("Map of the regions: the USA's Northeast, Southeast, Midwest, Southwest and West "
             "(with Alaska and Hawaii); Canada's East, Central, West and North.")
    return figure(svg(W, H, "".join(body), label),
                  "Five regions of the USA, four of Canada. Alaska and Hawaii belong to the "
                  "West; Canada's North is its three territories.", minw=560)


# ---------------------------------------------------------------- F3: size and people
def bars_panel(x0, y0, w, title, rows, vmax, unit_fmt):
    """rows: (label, value, cls, value_text). Horizontal bars from one baseline."""
    lab_w, gap, th = 92, 34, 20
    out = [text(x0, y0, title, "lb-b")]
    bw = w - lab_w - 70
    for i, (lab, v, cls, vt) in enumerate(rows):
        y = y0 + 18 + i * gap
        L = max(2.0, bw * v / vmax)
        out.append(text(x0 + lab_w - 8, y + th / 2 + 4, lab, "lb", "end"))
        out.append(bar(x0 + lab_w, y, L, th, cls))
        out.append(text(x0 + lab_w + L + 6, y + th / 2 + 4, vt, "lb-b"))
    out.append(f'<path class="axis" d="M{x0 + lab_w},{y0 + 10} {x0 + lab_w},{y0 + 18 + len(rows) * gap - 8}"/>')
    return "".join(out)


def bar(x, y, L, th, cls, r=4):
    """A horizontal bar, square at the baseline, 4px rounded at its end."""
    r = min(r, L / 2, th / 2)
    return (f'<path class="{cls}" d="M{x:.1f},{y:.1f}h{L - r:.1f}a{r},{r} 0 0 1 {r},{r}'
            f'v{th - 2 * r:.1f}a{r},{r} 0 0 1 -{r},{r}h-{L - r:.1f}Z"/>')


def size_people_chart():
    W, H = 760, 170
    a = bars_panel(10, 22, 370, "Area, million km²", [
        ("Canada", 9.98, "b-can", "9.98"), ("USA", 9.83, "b-usa", "9.83" + X),
        ("Poland" + X, 0.31, "b-pl", "0.31")], 10, None)
    b = bars_panel(390, 22, 370, "People, millions", [
        ("USA", 346, "b-usa", "346"), ("Canada", 40, "b-can", "40"),
        ("Poland" + X, 37, "b-pl", "37")], 350, None)
    label = ("Bar charts. Area: Canada 9.98 million square kilometres, USA 9.83, Poland 0.31. "
             "People: USA 346 million, Canada 40 million, Poland 37 million.")
    return figure(svg(W, H, a + b, label, cls="chart"),
                  "Almost the same size, but the USA has almost nine times as many people. "
                  "Canada has about as many people as Poland" + XH + ", in a country 32 times "
                  "bigger.", minw=560)


# ---------------------------------------------------------------- F4: capitals by region
REGION_VIEW = {
    "Northeast": dict(c=(-74, 42.6), box=(-80.6, 37.8, -66.9, 47.5), W=560, H=560),
    "Southeast": dict(c=(-85, 32.5), box=(-94.7, 24.4, -75.4, 40.7), W=560, H=540),
    "Midwest": dict(c=(-92, 43), box=(-104.1, 35.9, -80.4, 49.4), W=560, H=440),
    "Southwest": dict(c=(-104, 31.5), box=(-114.9, 25.8, -93.5, 37.1), W=560, H=380),
    "West": dict(c=(-113, 41), box=(-125.5, 31.2, -101.9, 49.1), W=560, H=560),
}
# per state: "name" = where its name goes (lon, lat), with a leader line to the state;
# "cap" = the capital label's offset in pixels and its anchor
TWEAK = {
    "Rhode Island": {"name": (-70.2, 40.75), "cap": (7, 12, "start")},
    "Connecticut": {"pos": (-72.7, 41.45), "cap": (-6, -6, "end")},
    "Delaware": {"name": (-73.9, 38.75), "cap": (7, 4, "start")},
    "New Jersey": {"name": (-72.9, 39.6), "cap": (7, 4, "start")},
    "New Hampshire": {"name": (-69.4, 43.0), "cap": (-6, 12, "end")},
    "Massachusetts": {"pos": (-72.2, 42.42), "cap": (7, 4, "start")},
    "Vermont": {"pos": (-72.75, 43.75), "cap": (-6, 4, "end")},
    "New York": {"cap": (-7, 4, "end")},
    "Pennsylvania": {"cap": (-7, 4, "end")},
    "Maryland": {"name": (-76.6, 37.9), "cap": (-7, 4, "end")},
    "Maine": {"cap": (7, 4, "start")},
    "West Virginia": {"cap": (0, 17, "middle")},
    "Kentucky": {"cap": (0, -9, "middle"), "pos": (-85.3, 37.35)},
    "South Carolina": {"cap": (7, 4, "start"), "pos": (-80.5, 33.45)},
    "North Carolina": {"pos": (-80.6, 35.35)},
    "Arkansas": {"pos": (-92.4, 35.75)},
    "Louisiana": {"cap": (-6, -7, "end"), "pos": (-92.6, 31.0)},
    "Mississippi": {"cap": (-6, -7, "end")},
    "Florida": {"cap": (6, -6, "start")},
    "Michigan": {"cap": (0, 17, "middle")},
    "Missouri": {"cap": (6, 12, "start"), "pos": (-92.6, 37.25)},
    "Illinois": {"cap": (-7, 4, "end"), "pos": (-89.1, 40.75)},
    "Indiana": {"cap": (6, 12, "start"), "pos": (-86.3, 40.6)},
    "Ohio": {"cap": (6, 12, "start"), "pos": (-82.6, 40.75)},
    "South Dakota": {"pos": (-100.3, 44.95)},
    "Oklahoma": {"pos": (-97.4, 36.3)},
    "Idaho": {"pos": (-114.5, 44.7)},
    "Minnesota": {"cap": (7, 4, "start")},
    "Iowa": {"cap": (7, 4, "start")},
    "Texas": {"cap": (-7, 4, "end")},
    "California": {"cap": (-7, 4, "end")},
    "Nevada": {"cap": (7, 4, "start"), "pos": (-116.6, 38.5)},
    "Oregon": {"cap": (-7, -6, "end")},
    "Washington": {"cap": (-7, 4, "end"), "pos": (-120.3, 47.35)},
    "Utah": {"cap": (7, -6, "start")},
}
CATCH = {   # famous big cities that are not the capital, by region
    "Northeast": [("New York City", "New York", "New York", (4, 18, "start")),
                  ("Philadelphia", "Philadelphia", "Pennsylvania", (-6, 14, "end")),
                  ("Baltimore", "Baltimore", "Maryland", (-6, -7, "end"))],
    "Southeast": [("Miami", "Miami", "Florida", (-7, 4, "end")),
                  ("New Orleans", "New Orleans", "Louisiana", (6, 12, "start")),
                  ("Louisville", "Louisville", "Kentucky", (-7, 4, "end")),
                  ("Charleston, SC", "Charleston", "South Carolina", (6, 12, "start"))],
    "Midwest": [("Chicago", "Chicago", "Illinois", (6, -6, "start")),
                ("Detroit", "Detroit", "Michigan", (7, 4, "start")),
                ("St. Louis", "St. Louis", "Missouri", (7, 4, "start"))],
    "Southwest": [("Houston", "Houston", "Texas", (7, 4, "start"))],
    "West": [("Los Angeles", "Los Angeles", "California", (-7, 4, "end")),
             ("Seattle", "Seattle", "Washington", (7, -5, "start")),
             ("Las Vegas", "Las Vegas", "Nevada", (7, 4, "start")),
             ("Portland", "Portland", "Oregon", (7, 4, "start"))],
}


def state_label(m, st, cls="lb-st"):
    lon, lat = GEO["states"][st]["label"]
    tw = TWEAK.get(st, {})
    name = st.upper() if len(st) < 9 else st
    if "name" in tw:
        x0, y0 = m.xy(lon, lat)
        x1, y1 = m.xy(*tw["name"])
        return leader(x0, y0, x1, y1 - 4) + text(x1, y1 + 4, st, cls, "middle")
    if "pos" in tw:
        lon, lat = tw["pos"]
    return at(m, lon, lat, st, cls)


def capital_mark(m, st, big=False):
    name, (lon, lat) = capital_of(st)
    name = {"Québec": "Quebec City"}.get(name, name)
    x, y = m.xy(lon, lat)
    dx, dy, anchor = TWEAK.get(st, {}).get("cap", (7, 4, "start"))
    return star(x, y, 6) + text(x + dx, y + dy, name, "lb-cap", anchor)


def catch_mark(m, label, name, adm1, off):
    lon, lat = place(name, adm1)
    x, y = m.xy(lon, lat)
    dx, dy, anchor = off
    return dot(x, y, 3.4, "city-x") + text(x + dx, y + dy, label, "lb-catch", anchor)


def region_map(region):
    v = REGION_VIEW[region]
    W, H = v["W"], v["H"]
    m = Map(LAEA(*v["c"]), bbox(*v["box"]), (0, 0, W, H), pad=4)
    mine = [s for s in US_REGIONS[region] if s not in ("Alaska", "Hawaii")]
    body = [frame(W, H), context_land(m)]
    others = [p for s, d in GEO["states"].items() if s not in mine for p in d["geom"]]
    body.append(m.path(m.polys(others), "land1"))
    body.append("".join(m.path(m.polys(state(s)), f"st {REGION_CLS[region]}") for s in mine))
    body.append(lakes(m, min_size=3))
    body.append(m.path(m.lines(GEO["borders"]["USA-CAN"] + GEO["borders"]["USA-MEX"]),
                       "border-nat"))
    body += [state_label(m, s) for s in mine]
    body += [catch_mark(m, *c) for c in CATCH.get(region, [])]
    body += [capital_mark(m, s) for s in mine]
    if region == "West":
        body.append(alaska_inset((W - 210, H - 152, 202, 144)))
        body.append(hawaii_inset_capital((8, H - 96, 150, 88)))
    label = (f"Map of the {region} region: " + ", ".join(
        f"{s} (capital {capital_of(s)[0]})" for s in US_REGIONS[region]) + ".")
    return figure(svg(W, H, "".join(body), label), "", minw=420, cls="regmap")


def alaska_inset(box):
    m = Map(LAEA(-152, 62), bbox(-170, 54, -130, 71.5), box, pad=4)
    x, y, w, h = box
    out = (f'<rect class="inset" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
           + m.path(m.polys(state("Alaska"), min_size=1.5), "st r-w")
           + m.path(m.polys(GEO["states"]["Yukon"]["geom"] + GEO["states"]["British Columbia"]["geom"]), "land1"))
    jx, jy = m.xy(*capital_of("Alaska")[1])
    ax, ay = m.xy(*place("Anchorage"))
    return (out + text(x + 6, y + 14, "ALASKA", "lb-st") + text(x + 6, y + 27, "(smaller scale)", "lb-tiny")
            + dot(ax, ay, 3.2, "city-x") + text(ax - 6, ay + 4, "Anchorage", "lb-catch", "end")
            + star(jx, jy, 6) + text(jx - 4, jy + 15, "Juneau", "lb-cap", "middle"))


def hawaii_inset_capital(box):
    m = Map(LAEA(-157, 20.5), bbox(-160.4, 18.8, -154.7, 22.3), box, pad=4)
    x, y, w, h = box
    hx, hy = m.xy(*capital_of("Hawaii")[1])
    return (f'<rect class="inset" x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
            + m.path(m.polys(state("Hawaii"), min_size=0.5), "st r-w")
            + text(x + w - 6, y + 14, "HAWAII", "lb-st", "end")
            + star(hx, hy, 6) + text(hx + 4, hy + 16, "Honolulu", "lb-cap"))


def map_legend_html():
    s = ('<svg viewBox="-8 -8 16 16" width="16" height="16" aria-hidden="true">'
         + star(0, 0, 6.5) + "</svg>")
    c = ('<svg viewBox="-8 -8 16 16" width="16" height="16" aria-hidden="true">'
         + dot(0, 0, 4, "city-x") + "</svg>")
    return (f'<p class="maplegend"><span>{s} the capital</span>'
            f'<span>{c} <i>a famous big city that is not the capital</i></span></p>')


# ---------------------------------------------------------------- F5: same scale
def sizes_figure():
    shapes = [("Alaska", state("Alaska"), (-150, 62)), ("Texas", state("Texas"), (-99.3, 31.3)),
              ("California", state("California"), (-119.5, 37.2)),
              ("Poland" + X, GEO["abroad"]["POL"], (19.4, 52.1)),
              ("Rhode Island", state("Rhode Island"), (-71.5, 41.7))]
    k = 0.104                                         # pixels per km
    W, H, gap, base = 760, 330, 22, 286
    projected = []
    for name, geom, c in shapes:
        proj = LAEA(*c)
        pts = [proj(lo, la) for poly in geom for lo, la in poly[0]]
        xs, ys = [p[0] * 6371 * k for p in pts], [p[1] * 6371 * k for p in pts]
        projected.append((name, geom, proj, min(xs), max(xs), min(ys), max(ys)))
    x = 8
    body = []
    for name, geom, proj, x0, x1, y0, y1 in projected:
        m = Map(proj, None, (0, 0, W, H), scale=6371 * k, centre=(0, 0)) if False else None
        ox, oy = x - x0, base - y1
        d = []
        for poly in geom:
            ring = poly[0]
            pts = [(ox + p[0] * 6371 * k, oy + p[1] * 6371 * k) for p in (proj(lo, la) for lo, la in ring)]
            if max(abs(a[0] - b[0]) for a, b in zip(pts, pts[1:] + pts[:1])) < 0.01 and len(pts) < 3:
                continue
            d.append(fmt(simplify(pts, 0.4), True))
        cls = "b-pl-f" if name.startswith("Poland") else "b-usa-f"
        body.append(f'<path class="{cls}" d="{"".join(d)}"/>')
        cx = x + (x1 - x0) / 2
        if name == "Rhode Island":
            body.append(leader(cx, base - 4, cx - 6, base - 96))
            body.append(multiline(cx - 2, base - 124, ["Rhode Island:", "this dot"], "lb-b", "end", 14))
        else:
            body.append(text(cx, base + 22, name, "lb-b", "middle"))
        x += (x1 - x0) + gap
    body.append(f'<path class="axis" d="M8,{base + 2} {W - 8},{base + 2}"/>')
    km = 500 * k
    body.append(f'<path class="scalebar" d="M{W - 20 - km:.1f},{H - 10} h{km:.1f}"/>'
                + text(W - 20 - km / 2, H - 16, "500 km", "lb-s", "middle"))
    label = ("Alaska, Texas, California, Poland and Rhode Island drawn at the same scale: Alaska "
             "is by far the biggest, Rhode Island a tiny dot.")
    return figure(svg(W, H, "".join(body), label, cls="chart"),
                  "All five at the same scale. Alaska is a bit more than twice the size of Texas "
                  "and four times the size of California; Rhode Island is about 1.5 times "
                  "Luxembourg.", minw=560)


# ---------------------------------------------------------------- F6: Canada's capitals
MARITIMES = ["New Brunswick", "Nova Scotia", "Prince Edward Island"]
CA_TWEAK = {
    "Newfoundland and Labrador": {"cap": (-6, 15, "end"), "pos": (-61.5, 53.4)},
    "Quebec": {"cap": (-6, -8, "end")},
    "Ontario": {"cap": (-8, 14, "end")},
    "British Columbia": {"cap": (-6, 14, "end")},
    "Alberta": {"cap": (-7, 4, "end")},
    "Saskatchewan": {"cap": (7, 12, "start"), "pos": (-106, 54.7)},
    "Manitoba": {"cap": (7, 4, "start")},
    "Yukon": {"cap": (-7, 4, "end")},
    "Northwest Territories": {"cap": (7, 4, "start"), "pos": (-118, 64.5)},
    "Nunavut": {"cap": (7, 4, "start"), "pos": (-95, 66)},
}
MARITIME_CAPS = {"New Brunswick": (6, 15, "start"), "Nova Scotia": (7, 12, "start"),
                 "Prince Edward Island": (6, 15, "start")}
MARITIME_NAMES = {"New Brunswick": (-66.3, 46.75), "Nova Scotia": (-62.4, 44.75),
                  "Prince Edward Island": (-62.6, 47.45)}


def canada_map():
    W, H = 760, 560
    m = Map(LAEA(-96, 60), bbox(-138, 42, -54, 70) + [(-80, 83), (-120, 78)], (0, 0, W, H), pad=6)
    body = [frame(W, H), context_land(m)]
    usa = [p for s, d in GEO["states"].items() if d["country"] == "USA" for p in d["geom"]]
    body.append(m.path(m.polys(usa), "land1"))
    for st, reg in PROV_REGION.items():
        body.append(m.path(m.polys(state(st)), f"st {CA_CLS[reg]}"))
    body.append(lakes(m, min_size=3))
    for st in PROV_REGION:
        if st in MARITIMES:
            continue
        lon, lat = CA_TWEAK.get(st, {}).get("pos", GEO["states"][st]["label"])
        body.append(at(m, lon, lat, st, "lb-st"))
    for label, name, adm1, off in [("Vancouver", "Vancouver", "British Columbia", (7, 4, "start")),
                                   ("Calgary", "Calgary", "Alberta", (7, 4, "start")),
                                   ("Saskatoon", "Saskatoon", "Saskatchewan", (7, 4, "start")),
                                   ("Montreal", "Montréal", "Québec", (6, 16, "start"))]:
        body.append(catch_mark(m, label, name, adm1, off))
    for st in PROV_REGION:
        name, (lon, lat) = capital_of(st)
        name = {"Québec": "Quebec City"}.get(name, name)
        x, y = m.xy(lon, lat)
        body.append(star(x, y, 6))
        if st not in MARITIMES:
            dx, dy, anchor = CA_TWEAK.get(st, {}).get("cap", (7, 4, "start"))
            body.append(text(x + dx, y + dy, name, "lb-cap", anchor))
    ox, oy = m.xy(*place("Ottawa"))
    body.append(f'<circle class="cap-ring" cx="{ox:.1f}" cy="{oy:.1f}" r="8.5"/>' + star(ox, oy, 6)
                + leader(ox, oy, ox + 10, oy + 46)
                + multiline(ox + 12, oy + 58, ["Ottawa: the capital", "of the whole country"],
                            "lb-cap", "start", 14))
    body.append(at(m, -104, 45.6, "USA", "lb-mid lb-m"))
    # the Maritimes, enlarged in a box over Greenland
    box = bbox(-68.6, 43.3, -59.6, 48.3)
    xs, ys = zip(*(m.xy(lo, la) for lo, la in box))
    body.append(f'<rect class="inset-mark" x="{min(xs):.1f}" y="{min(ys):.1f}" '
                f'width="{max(xs) - min(xs):.1f}" height="{max(ys) - min(ys):.1f}" rx="3"/>')
    ib = (W - 236, 10, 226, 176)
    body.append(leader(max(xs), min(ys), ib[0] + 30, ib[1] + ib[3]))
    body.append(maritimes_inset(ib))
    label = ("Map of Canada's ten provinces and three territories with their capitals; Ottawa, "
             "in Ontario, is the capital of the country. An enlarged box shows New Brunswick, "
             "Nova Scotia and Prince Edward Island.")
    return figure(svg(W, H, "".join(body), label),
                  "Canada's provinces, coloured by region as above, with their capitals; the box "
                  "enlarges the three small provinces by the Atlantic. Most Canadians live in the "
                  "south, near the USA.", minw=560)


def maritimes_inset(box):
    m = Map(LAEA(-64, 46), bbox(-68.6, 43.3, -59.6, 48.3), box, pad=2)
    x, y, w, h = box
    cid = uid("clip")
    out = [f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/></clipPath>',
           f'<g clip-path="url(#{cid})"><rect class="sea" x="{x}" y="{y}" width="{w}" height="{h}"/>',
           m.path(m.polys([p for s, d in GEO["states"].items() if d["country"] == "USA"
                           for p in d["geom"]]), "land1"),
           m.path(m.polys(state("Quebec")), "st r-cc"),
           m.path(m.polys(state("Newfoundland and Labrador")), "st r-ce")]
    out += [m.path(m.polys(state(s), min_size=0.8), "st r-ce") for s in MARITIMES]
    for st in MARITIMES:
        out.append(at(m, *MARITIME_NAMES[st], st, "lb-st"))
        name, (lon, lat) = capital_of(st)
        cx, cy = m.xy(lon, lat)
        dx, dy, anchor = MARITIME_CAPS[st]
        out.append(star(cx, cy, 6) + text(cx + dx, cy + dy, name, "lb-cap", anchor))
    out.append(text(x + w - 6, y + h - 8, "the Maritimes, enlarged", "lb-tiny", "end"))
    out.append("</g>")
    out.append(f'<rect class="inset" x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none"/>')
    return "".join(out)


# ---------------------------------------------------------------- F7: mountains and landscapes
def mountains_map():
    W, H = 760, 600
    m = na_view((0, 0, W, H))
    A = GEO["areas"]
    body = [frame(W, H), context_land(m), land(m, "land1", "land1")]
    for name, cls in [("Great Plains", "plain"), ("Canadian Shield", "shield"),
                      ("Barren Grounds", "tundra"), ("Arctic Archipelago", "tundra"),
                      ("Baffin Island", "tundra")]:
        body.append(m.path(m.polys(A[name], min_size=2), cls))
    body.append(lakes(m, min_size=3))
    for name in ["Rocky Mountains", "Appalachian Mountains", "Sierra Nevada", "Cascade Range",
                 "Alaska Range", "Brooks Range", "Adirondacks", "Ozarks", "Coast Mountains",
                 "Mackenzie Mountains"]:
        body.append(m.path(m.polys(A[name], min_size=1), "mtn"))
    body.append(m.path(m.lines(GEO["borders"]["USA-CAN"]), "border-nat"))
    for lon, lat, s, rot in [(-109.6, 42.6, "ROCKY MOUNTAINS", -58), (-121, 55.5, "THE ROCKIES", -52),
                             (-78.6, 39.6, "APPALACHIANS", -38), (-149, 61.4, "Alaska Range", 0),
                             (-161, 66.9, "Brooks Range", 0)]:
        x, y = m.xy(lon, lat)
        body.append(text(x, y, s, "lb-mtn", "middle", f' transform="rotate({rot} {x:.1f} {y:.1f})"'))
    body.append(callout(m, -119.6, 38.4, ["Sierra Nevada"], -40, -10, "end", "lb-mtn"))
    body.append(callout(m, -121.6, 45.0, ["Cascade Range"], -40, 12, "end", "lb-mtn"))
    body.append(callout(m, -74.2, 44.1, ["Adirondacks"], 24, -30, "start", "lb-mtn"))
    body.append(callout(m, -92.6, 36.9, ["Ozarks"], -6, 28, "middle", "lb-mtn"))
    for lon, lat, s in [(-100, 41.5, "Great Plains"), (-102.5, 52.6, "Prairies"),
                        (-82, 53.5, "Canadian Shield"), (-103, 66, "Arctic tundra")]:
        body.append(at(m, lon, lat, s, "lb-land"))
    for name, km, dx, dy, anchor in [("Denali", "6,190 m", -6, -12, "end"),
                                     ("Mount Logan", "5,959 m", 8, -6, "start"),
                                     ("Mount Whitney", "4,421 m", -8, 22, "end"),
                                     ("Mount Elbert", "4,401 m", 8, 16, "start"),
                                     ("Mount Rainier", "4,392 m", 10, 2, "start"),
                                     ("Mount Mitchell", "2,037 m", 9, 14, "start"),
                                     ("Mount Marcy", "1,629 m", 8, -4, "start"),
                                     ("Mount Chamberlin", "2,749 m", 10, -16, "start")]:
        p = GEO["peaks"][name]
        x, y = m.xy(p["lon"], p["lat"])
        body.append(peak(x, y) + multiline(x + dx, y + dy, [name, km], "lb-pk", anchor, 12))
    tx, ty = m.xy(-65.35, 66.54)
    body.append(peak(tx, ty) + multiline(tx + 8, ty + 14, ["Mount Thor:", "1,250 m cliff"], "lb-pk", "start", 12))
    body.append(at(m, -70, 69.5, "Baffin Island", "lb-land"))
    body.append(legend_box(W - 178, H - 112, [
        (lambda x, y: f'<rect class="mtn" x="{x - 9}" y="{y - 6}" width="18" height="12" rx="3"/>', "mountains"),
        (lambda x, y: f'<rect class="plain" x="{x - 9}" y="{y - 6}" width="18" height="12" rx="3"/>', "plains, prairies"),
        (lambda x, y: f'<rect class="shield" x="{x - 9}" y="{y - 6}" width="18" height="12" rx="3"/>', "Canadian Shield"),
        (lambda x, y: f'<rect class="tundra" x="{x - 9}" y="{y - 6}" width="18" height="12" rx="3"/>', "Arctic tundra")], w=168))
    label = ("Map of mountains and landscapes: the Rockies run from New Mexico far into Canada, "
             "the Appalachians along the east; peaks Denali, Mount Logan, Whitney, Elbert, "
             "Rainier, Mitchell, Marcy, Chamberlin; the Great Plains, Canadian Shield and tundra.")
    return figure(svg(W, H, "".join(body), label),
                  "The Rockies run down the west of both countries, the old Appalachians down "
                  "the east. The two highest peaks are on either side of the Alaska–Yukon "
                  "border: Denali in Alaska, Mount Logan in the Yukon.", minw=560)


def west_map():
    W, H = 620, 640
    m = Map(LAEA(-114, 39.5), bbox(-125, 31, -103, 49.2), (0, 0, W, H), pad=4)
    A = GEO["areas"]
    body = [frame(W, H), context_land(m), land(m, "land1", "land1")]
    mojave = [[[(-118.6, 34.6), (-118.3, 35.3), (-117.9, 36.0), (-117.6, 36.9), (-116.8, 37.3),
                (-115.7, 37.0), (-114.9, 36.6), (-114.1, 36.2), (-114.0, 35.3), (-114.4, 34.6),
                (-115.3, 34.0), (-116.3, 33.8), (-117.2, 34.0), (-118.0, 34.3), (-118.6, 34.6)]]]
    for geom, cls in [(A["Great Basin"], "desert"), (mojave, "desert d2"),
                      (A["Sonoran Desert"], "desert"), (A["Chihuahuan Desert"], "desert d2")]:
        body.append(m.path(m.polys(geom), cls))
    for name in ["Rocky Mountains", "Sierra Nevada", "Cascade Range"]:
        body.append(m.path(m.polys(A[name]), "mtn"))
    body.append(m.path("".join(m.polys(state(s)) for s in GEO["states"]
                               if GEO["states"][s]["country"] == "USA"), "edges"))
    body.append(lakes(m, min_size=1.5))
    body.append(m.path(m.lines(GEO["rivers"]["Colorado"] + GEO["rivers"]["Columbia"]
                               + GEO["rivers"]["Rio Grande"] + GEO["rivers"]["Snake"]
                               + GEO["rivers"]["Gila"]), "river"))
    body.append(m.path(m.lines(GEO["borders"]["USA-MEX"]), "border-nat"))
    for lon, lat, s, rot in [(-108.6, 42.6, "ROCKY MOUNTAINS", -62), (-120.0, 38.55, "SIERRA NEVADA", 52),
                             (-121.4, 44.6, "CASCADES", -84)]:
        x, y = m.xy(lon, lat)
        body.append(text(x, y, s, "lb-mtn", "middle", f' transform="rotate({rot} {x:.1f} {y:.1f})"'))
    for lon, lat, lines in [(-116.4, 40.6, ["GREAT BASIN", "DESERT", "bristlecone pines"]),
                            (-116.3, 34.75, ["MOJAVE", "Joshua trees"]),
                            (-112.6, 32.4, ["SONORAN", "saguaros"]),
                            (-105.6, 31.6, ["CHIHUAHUAN"])]:
        x, y = m.xy(lon, lat)
        body.append(text(x, y, lines[0], "lb-desert", "middle"))
        body += [text(x, y + 13 * i, l, "lb-desert2" if i == len(lines) - 1 and l.islower() else "lb-desert", "middle")
                 for i, l in enumerate(lines[1:], 1)]
    for name, dx, dy, anchor in [("Mount Whitney", -8, 16, "end"), ("Mount Elbert", 8, 4, "start"),
                                 ("Mount Rainier", 9, 4, "start")]:
        p = GEO["peaks"][name]
        x, y = m.xy(p["lon"], p["lat"])
        body.append(peak(x, y) + text(x + dx, y + dy, name, "lb-pk", anchor))
    body.append(callout(m, -122.19, 46.19, ["Mount Saint Helens", "(active volcano)"], -12, 22, "end", "lb-pk", 12, "peak"))
    body.append(callout(m, -116.87, 36.25, ["Death Valley:", "86 m below sea level"], 36, -44, "start", "lb-pk", 12, "dot"))
    body.append(callout(m, -112.1, 36.15, ["Grand Canyon"], 8, -26, "start", "lb-pk", 12, "dot"))
    body.append(callout(m, -114.74, 36.02, ["Hoover Dam,", "Lake Mead"], 40, 8, "start", "lb-s", 12, "dot"))
    body.append(callout(m, -122.1, 42.94, ["Crater Lake: deepest", "lake in the USA"], -14, 26, "end", "lb-s", 12, "dot"))
    body.append(callout(m, -120.03, 39.1, ["Lake Tahoe"], 30, -18, "start", "lb-s", 12, None))
    body.append(callout(m, -112.5, 41.1, ["Great Salt Lake"], 30, -30, "start", "lb-s", 12, None))
    x, y = m.xy(-110.0, 38.35)
    body.append(text(x, y, "Colorado", "lb-river", "middle",
                     f' transform="rotate(-40 {x:.1f} {y:.1f})"'))
    body.append(at(m, -123.4, 47.0, "Columbia", "lb-river", "end", dx=-4))
    body.append(at(m, -106.9, 34.0, "Rio Grande", "lb-river", "start", dx=6))
    x, y = m.xy(-124.6, 36.0)
    body.append(multiline(x, y, ["PACIFIC", "OCEAN"], "lb-sea", "middle", 15))
    label = ("Map of the western USA: the Cascades, Sierra Nevada and Rocky Mountains; the Great "
             "Basin, Mojave, Sonoran and Chihuahuan Deserts; the Colorado River and the Grand "
             "Canyon; Death Valley, Mount Whitney and Mount Saint Helens.")
    return figure(svg(W, H, "".join(body), label),
                  "The four big US deserts are all in the West. The Great Basin lies between the "
                  "Sierra Nevada and the Rockies; Death Valley, the lowest point, is close to "
                  "Mount Whitney, the highest in the lower 48.", minw=480)


# ---------------------------------------------------------------- F8: peaks
PEAKS = [("Denali", 6190, "Alaska Range", "usa"), ("Mount Logan", 5959, "Saint Elias Mts.", "can"),
         ("Whitney", 4421, "Sierra Nevada", "usa"), ("Elbert", 4401, "Rockies", "usa"),
         ("Rainier", 4392, "Cascades", "usa"), ("Chamberlin", 2749, "Brooks Range", "usa"),
         ("Rysy" + X, 2499, "Tatras, Poland", "pl"), ("Mitchell", 2037, "Appalachians", "usa"),
         ("Marcy", 1629, "Adirondacks", "usa")]


def peaks_chart():
    W, H = 760, 330
    x0, base, top, vmax = 56, 262, 34, 6500
    sy = (base - top) / vmax
    out = []
    for v in range(0, 7000, 1000):
        y = base - v * sy
        out.append(f'<path class="grid" d="M{x0},{y:.1f} {W - 8},{y:.1f}"/>')
        out.append(text(x0 - 6, y + 4, f"{v:,} m", "lb-tick", "end"))
    step = (W - x0 - 20) / len(PEAKS)
    for i, (name, h, rng, kind) in enumerate(PEAKS):
        cx = x0 + step * (i + .5)
        y = base - h * sy
        half = step * .62
        out.append(f'<path class="pk-{kind}" d="M{cx - half:.1f},{base} {cx:.1f},{y:.1f} '
                   f'{cx + half:.1f},{base}Z"><title>{name.replace(X, "")}: {h:,} m '
                   f'({round(h / 0.3048):,} ft)</title></path>')
        out.append(multiline(cx, y - 20, [name, f"{h:,} m"], "lb-pk", "middle", 12))
        out.append(multiline(cx, base + 18, rng.split(", ") if ", " in rng else [rng],
                             "lb-tiny", "middle", 11))
    out.append(f'<path class="axis" d="M{x0},{base} {W - 8},{base}"/>')
    out.append(legend_inline(W - 300, 14, [("pk-usa", "USA"), ("pk-can", "Canada"),
                                           ("pk-pl", "Poland" + X + ", for scale")]))
    label = ("Chart of peak heights: Denali 6,190 m, Mount Logan 5,959 m, Whitney 4,421 m, "
             "Elbert 4,401 m, Rainier 4,392 m, Chamberlin 2,749 m, Rysy 2,499 m, Mitchell "
             "2,037 m, Marcy 1,629 m.")
    return figure(svg(W, H, "".join(out), label, cls="chart"),
                  "The highest peaks, drawn to scale, with the range each one tops. Whitney, "
                  "Elbert and Rainier are almost the same height.", minw=600)


def legend_inline(x, y, items):
    out, cx = [], x
    for cls, lab in items:
        out.append(f'<rect class="{cls}" x="{cx:.1f}" y="{y - 9}" width="12" height="12" rx="3"/>')
        out.append(text(cx + 17, y + 1, lab, "lb-s"))
        cx += 17 + 7.2 * len(lab.replace(X, "*")) + 16
    return "".join(out)


# ---------------------------------------------------------------- F9: cross-section
def cross_section():
    W, H = 760, 320
    sea = 210                                     # y of sea level
    k = 0.024                                     # px per metre (vertical, exaggerated)

    def y(m_):
        return sea - m_ * k
    prof = [(0, -200), (88, -60), (96, 0), (112, 300), (130, 900), (150, 400), (168, 60),
            (230, 60), (262, 900), (286, 2500), (300, 4421), (312, 2600), (326, 400),
            (338, -86), (350, 300), (372, 1900), (392, 1300), (420, 1500), (440, 2100),
            (460, 1400), (490, 1600), (520, 1900), (548, 3200), (572, 3900), (586, 4401),
            (600, 3700), (624, 2400), (650, 1700), (700, 1200), (760, 700)]
    ground = "M" + " ".join(f"{x},{y(h):.1f}" for x, h in prof) + f" {W},{H} 0,{H}Z"
    out = [f'<rect class="sky" width="{W}" height="{H}" rx="12"/>',
           f'<path class="sea-x" d="M0,{sea} 96,{sea} 96,{H} 0,{H}Z"/>',
           f'<path class="ground" d="{ground}"/>',
           f'<path class="sealevel" d="M0,{sea} {W},{sea}"/>',
           text(W - 8, sea - 5, "sea level", "lb-tiny", "end")]
    # clouds, wind, rain
    for cx, cy in [(130, 62), (205, 52), (255, 74)]:
        out.append(f'<path class="cloud" d="M{cx - 26},{cy} a14,14 0 0 1 14,-14 a18,18 0 0 1 '
                   f'32,4 a12,12 0 0 1 6,22 h-44 a10,10 0 0 1 -8,-12Z"/>')
    for cx in range(214, 290, 12):
        out.append(f'<path class="rain" d="M{cx},{86} {cx - 6},{y(1600) if cx > 262 else 150:.0f}"/>')
    out.append('<path class="wind" d="M20,48 C70,40 110,40 150,44"/><path class="wind-head" d="M150,44 l-9,-5 1,9z"/>')
    out.append(multiline(16, 26, ["wet winds from the Pacific"], "lb-s"))
    out.append(multiline(436, 112, ["Great Basin Desert:", "little rain, because the",
                                     "Sierra Nevada blocks", "the wet winds"], "lb-s", "middle", 14))
    # continental divide
    cx, cy = 586, y(4401)
    out.append(f'<path class="divide" d="M{cx},{cy - 6} {cx},{cy - 56}"/>')
    out.append(multiline(cx, cy - 76, ["Continental Divide"], "lb-b", "middle"))
    out.append(f'<path class="flow" d="M{cx - 6},{cy - 40} C{cx - 40},{cy - 40} {cx - 60},{cy - 26} {cx - 78},{cy - 10}"/>'
               f'<path class="flow-head" d="M{cx - 78},{cy - 10} l2,-10 8,6z"/>')
    out.append(f'<path class="flow" d="M{cx + 6},{cy - 40} C{cx + 40},{cy - 40} {cx + 60},{cy - 26} {cx + 78},{cy - 10}"/>'
               f'<path class="flow-head" d="M{cx + 78},{cy - 10} l-2,-10 -8,6z"/>')
    out.append(multiline(cx - 86, cy - 44, ["water flows west", "to the Pacific"], "lb-s", "end", 13))
    out.append(multiline(W - 8, cy - 44, ["water flows east to the", "Atlantic (Gulf of Mexico)"], "lb-s", "end", 13))
    # names
    for x, h, s, a in [(300, 4421, "Mount Whitney 4,421 m", "middle"),
                       (338, -86, "Death Valley −86 m", "start")]:
        out.append(peak(x, y(h) - 2, 5) if h > 0 else dot(x, y(h), 3.4))
    out.append(text(300, y(4421) - 14, "Mount Whitney 4,421 m", "lb-pk", "end"))
    out.append(text(344, y(-86) + 18, "Death Valley −86 m", "lb-pk", "start"))
    for x, s in [(48, "PACIFIC"), (200, "California"), (300, "SIERRA NEVADA"),
                 (450, "GREAT BASIN"), (586, "ROCKY MOUNTAINS"), (705, "GREAT PLAINS")]:
        out.append(text(x, H - 14, s, "lb-xs", "middle"))
    out.append(text(W - 8, H - 34, "west → east, not to scale", "lb-tiny", "end"))
    label = ("Cross-section of the western USA from the Pacific to the Great Plains: wet winds "
             "rain on the Sierra Nevada, the Great Basin behind it stays dry; on the Rocky "
             "Mountains the Continental Divide sends water west to the Pacific and east to the "
             "Atlantic.")
    return figure(svg(W, H, "".join(out), label, cls="chart"),
                  "A walk from the Pacific to the Great Plains. The Sierra Nevada catches the "
                  "rain, so the Great Basin behind it is a desert; on the Rockies, the "
                  "Continental Divide decides which ocean a raindrop reaches.", minw=600)


# ---------------------------------------------------------------- F10: rivers and lakes
RIVERS_MAIN = ["Missouri", "Mississippi", "Yukon", "Rio Grande", "St. Lawrence", "Arkansas",
               "Colorado", "Ohio", "Red", "Columbia", "Hudson", "Mackenzie", "Fraser"]


def waters_map():
    W, H = 760, 600
    m = na_view((0, 0, W, H))
    body = [frame(W, H), context_land(m), land(m, "land1", "land1"), lakes(m)]
    red = [l for l in GEO["rivers"]["Red"] if min(la for _, la in l) < 36]
    minor = GEO["rivers"]["Slave"] + GEO["rivers"]["Peace"] + GEO["rivers"]["Finlay"] + \
        GEO["rivers"]["Teslin"] + GEO["rivers"]["Thompson"] + GEO["rivers"]["Snake"] + \
        GEO["rivers"]["Platte"] + GEO["rivers"]["North Platte"] + GEO["rivers"]["Tennessee"] + \
        GEO["rivers"]["Prairie Dog Town Fork Red"] + GEO["rivers"]["Pecos"] + GEO["rivers"]["Gila"]
    body.append(m.path(m.lines(minor), "river thin"))
    main = [l for r in RIVERS_MAIN if r != "Red" for l in GEO["rivers"][r]] + red
    body.append(m.path(m.lines(main), "river"))
    body.append(m.path(m.lines(GEO["borders"]["USA-CAN"]), "border-nat"))
    for lon, lat, s, a, rot in [(-104.5, 47.6, "Missouri", "middle", 22),
                                (-90.6, 35.5, "Mississippi", "middle", -78),
                                (-84.8, 38.2, "Ohio", "middle", -18),
                                (-96.9, 36.3, "Arkansas", "middle", 28),
                                (-97.6, 33.7, "Red", "middle", 12),
                                (-111.0, 37.3, "Colorado", "middle", 52),
                                (-101.5, 29.3, "Rio Grande", "middle", 40),
                                (-119.4, 46.6, "Columbia", "middle", 0),
                                (-152, 65.2, "Yukon", "middle", 0),
                                (-127.5, 66.4, "Mackenzie", "middle", -50),
                                (-122.6, 52.6, "Fraser", "middle", -70),
                                (-69.4, 48.6, "St. Lawrence", "middle", -32),
                                (-73.3, 41.4, "Hudson", "start", 0)]:
        x, y = m.xy(lon, lat)
        tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
        body.append(text(x, y, s, "lb-river", a, tr))
    for lon, lat, lines, dx, dy, a in [
            (-123.4, 65.9, ["Great Bear Lake"], 10, -14, "start"),
            (-114.5, 61.6, ["Great Slave Lake"], 18, 16, "start"),
            (-112.5, 41.1, ["Great Salt Lake"], 26, 22, "start"),
            (-84, 45.5, ["Great Lakes"], -12, -46, "end"),
            (-80.8, 26.95, ["Lake Okeechobee"], 24, 4, "start")]:
        body.append(callout(m, lon, lat, lines, dx, dy, a, "lb-s"))
    body.append(callout(m, -95.2, 47.24, ["Lake Itasca: the", "Mississippi starts here"], -46, -40, "end", "lb-s", 12, "dot"))
    body.append(callout(m, -79.07, 43.08, ["Niagara", "Falls"], -14, 40, "end", "lb-s", 12, "dot"))
    body.append(callout(m, -65.5, 45.1, ["Bay of Fundy:", "highest tides"], 34, 6, "start", "lb-s", 12, "dot"))
    body.append(callout(m, -121.58, 50.23, ["Lytton: the Thompson", "meets the Fraser"], -48, -26, "end", "lb-s", 12, "dot"))
    body.append(m.path(m.lines([ST_LAWRENCE]), "river"))
    for lon, lat, lines in [(-140, 36, ["PACIFIC", "OCEAN"]), (-55, 33, ["ATLANTIC", "OCEAN"]),
                            (-140, 77.5, ["ARCTIC OCEAN"]), (-90, 25.3, ["Gulf of", "Mexico"]),
                            (-176, 58, ["Bering", "Sea"])]:
        x, y = m.xy(lon, lat)
        body.append(multiline(x, y, lines, "lb-sea", "middle", 15))
    label = ("Map of rivers and lakes: the Missouri, Mississippi, Ohio, Arkansas, Red, Colorado, "
             "Rio Grande, Columbia, Hudson and St. Lawrence in the USA; the Yukon across Alaska; "
             "the Mackenzie and Fraser in Canada; the Great Lakes, Great Salt Lake, Great Bear "
             "and Great Slave Lakes.")
    return figure(svg(W, H, "".join(body), label),
                  "Where each river flows. The Missouri joins the Mississippi, which runs south "
                  "into the Gulf of Mexico; the Yukon runs to the Bering Sea, the Mackenzie north "
                  "to the Arctic Ocean, the St. Lawrence from the Great Lakes to the Atlantic.",
                  minw=560)


def rivers_chart():
    rows = [("Mackenzie", 4241, "can"), ("Missouri", 4088, "usa"), ("Mississippi", 3766, "usa"),
            ("Yukon", 3187, "usa"), ("Rio Grande", 3058, "usa"), ("St. Lawrence", 3058, "usa"),
            ("Arkansas", 2350, "usa"), ("Colorado", 2334, "usa"), ("Atchafalaya", 2285, "usa"),
            ("Ohio", 2108, "usa"), ("Red", 2076, "usa"), ("Columbia", 1996, "usa"),
            ("Wisła" + X, 1047, "pl"), ("Hudson", 507, "usa")]
    W, gap, th, lab_w = 760, 23, 16, 110
    H = 40 + gap * len(rows) + 12
    bw = W - lab_w - 110
    out = []
    for v in range(0, 5000, 1000):
        x = lab_w + bw * v / 4500
        out.append(f'<path class="grid" d="M{x:.1f},30 {x:.1f},{H - 12}"/>')
        out.append(text(x, 22, f"{v:,} km", "lb-tick", "middle"))
    for i, (name, km, kind) in enumerate(rows):
        y = 36 + i * gap
        L = bw * km / 4500
        out.append(text(lab_w - 8, y + th - 3, name, "lb", "end"))
        out.append(bar(lab_w, y, L, th, f"pk-{kind}"))
        mi_ = f"{round(km / 1.609344):,} mi" if kind != "pl" else ""
        out.append(text(lab_w + L + 6, y + th - 3, f"{km:,} km" + (f"  ({mi_})" if mi_ else ""), "lb-s"))
    out.append(legend_inline(W - 310, H - 2, [("pk-usa", "USA"), ("pk-can", "Canada"),
                                              ("pk-pl", "Poland" + X + ", for scale")]))
    label = "Bar chart of river lengths: " + ", ".join(f"{n.replace(X, '')} {k:,} km" for n, k, _ in rows) + "."
    return figure(svg(W, H + 10, "".join(out), label, cls="chart"),
                  "River lengths. The Missouri is the longest river in the USA; Canada's "
                  "Mackenzie river system is longer still.", minw=600)


def great_lakes_map():
    W, H = 760, 440
    m = Map(LAEA(-82, 45), bbox(-92.6, 40.6, -71.2, 49.2), (0, 0, W, H), pad=4)
    body = [frame(W, H), context_land(m)]
    us = [p for s, d in GEO["states"].items() if d["country"] == "USA" for p in d["geom"]]
    ca = [p for s, d in GEO["states"].items() if d["country"] == "CAN" for p in d["geom"]]
    body += [m.path(m.polys(us), "usa"), m.path(m.polys(ca), "can")]
    big = ["Lake Superior", "Lake Michigan", "Lake Huron", "Lake Erie", "Lake Ontario",
           "Lake Saint Clair"]
    body.append(lakes(m, min_size=2))
    body.append(m.path("".join(m.polys(GEO["lakes"][n]) for n in big), "lake-big"))
    body.append(m.path("".join(m.polys(GEO["lakes"]["Lake Michigan"])), "lake-mi"))
    body.append(m.path(m.lines([ST_LAWRENCE] + GEO["rivers"]["Hudson"]
                               + GEO["rivers"]["Niagara"]), "river"))
    body.append(m.path(m.lines(GEO["borders"]["USA-CAN"]), "border-nat"))
    canal = [(-78.88, 42.89), (-77.6, 43.12), (-76.15, 43.05), (-75.23, 43.1), (-74.2, 42.85),
             (-73.75, 42.68)]
    body.append(m.path(m.lines([canal]), "canal"))
    x, y = m.xy(-75.4, 43.15)
    body.append(text(x, y - 8, "Erie Canal (1825)", "lb-b", "middle"))
    x, y = m.xy(-73.9, 41.75)
    body.append(text(x - 6, y, "Hudson", "lb-river", "end"))
    for lon, lat, letter, name, area in [(-88.0, 47.6, "S", "Superior", "31,700 sq mi"),
                                         (-87.0, 43.4, "M", "Michigan", "22,300 sq mi"),
                                         (-82.4, 44.9, "H", "Huron", "23,000 sq mi"),
                                         (-81.3, 42.2, "E", "Erie", "9,910 sq mi"),
                                         (-77.9, 43.62, "O", "Ontario", "7,340 sq mi")]:
        x, y = m.xy(lon, lat)
        body.append(text(x, y, letter, "lb-letter", "middle"))
        body.append(text(x, y + 16, name, "lb-lake", "middle"))
    for name, adm1, dx, dy, a in [("Chicago", "Illinois", -7, 4, "end"),
                                  ("Milwaukee", "Wisconsin", -7, 4, "end"),
                                  ("Cleveland", "Ohio", 6, 14, "start"),
                                  ("Buffalo", "New York", -6, 16, "end"),
                                  ("Toronto", "Ontario", -6, -7, "end")]:
        x, y = m.xy(*place(name, adm1))
        body.append(dot(x, y, 3.2) + text(x + dx, y + dy, name, "lb", a))
    body.append(callout(m, -79.07, 43.08, ["Niagara Falls"], 34, 40, "start", "lb-b", 13, "dot"))
    body.append(callout(m, -86.7, 41.9, ["Lake Michigan: the only one", "entirely in the USA"],
                        -36, 30, "end", "lb-b", 14))
    x, y = m.xy(-72.3, 46.85)
    body.append(text(x, y, "St. Lawrence → Atlantic", "lb-river", "middle",
                     f' transform="rotate(-36 {x:.1f} {y:.1f})"'))
    body.append(at(m, -84.5, 49.0, "CANADA", "lb-mid lb-m"))
    body.append(at(m, -89.6, 44.1, "USA", "lb-mid lb-m"))
    body.append(f'<g transform="translate({W - 252},{H - 52})"><rect class="legend-bg" width="242" '
                f'height="42" rx="8"/>' + text(121, 17, "west to east: S M H E O", "lb-b", "middle")
                + text(121, 33, "Super Man Helps Every One", "lb-s", "middle") + "</g>")
    label = ("Map of the Great Lakes from west to east: Superior, Michigan, Huron, Erie, "
             "Ontario; Lake Michigan lies entirely in the USA; Niagara Falls between Erie and "
             "Ontario; the St. Lawrence runs to the Atlantic.")
    return figure(svg(W, H, "".join(body), label),
                  "The Great Lakes from west to east. Water flows from Superior down through "
                  "the lakes, over Niagara Falls into Lake Ontario, and out along the St. "
                  "Lawrence to the Atlantic.", minw=560)


# ---------------------------------------------------------------- F13: tides
def tide_chart():
    W, H = 760, 260
    x0, x1, top, base = 56, 640, 26, 214
    sy = (base - top) / 17
    pts = []
    for i in range(241):
        t = i / 10
        lvl = 8 + 8 * math.cos(2 * math.pi * (t - 3) / 12.42)
        pts.append((x0 + (x1 - x0) * t / 24, base - lvl * sy))
    out = []
    for v in range(0, 17, 4):
        y = base - v * sy
        out.append(f'<path class="grid" d="M{x0},{y:.1f} {x1},{y:.1f}"/>' + text(x0 - 6, y + 4, f"{v} m", "lb-tick", "end"))
    for h in range(0, 25, 6):
        x = x0 + (x1 - x0) * h / 24
        out.append(text(x, base + 18, f"{h} h", "lb-tick", "middle"))
    area = fmt(pts + [(x1, base), (x0, base)], True)
    out.append(f'<path class="tide-fill" d="{area}"/><path class="tide-line" d="{fmt(pts, False)}"/>')
    for t, lab in [(3, "high tide"), (15.42, "high tide")]:
        x = x0 + (x1 - x0) * t / 24
        out.append(text(x, top - 6 + 2, lab, "lb-s", "middle"))
    for t, lines in [(9.21, ["low tide: walk", "on the seabed"]), (21.63, ["low tide"])]:
        x = x0 + (x1 - x0) * t / 24
        out.append(multiline(x, base - 26, lines, "lb-s", "middle", 13))
    out.append(f'<path class="axis" d="M{x0},{base} {x1},{base}"/>')
    # a five-storey block for scale
    bx, bw = 676, 46
    out.append(f'<rect class="block" x="{bx}" y="{base - 16 * sy:.1f}" width="{bw}" height="{16 * sy:.1f}" rx="2"/>')
    for f in range(5):
        fy = base - (f + 1) * 3.2 * sy
        out.append(f'<path class="floor" d="M{bx},{fy:.1f} {bx + bw},{fy:.1f}"/>')
        for wx in (bx + 8, bx + 26):
            out.append(f'<rect class="window" x="{wx}" y="{fy + 4:.1f}" width="12" height="{3.2 * sy - 9:.1f}" rx="1"/>')
    out.append(multiline(bx + bw / 2, base + 18, ["a 5-storey", "block: 16 m"], "lb-tiny", "middle", 11))
    out.append(f'<path class="bracket" d="M{x1 + 14},{top + sy:.1f} h6 v{(base - top) - sy:.1f} h-6"/>')
    out.append(multiline(x1 + 24, base - 8 * sy - 6, ["up to", "16 m"], "lb-b", "start", 14))
    label = ("Chart of the water level in the Bay of Fundy over 24 hours: two high tides and two "
             "low tides, rising and falling by up to 16 metres, as tall as a five-storey block.")
    return figure(svg(W, H, "".join(out), label, cls="chart"),
                  "The Bay of Fundy in one day: the sea comes in and goes out twice, and the "
                  "water rises and falls by up to 16 m.", minw=600)


# ---------------------------------------------------------------- F14: temperatures
def temperature_chart():
    W, H = 760, 230
    x0, x1, yb = 30, 730, 112
    lo, hi = -70, 60

    def X_(c):
        return x0 + (x1 - x0) * (c - lo) / (hi - lo)
    out = [f'<defs><linearGradient id="tgrad" x1="0" x2="1"><stop offset="0" stop-color="var(--cold)"/>'
           f'<stop offset="{(0 - lo) / (hi - lo):.3f}" stop-color="var(--neutral)"/>'
           f'<stop offset="1" stop-color="var(--hot2)"/></linearGradient></defs>',
           f'<rect x="{x0}" y="{yb - 9}" width="{x1 - x0}" height="18" rx="9" fill="url(#tgrad)"/>']
    for c in range(-70, 61, 10):
        x = X_(c)
        out.append(f'<path class="tick" d="M{x:.1f},{yb - 13} {x:.1f},{yb - 9}"/>' + text(x, yb - 17, f"{c}°C", "lb-tick", "middle"))
    for f in range(-80, 141, 20):
        c = (f - 32) / 1.8
        x = X_(c)
        out.append(f'<path class="tick" d="M{x:.1f},{yb + 9} {x:.1f},{yb + 13}"/>' + text(x, yb + 25, f"{f}°F", "lb-tick", "middle"))
    marks = [(-63, ["Snag, Yukon, 1947:", "−63°C / −81°F"], "below", "b"),
             (56.7, ["Death Valley, 1913" + X + ":", "56.7°C / 134°F"], "above", "b"),
             (-41, ["Poland's coldest" + X + ":", "−41°C"], "above", "m"),
             (40.5, ["Poland's hottest" + X + ":", "40.5°C, 2026"], "below", "m"),
             (-30, ["northern Canada", "in winter: below −30°C"], "below", "m"),
             (0, ["water freezes:", "0°C / 32°F"], "above", "m")]
    for c, lines, side, kind in marks:
        x = X_(c)
        anchor = "end" if c > 50 else "start" if c < -60 else "middle"
        tx = x + (8 if anchor == "end" else -8 if anchor == "start" else 0)
        if side == "above":
            out.append(f'<path class="mark-line" d="M{x:.1f},{yb - 28} {x:.1f},{yb - 46}"/>')
            out.append(multiline(tx, yb - 66, lines, "lb-b" if kind == "b" else "lb-s", anchor, 13))
        else:
            out.append(f'<path class="mark-line" d="M{x:.1f},{yb + 32} {x:.1f},{yb + 52}"/>')
            out.append(multiline(tx, yb + 66, lines, "lb-b" if kind == "b" else "lb-s", anchor, 13))
        out.append(f'<circle class="mark-dot" cx="{x:.1f}" cy="{yb}" r="5"/>')
    label = ("Temperature scale from minus 70 to plus 60 degrees Celsius: Snag minus 63, "
             "Death Valley plus 56.7, Poland's records minus 41 and plus 40.5.")
    return figure(svg(W, H, "".join(out), label, cls="chart"),
                  "The two records on one thermometer, in °C above and °F below. Death Valley "
                  "has been 16 degrees hotter than Poland's hottest day, Snag 22 degrees colder "
                  "than Poland's coldest" + XH + ".", minw=600)


# ---------------------------------------------------------------- F15: climate
CLIMATE = {"Northeast": "c-cont", "Midwest": "c-cont", "Southeast": "c-sub",
           "Southwest": "c-semi", "West": "c-west"}


def climate_map():
    W, H = 760, 600
    m = na_view((0, 0, W, H))
    body = [frame(W, H), context_land(m)]
    for st, d in GEO["states"].items():
        if st in ("Hawaii", "District of Columbia"):
            continue
        if d["country"] == "USA":
            cls = CLIMATE[STATE_REGION[st]]
        else:
            cls = "c-cold" if st in CA_REGIONS["North"] else "c-can"
        body.append(m.path(m.polys(d["geom"]), f"st {cls}"))
    body.append(lakes(m))
    body.append(m.path(m.lines(GEO["borders"]["USA-CAN"]), "border-nat"))
    body.append(callout(m, -72.8, 43.6, ["humid continental:", "snowy winters"], 52, -18, "start", "lb-s", 13, None))
    for lon, lat, lines in [(-93, 44.5, ["humid continental:", "snow in winter"]),
                            (-86, 33, ["humid subtropical:", "hot summers"]),
                            (-104.5, 33, ["semiarid,", "dry"]),
                            (-116, 40.5, ["mountains: alpine", "deserts: dry"]),
                            (-112, 66.5, ["very cold, long snowy winters;", "parts frozen all year"]),
                            (-96, 54, ["warm summers in the south"])]:
        x, y = m.xy(lon, lat)
        body.append(multiline(x, y, lines, "lb-s", "middle", 13))
    body.append(callout(m, -121.5, 36.5, ["California coast:", "Mediterranean"], -30, 28, "end", "lb-s", 13, None))
    for lon, lat in [(-79, 30.5), (-88.5, 27.5)]:
        x, y = m.xy(lon, lat)
        body.append(hurricane(x, y))
    body.append(callout(m, -77.5, 28.6, ["hurricanes in summer", "and autumn"], 30, 30, "start", "lb-s", 13, None))
    body.append(callout(m, -116.87, 36.25, ["Death Valley:", "56.7°C"], -40, 46, "end", "lb-b", 13, "star"))
    body.append(callout(m, -140.4, 62.4, ["Snag:", "−63°C"], -30, 26, "end", "lb-b", 13, "star"))
    x, y = m.xy(-108, 70)
    body.append(aurora(x, y) + text(x + 54, y + 4, "Northern Lights", "lb-s"))
    label = ("Climate map: humid continental in the Northeast and Midwest, humid subtropical in "
             "the Southeast with hurricanes, semiarid in the Southwest, mixed in the West with a "
             "Mediterranean California coast; very cold in northern Canada.")
    return figure(svg(W, H, "".join(body), label),
                  "Climate by region. The Northeast and the Midwest share one climate (the same "
                  "colour); hurricanes hit the Southeast; the far north of Canada is frozen for "
                  "much of the year.", minw=560)


def hurricane(x, y, r=9):
    return (f'<g class="hurr" transform="translate({x:.1f},{y:.1f})"><circle r="3"/>'
            f'<path d="M0,-3 C{r},-{r} {r * 1.6},-2 {r * 1.4},4"/><path d="M0,3 C-{r},{r} -{r * 1.6},2 -{r * 1.4},-4"/></g>')


def aurora(x, y):
    return (f'<path class="aurora" d="M{x - 40},{y + 6} C{x - 26},{y - 12} {x - 10},{y + 10} '
            f'{x + 4},{y - 6} S{x + 30},{y + 4} {x + 46},{y - 8}"/>')


# ---------------------------------------------------------------- F16: flags
def flags_figure():
    W, H = 760, 250
    # USA: 13 stripes, 50 stars in 9 rows of 6 and 5
    fx, fy, fw = 20, 30, 300
    fh = fw / 1.9
    sh = fh / 13
    out = [f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh:.1f}" fill="#fff"/>']
    for i in range(0, 13, 2):
        out.append(f'<rect class="us-red" x="{fx}" y="{fy + i * sh:.1f}" width="{fw}" height="{sh:.2f}"/>')
    cw, ch = fw * 0.4, sh * 7
    out.append(f'<rect class="us-blue" x="{fx}" y="{fy}" width="{cw:.1f}" height="{ch:.1f}"/>')
    for row in range(9):
        n = 6 if row % 2 == 0 else 5
        for col in range(n):
            sx = fx + cw * ((col * 2 + (1 if row % 2 == 0 else 2)) / 12)
            sy = fy + ch * ((row + 1) / 10)
            out.append(star(sx, sy, 3.4, "us-star"))
    out.append(f'<rect class="flag-edge" x="{fx}" y="{fy}" width="{fw}" height="{fh:.1f}"/>')
    out.append(leader(fx + fw + 2, fy + fh * .7, fx + fw + 24, fy + fh * .7)
               + multiline(fx + fw + 28, fy + fh * .7 - 4, ["13 stripes:", "the 13 colonies"], "lb-s", "start", 13))
    out.append(leader(fx + cw * .5, fy + ch + 2, fx + cw * .5, fy + fh + 26)
               + multiline(fx + cw * .5, fy + fh + 40, ["50 stars: the 50 states"], "lb-s", "middle"))
    out.append(text(fx, fy - 10, "USA", "lb-b"))
    # Canada: red-white-red, the maple leaf
    gx, gy, gw = 460, 30, 280
    gh = gw / 2
    s = gw / 9600
    out.append(f'<g transform="translate({gx},{gy}) scale({s:.5f})">'
               '<path fill="#fff" d="M0 0h9600v4800H0z"/>'
               '<path class="ca-red" d="M0 0h2400v4800H0zM7200 0h2400v4800H7200z"/>'
               '<path class="ca-red" d="m4890 4430-45-863a95 95 0 0 1 111-98l859 151-116-320a65 65 0 0 1 '
               '20-73l941-762-212-99a65 65 0 0 1-34-79l186-572-542 115a65 65 0 0 1-73-38l-105-247-423 '
               '454a65 65 0 0 1-111-57l204-1052-327 189a65 65 0 0 1-91-27l-332-652-332 652a65 65 0 0 '
               '1-91 27l-327-189 204 1052a65 65 0 0 1-111 57l-423-454-105 247a65 65 0 0 1-73 38l-542-'
               '115 186 572a65 65 0 0 1-34 79l-212 99 941 762a65 65 0 0 1 20 73l-116 320 859-151a95 95 '
               '0 0 1 111 98l-45 863z"/></g>')
    out.append(f'<rect class="flag-edge" x="{gx}" y="{gy}" width="{gw}" height="{gh:.1f}"/>')
    out.append(text(gx, gy - 10, "Canada", "lb-b"))
    out.append(leader(gx + gw / 2, gy + gh * .82, gx + gw / 2, gy + gh + 26)
               + multiline(gx + gw / 2, gy + gh + 40, ["the maple leaf; red and white"], "lb-s", "middle"))
    label = ("The flags: the USA's with 13 red and white stripes and 50 white stars on blue; "
             "Canada's, red and white with a red maple leaf.")
    return figure(svg(W, H, "".join(out), label, cls="chart"), "", minw=560)


# ---------------------------------------------------------------- F19: trees
def trees_chart():
    W, H = 760, 340
    x0, base, top = 64, 300, 24
    sy = (base - top) / 120
    out = []
    for v in range(0, 121, 20):
        y = base - v * sy
        out.append(f'<path class="grid" d="M{x0},{y:.1f} {W - 10},{y:.1f}"/>' + text(x0 - 6, y + 4, f"{v} m", "lb-tick", "end"))
    out.append(f'<path class="axis" d="M{x0},{base} {W - 10},{base}"/>')
    # person
    px = 110
    out.append(f'<path class="person" d="M{px},{base} v{-1.8 * sy:.1f}"/>'
               + text(px, base - 1.8 * sy - 8, "you: 1.8 m", "lb-s", "middle"))
    # saguaro 18 m
    sx, h = 210, 18 * sy
    out.append(f'<path class="cactus" d="M{sx - 4},{base} v{-h:.1f} a4,4 0 0 1 8,0 v{h:.1f}z'
               f'M{sx - 4},{base - h * .45:.1f} h-8 v{-h * .3:.1f} a3,3 0 0 1 6,0 v{h * .18:.1f} h2z'
               f'M{sx + 4},{base - h * .55:.1f} h8 v{-h * .28:.1f} a3,3 0 0 1 -6,0 v{-h * .0:.1f}z"/>')
    out.append(multiline(sx, base - h - 22, ["saguaro:", "over 18 m (60 ft)"], "lb-s", "middle", 13))
    # giant sequoia 82 m
    gx, h = 380, 82 * sy
    out.append(f'<path class="trunk" d="M{gx - 9},{base} L{gx - 5},{base - h * .45:.1f} L{gx + 5},{base - h * .45:.1f} L{gx + 9},{base}Z"/>'
               f'<path class="crown" d="M{gx},{base - h:.1f} C{gx + 30},{base - h * .85:.1f} {gx + 34},{base - h * .5:.1f} {gx + 22},{base - h * .4:.1f}'
               f' L{gx - 22},{base - h * .4:.1f} C{gx - 34},{base - h * .5:.1f} {gx - 30},{base - h * .85:.1f} {gx},{base - h:.1f}Z"/>')
    out.append(multiline(gx, base - h - 22, ["giant sequoia:", "up to 82 m (270 ft)"], "lb-s", "middle", 13))
    # coast redwood 116 m
    rx, h = 560, 116 * sy
    out.append(f'<path class="trunk" d="M{rx - 6},{base} L{rx - 3},{base - h * .4:.1f} L{rx + 3},{base - h * .4:.1f} L{rx + 6},{base}Z"/>'
               f'<path class="crown" d="M{rx},{base - h:.1f} L{rx + 16},{base - h * .55:.1f} L{rx + 13},{base - h * .36:.1f}'
               f' L{rx - 13},{base - h * .36:.1f} L{rx - 16},{base - h * .55:.1f}Z"/>')
    out.append(multiline(rx + 24, base - h + 8, ["coast redwood: the tallest", "living things, up to 116 m" + X], "lb-s", "start", 13))
    label = ("Chart of heights: a person 1.8 m, a saguaro over 18 m, a giant sequoia up to 82 m, "
             "a coast redwood up to 116 m.")
    return figure(svg(W, H, "".join(out), label, cls="chart"),
                  "How tall, drawn to scale. Giant sequoias are the largest trees by volume, "
                  "coast redwoods the tallest.", minw=560)


def ages_axis():
    W, H = 760, 220
    x0, x1 = 30, 730
    lo, hi = -3500, 2026

    def X_(yr):
        return x0 + (x1 - x0) * (yr - lo) / (hi - lo)
    out = []
    ya = 150
    out.append(f'<path class="axis" d="M{x0},{ya} {x1},{ya}"/>')
    for yr, lab in [(-3000, "3000 BC"), (-2000, "2000 BC"), (-1000, "1000 BC"), (0, "AD 1"),
                    (1000, "1000"), (2000, "2000")]:
        x = X_(yr)
        out.append(f'<path class="tick" d="M{x:.1f},{ya} {x:.1f},{ya + 5}"/>' + text(x, ya + 18, lab, "lb-tick", "middle"))
    for yr0, y, cls, lines in [(-2975, 40, "pk-usa", "bristlecone pine: over 5,000 years old"),
                              (-975, 80, "pk-can", "giant sequoia: over 3,000 years old")]:
        x = X_(yr0)
        out.append(f'<path class="{cls}" d="M{x:.1f},{y} H{x1 - 4} a4,4 0 0 1 4,4 v8 a4,4 0 0 1 -4,4 H{x:.1f}Z"/>')
        out.append(f'<path class="{cls} fade" d="M{x - 30:.1f},{y} H{x:.1f} v16 H{x - 30:.1f}Z"/>')
        out.append(text(x + 6, y - 6, lines, "lb-b"))
    for yr, lines, dy in [(-2600, ["pyramids of Giza" + X], 0), (-753, ["Rome founded" + X], 0),
                          (966, ["Baptism of Poland" + X], 0), (1492, ["Columbus reaches America" + X], 16)]:
        x = X_(yr)
        out.append(f'<path class="mark-line" d="M{x:.1f},{ya - 4} {x:.1f},{ya - 22 - dy}"/>')
        out.append(f'<circle class="mark-dot-s" cx="{x:.1f}" cy="{ya}" r="3.5"/>')
        out.append(text(x, ya - 26 - dy, lines[0], "lb-tiny", "middle" if yr < 1400 else "end"))
    out.append(text(x1, ya + 34, "today", "lb-tiny", "end"))
    label = ("Time axis from 3000 BC to today: the oldest bristlecone pines started growing "
             "before 3000 BC, before the pyramids of Giza; the oldest giant sequoias before "
             "1000 BC.")
    return figure(svg(W, H, "".join(out), label, cls="chart"),
                  "How old, on a timeline. A bristlecone pine alive today was already a "
                  "small tree when the pyramids were built" + XH + ".", minw=560)


# ---------------------------------------------------------------- F20: monarch migration
def monarch_map():
    W, H = 420, 420
    m = Map(LAEA(-88, 34), bbox(-106, 16, -66, 50), (0, 0, W, H), pad=4)
    body = [frame(W, H), context_land(m), land(m, "land1", "land1"), lakes(m, min_size=3)]
    body.append(m.path(m.lines(GEO["borders"]["USA-CAN"] + GEO["borders"]["USA-MEX"]), "border-nat"))
    a = m.xy(-79.5, 44.0)
    b = m.xy(-100.3, 19.6)
    c1 = m.xy(-91, 39)
    c2 = m.xy(-101.5, 29.5)
    body.append(f'<path class="migr" d="M{a[0]:.1f},{a[1]:.1f} C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {b[0]:.1f},{b[1]:.1f}"/>')
    body.append(f'<circle class="migr-end" cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="5"/><circle class="migr-end" cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="5"/>')
    body.append(text(a[0] + 8, a[1] - 10, "southern Ontario", "lb-b"))
    body.append(text(a[0] + 8, a[1] + 4, "and Quebec", "lb-b"))
    body.append(multiline(b[0] + 10, b[1] + 4, ["mountain forests", "of Mexico"], "lb-b", "start", 14))
    mx, my = m.xy(-90, 33)
    body.append(multiline(mx + 18, my, ["every autumn:", "4,000–5,000 km"], "lb-s", "start", 13))
    body.append(at(m, -96, 47, "CANADA", "lb-mid lb-m") if False else "")
    label = ("Map of the monarch butterfly's autumn migration from southern Ontario and Quebec "
             "to the mountain forests of Mexico, 4,000 to 5,000 kilometres.")
    return figure(svg(W, H, "".join(body), label),
                  "The monarch's autumn journey, one of the longest insect migrations.", minw=0,
                  cls="small")


# ---------------------------------------------------------------- F21-23: parks
US_PARKS = [  # NatGeo order; lon, lat, label offset or ("at", lon, lat, anchor) on a leader
    ("Zion", -113.03, 37.30, ("at", -116.2, 38.9, "end")),
    ("Yellowstone", -110.59, 44.60, (10, -4, "start")),
    ("Acadia", -68.21, 44.34, (-4, -14, "middle")),
    ("Yosemite", -119.54, 37.85, ("at", -125.6, 39.6, "end")),
    ("Sequoia", -118.57, 36.49, ("at", -125.4, 37.6, "end")),
    ("Crater Lake", -122.11, 42.94, (-12, 4, "end")),
    ("Grand Canyon", -112.14, 36.10, ("at", -109.6, 34.6, "start")),
    ("Great Smoky Mountains", -83.51, 35.61, (12, 12, "start")),
    ("Death Valley", -116.93, 36.51, ("at", -125.2, 35.6, "end")),
    ("Redwood", -124.00, 41.30, (-12, 4, "end")),
    ("Olympic", -123.60, 47.80, (-12, 4, "end")), ("Grand Teton", -110.70, 43.79, (10, 10, "start")),
    ("Everglades", -80.90, 25.29, (12, 4, "start")), ("Big Bend", -103.25, 29.25, (12, 4, "start")),
    ("Joshua Tree", -115.90, 33.87, ("at", -123.6, 32.9, "end")),
    ("Bryce Canyon", -112.19, 37.59, ("at", -111.2, 40.3, "middle")),
    ("Arches", -109.59, 38.73, (12, 4, "start")), ("Great Sand Dunes", -105.51, 37.73, (12, 4, "start")),
    ("Dry Tortugas", -82.87, 24.63, (-12, 4, "end")), ("Mammoth Cave", -86.10, 37.19, (12, 4, "start")),
]


def us_parks_map():
    W, H = 760, 480
    m = Map(LAEA(-99, 38), bbox(-131.5, 24.3, -67, 49.3), (0, 0, W, H), pad=6)
    body = [frame(W, H), context_land(m)]
    for st, d in GEO["states"].items():
        if d["country"] == "USA":
            body.append(m.path(m.polys(d["geom"]), "st land1"))
    body.append(lakes(m, min_size=3))
    for i, (name, lon, lat, pos) in enumerate(US_PARKS, 1):
        x, y = m.xy(lon, lat)
        if pos[0] == "at":
            tx, ty = m.xy(pos[1], pos[2])
            ex = tx + (3 if pos[3] == "end" else -3 if pos[3] == "start" else 0)
            body.append(leader(x, y, ex, ty - 4) + text(tx, ty, name, "lb-park", pos[3]))
        else:
            dx, dy, a = pos
            body.append(text(x + dx, y + dy, name, "lb-park", a))
    shift = {"Zion": (-9, 7), "Bryce Canyon": (9, -8)}    # 80 km apart: pull the badges apart
    for i, (name, lon, lat, _) in enumerate(US_PARKS, 1):
        x, y = m.xy(lon, lat)
        if name in shift:
            dx, dy = shift[name]
            body.append(leader(x, y, x + dx, y + dy) + dot(x, y, 2.2) + badge(x + dx, y + dy, i))
        else:
            body.append(badge(x, y, i))
    label = "Map of the 20 national parks on the reading list: " + ", ".join(
        f"{i} {n}" for i, (n, *_) in enumerate(US_PARKS, 1)) + "."
    return figure(svg(W, H, "".join(body), label),
                  "The 20 parks, numbered as in the list below. Many of them are in the West; "
                  "only Acadia, the Great Smoky Mountains, Mammoth Cave, the Everglades and Dry "
                  "Tortugas are in the east.", minw=600)


LARGEST_KM2 = [("Wrangell-St. Elias", 33682, True), ("Gates of the Arctic", 30448, True),
               ("Denali", 19186, True), ("Katmai", 14870, True), ("Death Valley", 13793, False),
               ("Glacier Bay", 13045, True), ("Lake Clark", 10602, True),
               ("Yellowstone", 8983, False), ("Kobuk Valley", 7085, True),
               ("Everglades", 6107, False)]


def largest_parks_chart():
    W, gap, th, lab_w = 760, 24, 16, 160
    rows = [(n, a, "pk-ak" if ak else "pk-low") for n, a, ak in LARGEST_KM2]
    rows.insert(0, ("Mazowieckie" + X, 35558, "pk-pl"))
    H = 46 + gap * len(rows) + 16
    bw = W - lab_w - 130
    out = []
    for v in range(0, 40001, 10000):
        x = lab_w + bw * v / 36000
        out.append(f'<path class="grid" d="M{x:.1f},30 {x:.1f},{H - 22}"/>' + text(x, 22, f"{v:,} km²", "lb-tick", "middle"))
    for i, (name, a, cls) in enumerate(rows):
        y = 36 + i * gap
        L = bw * a / 36000
        lab = (f"{i}. " if i else "") + name
        out.append(text(lab_w - 8, y + th - 3, lab, "lb" if i else "lb-s", "end"))
        out.append(bar(lab_w, y, L, th, cls))
        out.append(text(lab_w + L + 6, y + th - 3, f"{round(a, -2):,} km²" + (X if i else ""), "lb-s"))
    out.append(legend_inline(W - 400, H - 4, [("pk-ak", "in Alaska"), ("pk-low", "elsewhere"),
                                              ("pk-pl", "our voivodeship" + X + ", for scale")]))
    label = ("Bar chart of the ten largest US national parks by area: " + ", ".join(
        f"{n} {a:,} square kilometres" for n, a, _ in LARGEST_KM2)
        + "; seven are in Alaska. Mazowieckie, for scale, 35,558.")
    return figure(svg(W, H + 6, "".join(out), label, cls="chart"),
                  "The ten largest US national parks, by area. The largest, Wrangell-St. Elias, "
                  "is almost as big as the whole Mazowieckie voivodeship" + XH + ".", minw=600)


CA_PARKS = [  # Canadian Sky's top 10, number 1 first
    ("Pacific Rim", -125.7, 49.0, (-12, 4, "end")), ("Banff", -115.7, 51.25, (12, 10, "start")),
    ("Yoho", -116.55, 51.45, (-26, -2, "end")), ("Jasper", -118.0, 52.9, (12, -4, "start")),
    ("Mont-Tremblant", -74.4, 46.45, (-12, -6, "end")),
    ("Cape Breton Highlands", -60.65, 46.75, (8, 24, "middle")),
    ("Gaspésie", -66.0, 48.97, (-12, -6, "end")), ("Waterton Lakes", -113.9, 49.05, (12, 12, "start")),
    ("Thousand Islands", -75.95, 44.36, (-12, 12, "end")),
    ("Gros Morne", -57.75, 49.6, (12, 4, "start")),
]


def canada_parks_map():
    W, H = 760, 470
    m = Map(LAEA(-95, 55), bbox(-141, 42.5, -52.5, 62.5), (0, 0, W, H), pad=6)
    body = [frame(W, H), context_land(m)]
    usa = [p for s, d in GEO["states"].items() if d["country"] == "USA" for p in d["geom"]]
    body.append(m.path(m.polys(usa), "land0"))
    for st, d in GEO["states"].items():
        if d["country"] == "CAN":
            body.append(m.path(m.polys(d["geom"]), "st land1"))
    body.append(lakes(m, min_size=3))
    for i, (name, lon, lat, (dx, dy, a)) in enumerate(CA_PARKS, 1):
        x, y = m.xy(lon, lat)
        body.append(text(x + dx, y + dy, name, "lb-park", a))
    for name, lon, lat, lines, dx, dy, a in [
            ("Wood Buffalo", -113.0, 59.4, ["Wood Buffalo:", "the largest"], 12, 4, "start"),
            ("Kluane", -139.0, 60.75, ["Kluane:", "Mount Logan"], 12, 4, "start")]:
        x, y = m.xy(lon, lat)
        body.append(f'<rect class="badge-o" x="{x - 6:.1f}" y="{y - 6:.1f}" width="12" height="12" rx="3"/>')
        body.append(multiline(x + dx, y + dy, lines, "lb-park", a, 13))
    for i, (name, lon, lat, _) in enumerate(CA_PARKS, 1):
        x, y = m.xy(lon, lat)
        if name == "Yoho":                     # next to Banff: shift the badge, point at the park
            body.append(leader(x, y, x - 14, y - 6) + dot(x, y, 2.4) + badge(x - 16, y - 7, i))
        else:
            body.append(badge(x, y, i))
    body.append(at(m, -100, 45.5, "USA", "lb-mid lb-m"))
    label = "Map of Canada's top 10 national parks: " + ", ".join(
        f"{i} {n}" for i, (n, *_) in enumerate(CA_PARKS, 1)) + "; also Wood Buffalo and Kluane."
    return figure(svg(W, H, "".join(body), label),
                  "Canadian Sky's top 10, numbered as in the list below, with Wood Buffalo (the "
                  "largest park) and Kluane. Four of the ten are in the Rockies.", minw=600)


# ---------------------------------------------------------------- F25: timeline
EVENTS = [(1608, ["Quebec City: Old Town", "founded"], 1),
          (1804, ["Lewis and Clark set off", "up the Missouri" + X], -1),
          (1825, ["the Erie Canal joins the", "Hudson to the Great Lakes"], 2),
          (1872, ["Yellowstone: the first", "US national park"], -2),
          (1885, ["Banff: Canada's first", "national park"], 3),
          (1913, ["Death Valley:", "56.7°C" + X], -3),
          (1936, ["Hoover Dam"], 1),
          (1937, ["Gaspésie", "National Park"], -1),
          (1947, ["Snag, Yukon:", "−63°C"], 2),
          (2025, ["Gulf of America,", "Mount McKinley (US names)"], -2)]


def timeline():
    W, H = 760, 330
    x0, x1, ya = 30, 728, 165
    lo, hi = 1600, 2030

    def X_(yr):
        return x0 + (x1 - x0) * (yr - lo) / (hi - lo)
    out = [f'<path class="axis-thick" d="M{x0},{ya} {x1},{ya}"/>']
    for yr in range(1600, 2031, 50):
        x = X_(yr)
        out.append(f'<path class="tick" d="M{x:.1f},{ya - 4} {x:.1f},{ya + 4}"/>')
        out.append(text(x, ya + (18 if yr % 100 == 0 else 16), str(yr), "lb-tick" if yr % 100 == 0 else "lb-tiny", "middle"))
    for yr, lines, lvl in EVENTS:
        x = X_(yr)
        up = lvl > 0
        stem = 26 + 34 * (abs(lvl) - 1)
        y1 = ya - stem if up else ya + stem + 8
        out.append(f'<path class="mark-line" d="M{x:.1f},{ya} {x:.1f},{y1:.1f}"/>')
        out.append(f'<circle class="mark-dot-s" cx="{x:.1f}" cy="{ya}" r="4"/>')
        anchor = "end" if yr > 1990 else "start" if yr < 1640 else "middle"
        tx = x + (4 if anchor == "start" else -4 if anchor == "end" else 0)
        ty = y1 - 6 - 13 * (len(lines) - 1) if up else y1 + 14
        out.append(text(tx, ty, f"{yr}", "lb-b", anchor))
        out.append(multiline(tx, ty + 13, lines, "lb-s", anchor, 13) if not up
                   else multiline(tx, ty + 13, lines, "lb-s", anchor, 13))
    label = "Time axis from 1600 to today: " + "; ".join(
        f"{y}: {' '.join(l).replace(X, '')}" for y, l, _ in EVENTS) + "."
    return figure(svg(W, H, "".join(out), label, cls="chart"), "", minw=640)


# ---------------------------------------------------------------- photos on the page
def _credits():
    path = HERE / "src" / "photos" / "credits.json"
    return json.loads(path.read_text()) if path.exists() else {}


CREDITS = _credits()


def img(key, alt):
    c = CREDITS.get(key, {"width": 640, "height": 427})
    return (f'<img src="/img/usa_kanada/{key}.jpg" width="{c["width"]}" height="{c["height"]}" '
            f'alt="{esc(alt)}" loading="lazy" decoding="async">')


def photos(items):
    """items: (key, caption); the caption is also the alt text, without tags."""
    figs = "".join(f'<figure class="ph">{img(k, _plain(c))}<figcaption>{c}</figcaption></figure>'
                   for k, c in items)
    return f'<div class="photos">{figs}</div>'


def card(key, num, title, where, body, alt=None):
    n = f'<span class="num">{num}</span>' if num else ""
    w = f'<p class="where">{where}</p>' if where else ""
    return (f'<article class="card">{img(key, alt or _plain(title))}<div class="cbody">'
            f'<h4>{n}{title}</h4>{w}<p>{body}</p></div></article>')


def cards(items):
    return '<div class="cards">' + "".join(items) + "</div>"


def _plain(s):
    import re
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def credits_html(used):
    rows = []
    for key in sorted(used, key=lambda k: CREDITS[k]["title"].lower()):
        c = CREDITS[key]
        lic = (f'<a href="{esc(c["licence_url"])}" target="_blank" rel="noopener">{esc(c["licence"])}</a>'
               if c["licence_url"] else esc(c["licence"]))
        rows.append(f'<li><a href="{esc(c["page"])}" target="_blank" rel="noopener">'
                    f'{esc(c["title"])}</a>: {esc(c["artist"])}, {lic}</li>')
    return "<ul class=\"credits\">" + "".join(rows) + "</ul>"


# ---------------------------------------------------------------- photos
# key -> Wikimedia Commons file; tools/usa_canada/photo_prep.py fetches them with their credits
PHOTOS = {
    "bison": "American bison k5680-1.jpg",
    "bald_eagle": "Bald eagle about to fly in Alaska (2016).jpg",
    "beaver": "American Beaver.jpg",
    "canada_goose": "Canada goose on Seedskadee NWR (27826185489).jpg",
    "moose": "Alaska moose.jpg",
    "polar_bear": "Polar Bear - Alaska (cropped).jpg",
    "monarch": "Monarch butterfly in BBG (84685).jpg",
    "orca": "Killerwhales jumping.jpg",
    "walrus": "Walrus in the Russian Arctic National Park, Novaya Zemlya 2015-2.jpg",
    "caribou": "Mountain-type Woodland Caribou.jpg",
    "puffin": "Puffin (Fratercula arctica).jpg",
    "lynx": "Canada lynx by Michael Zahra (cropped).jpg",
    "beluga": "Oceanogràfic 29102004.jpg",
    "sherman": "General Sherman 1469870071.jpg",
    "redwood": "US 199 Redwood Highway.jpg",
    "bristlecone": "Big bristlecone pine Pinus longaeva.jpg",
    "joshua": "Joshua Tree 01.jpg",
    "saguaro": ("Carnegiea gigantea in Saguaro National Park near Tucson, Arizona during "
                "November (58).jpg"),
    "zion": "Zion angels landing view.jpg",
    "yellowstone": "Great Fountain Geyser Sunset.jpg",
    "acadia": "Bass Harbor Head Light Station 2016.jpg",
    "yosemite": "Yosemite falls winter 2010.JPG",
    "sequoia": "General Sherman Tree in Sequoia National Park - June 2022.jpg",
    "crater": "Crater Lake National Park, OR 2006 (6539577313).jpg",
    "grand_canyon": "Canyon River Tree (165872763).jpeg",
    "smokies": "View atop Cliff Tops on Mount LeConte, GSMNP, TN.jpg",
    "death_valley": "Mesquite Sand Dunes in Death Valley.jpg",
    "redwood_np": "Redwood National Park, fog in the forest.jpg",
    "olympic": "Cedar Creek Abbey Island Ruby Beach.jpg",
    "teton": "Barns grand tetons.jpg",
    "everglades": "Sunset over the River of Grass, NPSphoto, G.Gardner (9255157507).jpg",
    "big_bend": "Canyon, Rio Grande, Texas.jpeg",
    "joshua_np": "Joshua Tree - Cyclops + Potato Head - Sunrise.jpg",
    "bryce": "Inspiration Point Bryce Canyon November 2018 panorama.jpg",
    "arches": "Delicate arch sunset.jpg",
    "sand_dunes": "Great Sand Dunes National Park and Preserve, United States (Unsplash).jpg",
    "tortugas": "Fort-Jefferson Dry-Tortugas.jpg",
    "mammoth": "Mammoth Cave Rotunda (USGS Lwt02830).jpg",
    "pacific_rim": "Looking back over Long Beach (48832887943).jpg",
    "banff": "1 lake louise pano 2019.jpg",
    "yoho": "Takakkaw Falls - panoramio (1).jpg",
    "jasper": "Mount Andromeda at dusk, Jasper National Park, Alberta, Canada.jpg",
    "tremblant": "Paysage lac Monroe.jpg",
    "cape_breton": ("Cabot Trail winding through Cape Breton Highlands National Park, Nova "
                    "Scotia.jpg"),
    "gaspesie": ("Lac aux Américains vu du Mont Xalibu, Parc national de la Gaspésie, Québec, "
                 "Canada.jpg"),
    "waterton": "Watertonlake.jpg",
    "thousand": "Thousand Islands 2.JPG",
    "gros_morne": "Western Brook Pond Newfoundland Canada DSC 6405.jpg",
    "fundy": "Sandstone in Canada - IMG 0791 (11385934064).jpg",
    "niagara": ("Aerial view of the Canadian Falls (Horseshoe Falls) and the Hornblower Niagara "
                "Cruises boat; Niagara Falls.JPG"),
    "thor": "Mount Thor, Akshayuk Pass, Baffin Island.jpg",
    "moraine": "Moraine Lake 17092005.jpg",
    "denali": "Wonder Lake and Denali.jpg",
    "logan": "Mount Logan.jpg",
    "prairies": "Trees and Canola - panoramio.jpg",
    "saint_helens": "MSH82 st helens plume from harrys ridge 05-19-82.jpg",
    "great_salt": "Great Salt Lake by Sentinel-2.jpg",
    "hoover": "2017 Aerial view Hoover Dam 4774.jpg",
}


ALL = [where_map, size_people_chart, regions_map, lambda: region_map("Northeast"),
       lambda: region_map("Southeast"), lambda: region_map("Midwest"),
       lambda: region_map("Southwest"), lambda: region_map("West"), sizes_figure, canada_map,
       mountains_map, peaks_chart, west_map, cross_section, waters_map, rivers_chart,
       great_lakes_map, tide_chart, climate_map, temperature_chart, flags_figure, trees_chart,
       ages_axis, monarch_map, us_parks_map, largest_parks_chart, canada_parks_map, timeline]

# ---------------------------------------------------------------- CSS
_LIGHT = """
  --sea: #d6e6f5; --land0: #e4e3dd; --land1: #f5f3ec; --edge: #ffffff; --usa: #f3dcc3; --can: #f6d3d6;
  --river: #2f7fc4; --hot: #d6336c; --warm: #c27c0e; --halo: rgba(255,255,255,.88);
  --r-ne: #f2c3d6; --r-se: #c9e5bd; --r-mw: #f5df9c; --r-sw: #f3c79c; --r-w: #c8d2f3;
  --r-ce: #b9e0e3; --r-cc: #dccbf1; --r-cw: #e6d2b8; --r-cn: #dce2ea;
  --c-usa: #e07b24; --c-can: #d6336c; --c-pl: #9aa0b8; --c-ak: #2a78d6;
  --mtn: #a0704a; --plain: #cfe3ad; --shield: #e6d6e6; --tundra: #d2edf0; --sand: #e7bf5c;
  --cold: #3b82d6; --neutral: #e6e7ee; --hot2: #e0452b; --sky: #eef5fc; --ground: #ddcaa8;
  --cont: #cddff6; --sub: #cbe7c3; --semi: #f3dca2; --west: #e4d3ef; --icy: #e9f2fb;
"""
_DARK = """
  --sea: #15233c; --land0: #2a2d45; --land1: #303554; --edge: #12142a; --usa: #4a3826; --can: #4c2830;
  --river: #6fb0ef; --hot: #ff6fa6; --warm: #f2b04c; --halo: rgba(27,30,56,.9);
  --r-ne: #5a2a41; --r-se: #29482c; --r-mw: #574818; --r-sw: #5a381e; --r-w: #2d3868;
  --r-ce: #1d474c; --r-cc: #41315c; --r-cw: #493927; --r-cn: #323e4b;
  --c-usa: #f2994a; --c-can: #ff6fa6; --c-pl: #7c83a6; --c-ak: #5b9cf0;
  --mtn: #c49a74; --plain: #3a5230; --shield: #4a3a52; --tundra: #23464b; --sand: #c9a243;
  --cold: #5b9cf0; --neutral: #4a4e6e; --hot2: #ff7a5c; --sky: #18223b; --ground: #4a3d2c;
  --cont: #24395e; --sub: #284a2c; --semi: #574618; --west: #43335a; --icy: #2b3a4f;
"""
ART_CSS = f"""
:root {{{_LIGHT}}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{{_DARK}}} }}
:root[data-theme="dark"] {{{_DARK}}}
figure.viz {{ margin: 16px 0; }}
figure.viz .scroll {{ overflow-x: auto; border-radius: 12px; }}
figure.viz .inner {{ min-width: var(--minw, 0); }}
figure.viz svg {{ display: block; width: 100%; height: auto; }}
figure.viz.small {{ max-width: 420px; }}
figure.viz figcaption {{ font-size: .9rem; color: var(--muted); margin-top: 6px; max-width: 68ch; }}
figure.viz figcaption:empty {{ display: none; }}
svg.map text, svg.chart text {{ font-family: "Atkinson Hyperlegible", system-ui, sans-serif; fill: var(--ink);
  paint-order: stroke; stroke: var(--halo); stroke-width: 3px; stroke-linejoin: round; }}
svg.chart text {{ stroke-width: 2.5px; }}
svg .sea {{ fill: var(--sea); }}
svg .land0 {{ fill: var(--land0); stroke: var(--edge); stroke-width: .6; }}
svg .land1 {{ fill: var(--land1); stroke: var(--edge); stroke-width: .6; }}
svg .usa {{ fill: var(--usa); stroke: var(--edge); stroke-width: .5; }}
svg .can {{ fill: var(--can); stroke: var(--edge); stroke-width: .5; }}
svg .st {{ stroke: var(--edge); stroke-width: .7; }}
svg .edges {{ fill: none; stroke: var(--edge); stroke-width: .7; }}
svg .r-ne {{ fill: var(--r-ne); }} svg .r-se {{ fill: var(--r-se); }} svg .r-mw {{ fill: var(--r-mw); }}
svg .r-sw {{ fill: var(--r-sw); }} svg .r-w {{ fill: var(--r-w); }} svg .r-ce {{ fill: var(--r-ce); }}
svg .r-cc {{ fill: var(--r-cc); }} svg .r-cw {{ fill: var(--r-cw); }} svg .r-cn {{ fill: var(--r-cn); }}
svg .c-cont {{ fill: var(--cont); }} svg .c-sub {{ fill: var(--sub); }} svg .c-semi {{ fill: var(--semi); }}
svg .c-west {{ fill: var(--west); }} svg .c-cold {{ fill: var(--icy); }} svg .c-can {{ fill: var(--land1); }}
svg .lake {{ fill: var(--sea); stroke: var(--river); stroke-width: .4; stroke-opacity: .6; }}
svg .lake-big {{ fill: var(--sea); stroke: var(--river); stroke-width: 1; }}
svg .lake-mi {{ fill: none; stroke: var(--hot); stroke-width: 2.2; }}
svg .river {{ fill: none; stroke: var(--river); stroke-width: 1.7; stroke-linejoin: round; stroke-linecap: round; }}
svg .river.thin {{ stroke-width: .9; stroke-opacity: .75; }}
svg .canal {{ fill: none; stroke: var(--river); stroke-width: 2; stroke-dasharray: 5 3; }}
svg .mtn {{ fill: var(--mtn); fill-opacity: .5; }}
svg .plain {{ fill: var(--plain); }} svg .shield {{ fill: var(--shield); }} svg .tundra {{ fill: var(--tundra); }}
svg .desert {{ fill: var(--sand); fill-opacity: .6; }}
svg .desert.d2 {{ fill-opacity: .85; }}
svg .canyon {{ fill: var(--hot2); fill-opacity: .7; }}
svg .border-hot {{ fill: none; stroke: var(--hot); stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }}
svg .border-warm {{ fill: none; stroke: var(--warm); stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }}
svg .border-nat {{ fill: none; stroke: var(--ink); stroke-width: 1.3; stroke-opacity: .5; }}
svg .circle-line {{ fill: none; stroke: var(--muted); stroke-width: .8; stroke-dasharray: 4 4; }}
svg .cap {{ fill: var(--hot); stroke: var(--paper); stroke-width: 1.2; }}
svg .cap-ring {{ fill: none; stroke: var(--hot); stroke-width: 1.6; }}
svg .city {{ fill: var(--ink); stroke: var(--paper); stroke-width: 1.2; }}
svg .city-x {{ fill: var(--paper); stroke: var(--ink); stroke-width: 1.5; }}
svg .peak {{ fill: var(--ink); stroke: var(--paper); stroke-width: 1; }}
svg .leader {{ fill: none; stroke: var(--muted); stroke-width: .9; }}
svg .inset {{ fill: var(--sea); stroke: var(--muted); stroke-width: .8; stroke-opacity: .6; }}
svg .inset[fill="none"] {{ fill: none; }}
svg .inset-mark {{ fill: none; stroke: var(--ink); stroke-width: 1; stroke-opacity: .6; }}
svg .legend-bg {{ fill: var(--paper); stroke: var(--line); }}
svg .badge {{ fill: var(--c, var(--hot)); stroke: var(--paper); stroke-width: 1.5; }}
svg .badge-o {{ fill: var(--paper); stroke: var(--c, var(--hot)); stroke-width: 2; }}
svg .scalebar {{ fill: none; stroke: var(--ink); stroke-width: 2; }}
svg .grid {{ fill: none; stroke: var(--line); stroke-width: 1; }}
svg .axis {{ fill: none; stroke: var(--muted); stroke-width: 1; }}
svg .axis-thick {{ fill: none; stroke: var(--muted); stroke-width: 2; }}
svg .tick {{ fill: none; stroke: var(--muted); stroke-width: 1; }}
svg .b-usa, svg .pk-usa {{ fill: var(--c-usa); }} svg .b-can, svg .pk-can {{ fill: var(--c-can); }}
svg .b-pl, svg .pk-pl {{ fill: var(--c-pl); }} svg .pk-ak {{ fill: var(--c-ak); }} svg .pk-low {{ fill: var(--c-usa); }}
svg .b-usa-f {{ fill: var(--c-usa); fill-opacity: .8; stroke: var(--c-usa); stroke-width: .6; }}
svg .b-pl-f {{ fill: var(--c-pl); fill-opacity: .8; stroke: var(--c-pl); stroke-width: .6; }}
svg .fade {{ opacity: .35; }}
svg .sky {{ fill: var(--sky); }} svg .sea-x {{ fill: var(--sea); }}
svg .ground {{ fill: var(--ground); stroke: var(--mtn); stroke-width: 1; }}
svg .sealevel {{ fill: none; stroke: var(--river); stroke-width: 1; stroke-dasharray: 5 4; }}
svg .cloud {{ fill: var(--paper); stroke: var(--muted); stroke-width: 1; }}
svg .rain {{ fill: none; stroke: var(--river); stroke-width: 1.4; stroke-linecap: round; stroke-dasharray: 5 6; }}
svg .wind, svg .flow {{ fill: none; stroke: var(--ink); stroke-width: 1.6; }}
svg .wind-head, svg .flow-head {{ fill: var(--ink); }}
svg .flow {{ stroke: var(--river); }} svg .flow-head {{ fill: var(--river); }}
svg .divide {{ fill: none; stroke: var(--hot); stroke-width: 2; stroke-dasharray: 4 3; }}
svg .tide-fill {{ fill: var(--river); fill-opacity: .14; }}
svg .tide-line {{ fill: none; stroke: var(--river); stroke-width: 2; stroke-linejoin: round; }}
svg .block {{ fill: var(--land0); stroke: var(--muted); stroke-width: 1; }}
svg .floor {{ fill: none; stroke: var(--muted); stroke-width: .6; }}
svg .window {{ fill: var(--sea); }}
svg .bracket {{ fill: none; stroke: var(--ink); stroke-width: 1.4; }}
svg .mark-line {{ fill: none; stroke: var(--muted); stroke-width: 1; }}
svg .mark-dot {{ fill: var(--paper); stroke: var(--ink); stroke-width: 2; }}
svg .mark-dot-s {{ fill: var(--ink); stroke: var(--paper); stroke-width: 1.5; }}
svg .hurr {{ fill: none; stroke: var(--hot); stroke-width: 2; }} svg .hurr circle {{ fill: var(--hot); }}
svg .aurora {{ fill: none; stroke: #2fbf71; stroke-width: 4; stroke-linecap: round; opacity: .8; }}
svg .us-red {{ fill: #b22234; }} svg .us-blue {{ fill: #3c3b6e; }} svg .us-star {{ fill: #fff; }}
svg .ca-red {{ fill: #d52b1e; }}
svg .flag-edge {{ fill: none; stroke: var(--line); stroke-width: 1; }}
svg .person {{ fill: none; stroke: var(--ink); stroke-width: 3; stroke-linecap: round; }}
svg .cactus {{ fill: #4f8a3c; }} svg .trunk {{ fill: #8a4f2c; }} svg .crown {{ fill: #3f7d3a; }}
svg .migr {{ fill: none; stroke: var(--c-usa); stroke-width: 3; stroke-dasharray: 8 5; }}
svg .migr-end {{ fill: var(--c-usa); stroke: var(--paper); stroke-width: 1.5; }}
svg .lb {{ font-size: 13px; }}
svg .lb-s {{ font-size: 11.5px; }}
svg .lb-b {{ font-size: 13px; font-weight: 700; }}
svg .lb-m {{ fill: var(--muted); }}
svg .lb-tiny {{ font-size: 10px; fill: var(--muted); }}
svg .lb-xs {{ font-size: 10.5px; font-weight: 700; letter-spacing: .08em; fill: var(--muted); }}
svg .lb-tick {{ font-size: 11px; fill: var(--muted); font-variant-numeric: tabular-nums; }}
svg .lb-mid {{ font-size: 14px; font-weight: 700; letter-spacing: .08em; }}
svg .lb-big {{ font-size: 22px; font-weight: 800; letter-spacing: .14em; font-family: "Bricolage Grotesque", sans-serif; }}
svg .lb-faint {{ fill: var(--muted); stroke-width: 0; opacity: .55; }}
svg .lb-sea {{ font-size: 13px; font-style: italic; fill: var(--river); letter-spacing: .1em; }}
svg .lb-reg {{ font-size: 13px; font-weight: 800; letter-spacing: .1em; }}
svg .lb-st {{ font-size: 10.5px; fill: var(--muted); letter-spacing: .02em; }}
svg .lb-cap {{ font-size: 12.5px; font-weight: 700; }}
svg .lb-catch {{ font-size: 11px; font-style: italic; fill: var(--muted); }}
svg .lb-pk {{ font-size: 11.5px; font-weight: 700; }}
svg .lb-mtn {{ font-size: 11px; font-weight: 700; letter-spacing: .12em; fill: var(--mtn); }}
svg .lb-land {{ font-size: 11.5px; font-style: italic; fill: var(--muted); }}
svg .lb-desert {{ font-size: 10.5px; font-weight: 700; letter-spacing: .1em; }}
svg .lb-desert2 {{ font-size: 10.5px; font-style: italic; fill: var(--muted); }}
svg .lb-river {{ font-size: 11.5px; font-style: italic; font-weight: 700; fill: var(--river); }}
svg .lb-letter {{ font-size: 30px; font-weight: 800; fill: var(--river); font-family: "Bricolage Grotesque", sans-serif; }}
svg .lb-lake {{ font-size: 11.5px; font-weight: 700; fill: var(--river); }}
svg .lb-park {{ font-size: 11.5px; font-weight: 700; }}
svg .lb-badge {{ font-size: 10.5px; font-weight: 700; fill: var(--paper); stroke: none; }}
svg .x {{ fill: var(--muted); font-weight: 700; }}
.maplegend {{ display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: .9rem; color: var(--muted); }}
.maplegend span {{ display: inline-flex; align-items: center; gap: 6px; }}
.region {{ display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr); gap: 14px; align-items: start; margin: 18px 0; }}
.region figure.viz {{ margin: 0; }}
.region h4 {{ margin: 0 0 4px; font-family: "Bricolage Grotesque", sans-serif; color: var(--c); font-size: 1.1rem; }}
.region .tbl {{ margin: 0; }}
@media (max-width: 720px) {{ .region {{ grid-template-columns: minmax(0, 1fr); }} }}
.photos {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); margin: 14px 0; }}
.ph {{ margin: 0; background: var(--paper); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }}
.ph img, .card img {{ display: block; width: 100%; height: auto; aspect-ratio: 3 / 2; object-fit: cover; background: var(--line); }}
.ph figcaption {{ font-size: .85rem; padding: 6px 10px 8px; color: var(--muted); line-height: 1.35; }}
.cards {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); margin: 14px 0; }}
.card {{ background: var(--paper); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
.card .cbody {{ padding: 8px 12px 12px; }}
.card h4 {{ margin: 0; font-family: "Bricolage Grotesque", sans-serif; font-size: 1.05rem; display: flex; gap: 8px; align-items: center; }}
.card .num {{ flex: none; width: 24px; height: 24px; border-radius: 50%; background: var(--c); color: var(--paper); font-size: .78rem; display: grid; place-items: center; font-family: "Atkinson Hyperlegible", sans-serif; }}
.card .where {{ margin: 0; font-size: .85rem; color: var(--muted); }}
.card p {{ margin: .3rem 0 0; font-size: .92rem; line-height: 1.45; }}
.credits {{ font-size: .8rem; columns: 2 300px; padding-left: 1.1rem; }}
.credits li {{ break-inside: avoid; margin: 0 0 3px; }}
@media print {{
  figure.viz, .card, .ph, .region {{ break-inside: avoid; }}
  figure.viz .inner {{ min-width: 0 !important; }}
}}
"""


def preview():
    uk = (HERE.parents[1] / "site" / "public" / "ojaj_uk.html").read_text(encoding="utf-8")
    css = uk[uk.index("<style>") + 7:uk.index("</style>")]
    figs = "\n".join(f'<section class="branch {"ypog"[i % 4]}"><h3>{i + 1}</h3>{f()}</section>'
                     for i, f in enumerate(ALL))
    figs += photos([("denali", "Denali"), ("logan", "Mount Logan"), ("saint_helens", "St Helens")])
    figs += cards([card("zion", 1, "Zion", "Utah", "Watchman Mountain ...")])
    out = HERE.parents[1] / "tmp" / "_art_preview.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap">
<style>{css}</style><style>body{{margin:0}}{ART_CSS}</style></head>
<body><div class="wrap">{figs}</div></body></html>""", encoding="utf-8")
    sizes = {i + 1: len(f()) for i, f in enumerate(ALL)}
    print(f"wrote {out} ({out.stat().st_size:,} bytes); figure sizes: {sizes}")


if __name__ == "__main__":
    preview()
