"""Cut the Natural Earth files down to what the USA & Canada notebook's maps draw.

Reads the GeoJSON files in tools/usa_canada/src/geo/ (Natural Earth, public domain, downloaded from
github.com/nvkelso/natural-earth-vector on 19.11.2026) and writes tools/usa_canada/src/na_geo.json:
states and provinces, neighbouring countries, lakes, the rivers on the reading list, named
mountain ranges, deserts and landscapes, capitals and cities, and peaks, as lon/lat
simplified to about a kilometre. The notebook's generator projects and draws them.

Run: python3 -I tools/usa_canada/build_na_geo.py
"""
import json
from pathlib import Path

GEO = Path(__file__).parent / "src" / "geo"
OUT = Path(__file__).parent / "src" / "na_geo.json"
BOX = (-180.0, 14.0, -40.0, 84.0)          # lon min, lat min, lon max, lat max
TOL = 0.01                                  # degrees, about 1 km


def load(name):
    return json.loads((GEO / f"{name}.geojson").read_text())["features"]


def prop(f, key):
    p = f["properties"]
    return p.get(key, p.get(key.upper()))


def dp(points, tol):
    """Douglas-Peucker on a list of (x, y)."""
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
        norm = (dx * dx + dy * dy) ** 0.5
        best, idx = -1.0, None
        for i in range(a + 1, b):
            px, py = points[i]
            # a closed ring starts and ends on the same point: measure from that point
            d = (abs(dy * (px - ax) - dx * (py - ay)) / norm if norm
                 else ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5)
            if d > best:
                best, idx = d, i
        if idx is not None and best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(points, keep) if k]


def in_box(pts):
    return any(BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3] for x, y in pts)


def rings(geom, tol=TOL, min_pts=4, boxed=True):
    """Polygon or MultiPolygon -> list of polygons, each a list of rings of [lon, lat]."""
    if not geom:
        return []
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        rs = []
        for i, ring in enumerate(poly):
            pts = [(round(x, 3), round(y, 3)) for x, y, *_ in ring]
            if i == 0 and boxed and not in_box(pts):
                break
            s = dp(pts, tol)
            if len(s) >= min_pts:
                rs.append(s)
            elif i == 0:
                break
        if rs:
            out.append(rs)
    return out


def lines(geom, tol=TOL):
    if not geom:
        return []
    parts = geom["coordinates"] if geom["type"] == "MultiLineString" else [geom["coordinates"]]
    out = []
    for part in parts:
        pts = [(round(x, 3), round(y, 3)) for x, y, *_ in part]
        if in_box(pts):
            out.append(dp(pts, tol))
    return out


def shared(geom_a, geom_b):
    """The runs of geom_a's outline that geom_b's outline also has: a land border."""
    def outlines(g):
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        return [[(round(x, 5), round(y, 5)) for x, y, *_ in poly[0]] for poly in polys]
    other = {pt for ring in outlines(geom_b) for pt in ring}
    runs = []
    for ring in outlines(geom_a):
        run = []
        for pt in ring:
            if pt in other:
                run.append(pt)
            else:
                if len(run) > 1:
                    runs.append(run)
                run = []
        if len(run) > 1:
            runs.append(run)
    return [dp([(round(x, 3), round(y, 3)) for x, y in r], TOL) for r in runs]


def main():
    data = {"states": {}, "countries": {}, "lakes": {}, "rivers": {}, "areas": {},
            "places": {}, "peaks": {}, "borders": {}, "abroad": {}}
    for f in load("ne_50m_admin_1_states_provinces"):
        if prop(f, "adm0_a3") in ("USA", "CAN"):
            name = prop(f, "name").replace("Québec", "Quebec")
            data["states"][name] = {"country": prop(f, "adm0_a3"), "postal": prop(f, "postal"),
                                    "label": [prop(f, "longitude"), prop(f, "latitude")],
                                    "geom": rings(f["geometry"])}
    raw = {}
    for f in load("ne_50m_admin_0_countries"):
        a3 = prop(f, "ADM0_A3")
        raw[a3] = f["geometry"]
        if a3 in ("POL", "LUX"):
            data["abroad"][a3] = rings(f["geometry"], tol=0.005, boxed=False)
            continue
        g = rings(f["geometry"])
        if g:
            data["countries"][a3] = g
    data["borders"]["USA-CAN"] = shared(raw["USA"], raw["CAN"])
    data["borders"]["USA-MEX"] = shared(raw["USA"], raw["MEX"])
    for f in load("ne_50m_lakes"):
        g = rings(f["geometry"])
        if g:
            name = prop(f, "name") or f"lake{len(data['lakes'])}"
            data["lakes"].setdefault(name, []).extend(g)
    want_rivers = {"Missouri", "Mississippi", "Yukon", "Rio Grande", "St. Lawrence", "Arkansas",
                   "Colorado", "Ohio", "Red", "Columbia", "Hudson", "Mackenzie", "Slave", "Peace",
                   "Fraser", "Thompson", "Snake", "Niagara", "Gila", "Tennessee", "Platte",
                   "North Platte", "Prairie Dog Town Fork Red", "Finlay", "Teslin", "Pecos"}
    for f in load("ne_10m_rivers_lake_centerlines"):
        name = prop(f, "name")
        if name in want_rivers:
            ls = lines(f["geometry"])
            if ls:
                data["rivers"].setdefault(name, []).extend(ls)
    want_areas = {"ROCKY MOUNTAINS": "Rocky Mountains", "APPALACHIAN MTS.": "Appalachian Mountains",
                  "SIERRA NEVADA": "Sierra Nevada", "CASCADE RANGE": "Cascade Range",
                  "ALASKA RANGE": "Alaska Range", "BROOKS RANGE": "Brooks Range",
                  "Adirondack Mts.": "Adirondacks", "Ozark Plateau": "Ozarks",
                  "COAST MOUNTAINS": "Coast Mountains", "MACKENZIE MTS.": "Mackenzie Mountains",
                  "GREAT BASIN": "Great Basin", "SONORAN DESERT": "Sonoran Desert",
                  "CHIHUAHUAN DESERT": "Chihuahuan Desert", "GREAT PLAINS": "Great Plains",
                  "CANADIAN SHIELD": "Canadian Shield", "BARREN GROUNDS": "Barren Grounds",
                  "Grand Canyon": "Grand Canyon", "BAFFIN ISLAND": "Baffin Island",
                  "ARCTIC ARCHIPELAGO": "Arctic Archipelago"}
    for f in load("ne_10m_geography_regions_polys"):
        name = want_areas.get(prop(f, "name"))
        if name:
            data["areas"].setdefault(name, []).extend(rings(f["geometry"], tol=0.02))
    for f in load("ne_10m_populated_places_simple"):
        p = f["properties"]
        if p["adm0name"] in ("United States of America", "Canada", "Mexico"):
            key = p["name"].replace("  ", " ")
            data["places"].setdefault(key, []).append({
                "adm1": p["adm1name"], "cls": p["featurecla"], "pop": p["pop_max"],
                "lon": round(p["longitude"], 3), "lat": round(p["latitude"], 3)})
    for f in load("ne_10m_geography_regions_elevation_points"):
        p = f["properties"]
        x, y = f["geometry"]["coordinates"][:2]
        if p.get("name") and BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]:
            data["peaks"][p["name"]] = {"elev": p.get("elevation"), "lon": round(x, 3),
                                        "lat": round(y, 3)}
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes): " + ", ".join(
        f"{k} {len(v)}" for k, v in data.items()))
    missing = [s for s in ("Missouri", "Mississippi", "Mackenzie", "Colorado", "Rio Grande")
               if s not in data["rivers"]]
    if missing:
        raise SystemExit(f"rivers missing: {missing}")


main()
