#!/usr/bin/env python3
"""Build the Topeka preview site from runs/topeka-ks outputs."""
import json, math, datetime, html, shutil
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd, markdown

ROOT = Path(__file__).resolve().parents[1] / "runs" / "topeka-ks"
OUT, SITE = ROOT / "out", ROOT / "site"
(SITE / "figures").mkdir(parents=True, exist_ok=True)
(SITE / "data" / "downloads").mkdir(parents=True, exist_ok=True)
(SITE / ".well-known").mkdir(exist_ok=True)
BUILT = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p CT")
TITLE = "Topeka transit access gaps"
GEOID_PREFIX = "20177"
AGENCY = "Topeka Metro"
NOINDEX = True

bg = pd.read_csv(OUT / "bg_base.csv", dtype={"GEOID": str})
A = pd.read_csv(OUT / "access_bg.csv", dtype={"GEOID": str})
S = pd.read_csv(OUT / "access_summary.csv")
span = pd.read_csv(OUT / "route_span.csv")
gaps = json.loads((OUT / "gaps_summary.json").read_text()) if (OUT / "gaps_summary.json").exists() else {}
peers = pd.read_csv(OUT / "peers_table.csv")
dest = pd.read_csv(OUT / "destinations.csv")
hh_tot = int(bg.households.sum())
noveh_tot = int(bg.noveh_hh.sum())
jobs_tot = int(bg.jobs.sum())
sum_county = S[S.area == "all_county"].set_index("slot")

def slot_row(slot):
    r = sum_county.loc[slot]
    return dict(
        hh_miss=int(r.no_any_need_hh),
        noveh_miss=int(r.no_any_need_noveh),
        jobs45=float(r.hh_weighted_jobs_45min_share) * 100,
    )

w8, w21, sun, sat = map(slot_row, ["wed_0800", "wed_2100", "sun_1100", "sat_1100"])
w18 = slot_row("wed_1800")
wd, sat_s = span[span.day_type == "weekday"], span[span.day_type == "saturday"]

def fmt_h(h):
    if h is None or (isinstance(h, float) and math.isnan(h)):
        return "—"
    hr = int(h)
    mi = int(round((h - hr) * 60))
    if mi == 60:
        hr += 1
        mi = 0
    ap = "AM" if hr < 12 else "PM"
    return f"{(hr % 12) or 12}:{mi:02d} {ap}"

topeka_peer = peers[peers.ntd_id.astype(str) == "70014"].iloc[0]

report = f"""# {TITLE}

*Independent analysis. Not a Topeka Metro publication. Not affiliated with Strong Towns. Built {BUILT}.*

## Summary

Who in Topeka and Shawnee County can get where without a car, and **when**?

Using the published **{AGENCY} GTFS** schedule, U.S. Census ACS 2023 household data, LODES 2023 jobs, OpenStreetMap destinations, and a walk+transit travel-time model (r5py):

1. **There is no Sunday fixed-route service.** The GTFS calendar has no Sunday service. Sample Sunday trips: **0**.
2. **Weekday buses end mid-evening.** On a sample Wednesday, last trip starts were about **{fmt_h(float(wd.last_h.max()))}**; **0 routes** ran past 9:00 PM. At 9 PM the access picture matches Sunday (walk-only).
3. **Saturday ends earlier** (last trip start about **{fmt_h(float(sat_s.last_h.max()))}**).
4. On a weekday morning, about **{w8['hh_miss']:,}** Shawnee County households live in block groups that cannot reach a supermarket, doctor, **and** pharmacy within 30 minutes by walking and bus; about **{w8['noveh_miss']:,}** of those are no-vehicle households. On Sunday that rises to about **{sun['hh_miss']:,}** households / **{sun['noveh_miss']:,}** no-vehicle.

Shawnee County: **{hh_tot:,}** households, **{noveh_tot:,}** no-vehicle households, **{jobs_tot:,}** jobs (LODES 2023). OSM destinations: **{len(dest)}**.

## 1. When does the bus run?

| Day type | Routes | Trips | First trip start | Last trip start | Routes past 9 PM |
|---|---:|---:|---|---|---:|
| Weekday | {len(wd)} | {int(wd.trips.sum())} | {fmt_h(float(wd.first_h.min()))} | {fmt_h(float(wd.last_h.max()))} | {int((wd.last_h >= 21).sum())} |
| Saturday | {len(sat_s)} | {int(sat_s.trips.sum())} | {fmt_h(float(sat_s.first_h.min()))} | {fmt_h(float(sat_s.last_h.max()))} | {int((sat_s.last_h >= 21).sum())} |
| Sunday | 0 | 0 | — | — | 0 |

Source: {AGENCY} GTFS (https://gtfs.remix.com/topeka_metro_ks_us.zip). Sample dates Wed 2026-10-21 / Sat 10-24 / Sun 10-25.

## 2. Who can reach daily needs and jobs?

| Slot | Households missing 30-min need access | No-vehicle HH missing | HH-weighted % of county jobs in 45 min |
|---|---:|---:|---:|
| Wed 8 AM | {w8['hh_miss']:,} | {w8['noveh_miss']:,} | {w8['jobs45']:.1f}% |
| Wed 6 PM | {w18['hh_miss']:,} | {w18['noveh_miss']:,} | {w18['jobs45']:.1f}% |
| Wed 9 PM | {w21['hh_miss']:,} | {w21['noveh_miss']:,} | {w21['jobs45']:.1f}% |
| Sat 11 AM | {sat['hh_miss']:,} | {sat['noveh_miss']:,} | {sat['jobs45']:.1f}% |
| Sun 11 AM | {sun['hh_miss']:,} | {sun['noveh_miss']:,} | {sun['jobs45']:.1f}% |

Wed 9 PM matches Sunday because fixed-route service has ended.

## 3. Illustrative stages (not recommendations)

Lawrence used agency-confirmed cost ranges. **Topeka Metro operating-cost assumptions for added evening/Sunday service were not verified.** NTD 2024 lists Topeka Metro fixed-route bus at about **${topeka_peer.cost_per_hour:.2f}/vehicle revenue hour** and **{int(topeka_peer.vehicle_revenue_hours):,}** VRH — a published average, not a marginal cost. This preview **omits a Topeka stage cost table** rather than invent numbers.

## 4. Peers (NTD)

"""
for _, r in peers.sort_values("vehicle_revenue_hours").iterrows():
    report += f"- **{r.agency.split(',')[0]}** ({r.city}): {int(r.vehicle_revenue_hours):,} VRH; ~${r.cost_per_hour:.2f}/hour\n"
report += """
Source: FTA NTD via data.transportation.gov (NTD ID 70014).

## 5. Data that would need a records request

| Item | Why it matters | Likely holder |
|---|---|---|
| Marginal cost per revenue hour for added evening/Sunday service | Stage costs | Topeka Metro / City of Topeka finance |
| On Demand / paratransit hours, fare, coverage | Service after fixed-route ends | Topeka Metro |
| APC or stop-level boardings | Where riders board | Topeka Metro |
| Route-level ridership by time of day | Demand vs span | Topeka Metro |
| Ops contract unit costs | Cost scenarios | Topeka Metro / City of Topeka |
| School bell times (USD 501 and others) | School-access overlays | School districts |
| Confirmation GTFS matches rider guide | Schedule QA | Topeka Metro |
| Title VI analyses for recent changes | Equity framing | Topeka Metro |
| Local transit budget / dedicated tax detail | Who pays | City of Topeka; Shawnee County if relevant |

**Not verified with Topeka Metro** beyond the public GTFS feed and published NTD tables.

## Limits

Schedule ≠ reality; On Demand not modelled; ACS MOEs; LODES 2023 lag; county geography includes rural block groups; stages withheld without agency costs.

## Methods (short)

GTFS span (DuckDB); ACS Census Data API; LODES8 WAC; OSM destinations; r5py 1.1.7 walk+transit (10-min window, 120-min cap). This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.
"""
(ROOT / "report").mkdir(exist_ok=True)
(ROOT / "report" / "draft_report.md").write_text(report)

for f in list(OUT.glob("chart_*.png")) + list(OUT.glob("map_*.png")):
    shutil.copy(f, SITE / "figures" / f.name)

# geojson layers
a8 = A[A.slot == "wed_0800"].copy()
a8["worst"] = a8[["min_to_grocery", "min_to_doctor", "min_to_pharmacy"]].max(axis=1)
a8["jobs45"] = a8.jobs_45min / jobs_tot
bg2 = bg.merge(a8[["GEOID", "no_any_need", "worst", "jobs45", "jobs_45min"]], on="GEOID")
bg2["noveh"] = bg2.noveh_hh / bg2.households
shp = gpd.read_file(ROOT / "data/tiger/tl_2023_20_bg.shp", columns=["GEOID"])
shp = shp[shp.GEOID.str.startswith(GEOID_PREFIX)].to_crs(4326).merge(bg2, on="GEOID")
shp["geometry"] = shp.geometry.simplify(0.0004, preserve_topology=True)
feats = []
for _, r in shp.iterrows():
    feats.append(
        dict(
            type="Feature",
            geometry=json.loads(gpd.GeoSeries([r.geometry]).to_json())["features"][0]["geometry"],
            properties=dict(
                geoid=r.GEOID,
                hh=int(r.households),
                noveh=round(float(r.noveh) * 100, 1) if pd.notna(r.noveh) else None,
                missing=bool(r.no_any_need),
                worst=int(r.worst) if pd.notna(r.worst) else None,
                jobs45=round(float(r.jobs45) * 100, 1) if pd.notna(r.jobs45) else None,
            ),
        )
    )
json.dump(dict(type="FeatureCollection", features=feats), open(SITE / "data/blockgroups.geojson", "w"), separators=(",", ":"))

G = ROOT / "data/gtfs"
sh = pd.read_csv(G / "shapes.txt")
tr = pd.read_csv(G / "trips.txt", dtype=str)
ro = pd.read_csv(G / "routes.txt", dtype=str)
rs = tr.drop_duplicates("shape_id").merge(ro[["route_id", "route_short_name", "route_long_name"]], on="route_id")
rfeats = []
for _, r in rs.iterrows():
    p = sh[sh.shape_id == r.shape_id].sort_values("shape_pt_sequence")
    if len(p) < 2:
        continue
    coords = [[round(x, 5), round(y, 5)] for x, y in zip(p.shape_pt_lon, p.shape_pt_lat)][::3]
    coords.append([round(float(p.shape_pt_lon.iloc[-1]), 5), round(float(p.shape_pt_lat.iloc[-1]), 5)])
    rfeats.append(
        dict(
            type="Feature",
            geometry=dict(type="LineString", coordinates=coords),
            properties=dict(route=str(r.route_short_name), name=str(r.route_long_name)),
        )
    )
json.dump(dict(type="FeatureCollection", features=rfeats), open(SITE / "data/routes.geojson", "w"), separators=(",", ":"))
st = pd.read_csv(G / "stops.txt", dtype=str)
json.dump(
    dict(
        type="FeatureCollection",
        features=[
            dict(
                type="Feature",
                geometry=dict(type="Point", coordinates=[round(float(r.stop_lon), 5), round(float(r.stop_lat), 5)]),
                properties=dict(name=str(r.stop_name)),
            )
            for _, r in st.iterrows()
        ],
    ),
    open(SITE / "data/stops.geojson", "w"),
    separators=(",", ":"),
)

for name in ["bg_base.csv", "access_bg.csv", "access_summary.csv", "route_span.csv", "destinations.csv", "peers_table.csv", "gaps_summary.json"]:
    src = OUT / name
    if src.exists():
        shutil.copy(src, SITE / "data" / "downloads" / name)

md = lambda t: markdown.markdown(t, extensions=["tables", "sane_lists"])
NAV = [
    ("/summary.html", "Start here"),
    ("/", "Report"),
    ("/map.html", "Map"),
    ("/stages.html", "Stages"),
    ("/stops.html", "New stops"),
    ("/peers.html", "Peers"),
    ("/methods.html", "Methods"),
    ("/areas.html", "Neighborhoods"),
    ("/glossary.html", "Glossary"),
    ("/sources.html", "Sources"),
    ("/data/", "Data"),
    ("/amendments.html", "Amendments"),
]

def page(path, title, body, extra=""):
    parts = []
    for h, n in NAV:
        cur = ' aria-current="page"' if h == path else ""
        parts.append(f'<a href="{h}"{cur}>{n}</a>')
    nav = "".join(parts)
    robots = '<meta name="robots" content="noindex, nofollow">' if NOINDEX else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{robots}
<script src="/theme-init.js"></script>
<title>{html.escape(title)} | {html.escape(TITLE)}</title>
<meta name="description" content="Independent analysis of who can reach work, food and healthcare by bus in Topeka, Kansas — and when.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/styles.css">{extra}</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap"><a class="brand" href="/">{html.escape(TITLE)}</a><nav aria-label="Main">{nav}
<button type="button" class="theme-toggle" id="themeToggle" aria-pressed="false"><span>Dark mode</span></button></nav></div></header>
<main id="main" class="wrap">{body}</main>
<footer class="site"><div class="wrap"><p>Independent analysis. Preview / noindex. Not affiliated with Topeka Metro, the City of Topeka, Shawnee County, or Strong Towns. Data: U.S. Census (ACS 2023, LODES 2023, TIGER), {AGENCY} GTFS, OpenStreetMap (ODbL), FTA NTD. This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau. Built {BUILT}.</p>
<p class="muted"><strong>Not verified with Topeka Metro</strong> beyond public GTFS and NTD. AI-assisted research with human direction.</p>
<p class="footlinks"><a href="/data/">Data</a> · <a href="/sources.html">Sources</a> · <a href="/privacy.html">Privacy</a></p></div></footer>
<script src="/theme.js"></script></body></html>"""

def tw(h):
    return h.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")

body_html = tw(md(report))
fig_access = '<figure><img src="/figures/chart_no_access_by_slot.png" alt="Households missing 30-min access by time slot" loading="lazy"><figcaption>Households in block groups missing 30-minute access to grocery, doctor, or pharmacy.</figcaption></figure>'
fig_jobs = '<figure><img src="/figures/chart_jobs45_by_slot.png" alt="Jobs reachable in 45 minutes" loading="lazy"><figcaption>Household-weighted share of county jobs reachable within 45 minutes.</figcaption></figure>'
fig_peers = '<figure><img src="/figures/chart_peers_hours.png" alt="Peer vehicle revenue hours" loading="lazy"><figcaption>NTD 2024 vehicle revenue hours (bus modes).</figcaption></figure>'
fig_map = '<figure><img src="/figures/map_noveh_share.png" alt="No-vehicle share map" loading="lazy"><figcaption>No-vehicle household share by block group with Topeka Metro stops.</figcaption></figure>'
body_html = body_html.replace("<h2>2. Who can reach", fig_map + fig_access + fig_jobs + '<p class="callout">Explore the <a href="/map.html">map</a>.</p><h2>2. Who can reach', 1)
body_html = body_html.replace("<h2>4. Peers", fig_peers + "<h2>4. Peers", 1)
(SITE / "index.html").write_text(page("/", "Report", '<article class="report">' + body_html + "</article>"))

for slug, title, path in [
    ("summary.html", "One-page summary", ROOT / "content/summary.md"),
    ("glossary.html", "Glossary", ROOT / "content/glossary.md"),
    ("decisions.html", "How decisions get made", ROOT / "content/decisions.md"),
]:
    (SITE / slug).write_text(page("/" + slug, title, '<article class="report">' + tw(md(path.read_text())) + "</article>"))

(SITE / "methods.html").write_text(page("/methods.html", "Methods", '<article class="report">' + tw(md("""# Methods

## Span of service
DuckDB on GTFS calendar / trips / stop_times. Sample dates from city config.

## Demographics and jobs
ACS 2023 5-year (Census Data API) for Shawnee County 20/177. LODES8 WAC 2023 jobs to block group. TIGER 2023 shapes.

## Destinations
Geofabrik Kansas OSM clipped to Shawnee County; supermarket/grocery, clinic/hospital/doctors, pharmacy.

## Travel times
r5py 1.1.7; walk+transit; 10-minute departure window; 120-minute cap; need thresholds 30 minutes; jobs 30/45.

## Not done in this preview
Google validation, school overlays, stop candidates, agency-confirmed stage costs (see records-request table).

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.
""")) + "</article>"))

(SITE / "stages.html").write_text(page("/stages.html", "Stages", '<article class="report">' + md("""# Illustrative service stages

Lawrence simulated Sunday/evening/frequency stages with **agency-confirmed** costs.

For Topeka those inputs were **not verified with Topeka Metro**. NTD 2024 MB average cost/hour is not a marginal cost. **No Topeka stage cost table is published in this preview.**

GTFS already shows what evening/Sunday stages would address: no Sunday service; weekday last trips ~6:28 PM.
""") + "</article>"))

(SITE / "stops.html").write_text(page("/stops.html", "New stops", '<article class="report">' + md("""# Potential new stops

**Not replicated for Topeka in this preview.** Needs local stop-spacing review and preferably APC/ridership from Topeka Metro (records request).
""") + "</article>"))

(SITE / "areas.html").write_text(page("/areas.html", "Neighborhoods", '<article class="report">' + md("""# Neighborhood cards

Use the [map](/map.html) and `access_bg.csv` by GEOID until local neighborhood names are defined. **Not verified with the City of Topeka / Topeka Metro.**
""") + "</article>"))

peers_body = "<h1>Peer systems</h1>" + '<div class="tablewrap">' + peers.to_html(index=False) + "</div>"
peers_body += "<p class='note'>FTA NTD 2024 bus modes via data.transportation.gov.</p>" + fig_peers
(SITE / "peers.html").write_text(page("/peers.html", "Peers", '<article class="report">' + peers_body + "</article>"))

rows = []
for ln in (ROOT / "sources.md").read_text().splitlines():
    c = [x.strip() for x in ln.strip().strip("|").split("|")]
    if len(c) >= 4 and ln.startswith("|") and not set(c[0]) <= set("-") and c[0] != "Dataset or document":
        rows.append(f"<tr><td>{html.escape(c[0])}</td><td>{html.escape(c[1])}</td><td>{html.escape(c[2])}</td><td>{html.escape(c[3])}</td></tr>")
src_html = "<h1>Sources</h1><div class='tablewrap'><table><thead><tr><th>Dataset</th><th>Source</th><th>Vintage</th><th>Retrieved</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
src_html += md("\n## Records-request items\n\nSee the report section *Data that would need a records request*.")
(SITE / "sources.html").write_text(page("/sources.html", "Sources", '<article class="report">' + src_html + "</article>"))

(SITE / "amendments.html").write_text(page("/amendments.html", "Amendments", '<article class="report">' + tw(md("""# Amendments

| When (CT) | Change | Why |
|---|---|---|
| 2026-10-27 | Initial Topeka preview from public GTFS, ACS, LODES, OSM, NTD | Second-city kit test; noindex Cloudflare preview |
""")) + "</article>"))

(SITE / "privacy.html").write_text(page("/privacy.html", "Privacy", '<article class="report">' + md("""# Privacy

Static preview. No feedback form or visitor counter. No required cookies. No analytics in this build.
""") + "</article>"))

map_body = """<h1>Map</h1>
<p class="lede">Wednesday 8 AM need-access gaps by Shawnee County block group. Basemap © OpenStreetMap contributors.</p>
<div id="map" style="height:70vh;border:1px solid #ccc;border-radius:8px"></div>
<p class="note">Red = missing supermarket+doctor+pharmacy within 30 minutes (model). Blue lines = GTFS routes.</p>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const map=L.map('map').setView([39.05,-95.69],11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; OpenStreetMap',maxZoom:18}).addTo(map);
fetch('/data/blockgroups.geojson').then(r=>r.json()).then(g=>{
  L.geoJSON(g,{style:f=>({color:'#333',weight:0.5,fillColor:f.properties.missing?'#c53030':'#48bb78',fillOpacity:0.45}),
    onEachFeature:(f,l)=>l.bindPopup('<strong>'+f.properties.geoid+'</strong><br>HH: '+f.properties.hh+'<br>No-vehicle: '+f.properties.noveh+'%<br>Missing needs: '+f.properties.missing+'<br>Jobs 45 min: '+f.properties.jobs45+'%')}).addTo(map);
});
fetch('/data/routes.geojson').then(r=>r.json()).then(g=>L.geoJSON(g,{style:{color:'#2b6cb0',weight:2,opacity:0.7}}).addTo(map));
</script>
"""
(SITE / "map.html").write_text(page("/map.html", "Map", map_body))

(SITE / "data" / "index.html").write_text(
    page(
        "/data/",
        "Data downloads",
        """<h1>Data downloads</h1><ul>
<li><a href="/data/downloads/bg_base.csv">bg_base.csv</a></li>
<li><a href="/data/downloads/access_bg.csv">access_bg.csv</a></li>
<li><a href="/data/downloads/access_summary.csv">access_summary.csv</a></li>
<li><a href="/data/downloads/route_span.csv">route_span.csv</a></li>
<li><a href="/data/downloads/destinations.csv">destinations.csv</a></li>
<li><a href="/data/downloads/peers_table.csv">peers_table.csv</a></li>
<li><a href="/data/downloads/gaps_summary.json">gaps_summary.json</a></li>
<li><a href="/data/blockgroups.geojson">blockgroups.geojson</a></li>
<li><a href="/data/routes.geojson">routes.geojson</a></li>
<li><a href="/data/stops.geojson">stops.geojson</a></li>
</ul>""",
    )
)

for name in ["styles.css", "theme.js", "theme-init.js", "favicon.svg"]:
    src = Path(__file__).resolve().parents[1] / "templates" / "site" / name
    if src.exists():
        shutil.copy(src, SITE / name)

(SITE / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
(SITE / "_headers").write_text(
    """/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), camera=(), microphone=()
  Content-Security-Policy: default-src 'self'; script-src 'self' https://unpkg.com 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: https://*.tile.openstreetmap.org https://unpkg.com; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'
"""
)
(SITE / ".well-known" / "security.txt").write_text(
    "Contact: https://github.com/brevitywithorion/transit-gaps-kit\nPreferred-Languages: en\n"
)
(SITE / "404.html").write_text(page("/404.html", "Not found", "<h1>Page not found</h1><p><a href='/'>Home</a></p>"))

print("SITE BUILT", SITE)
print("pages", sorted(p.name for p in SITE.glob("*.html")))
print("KEY wed8_miss", w8["hh_miss"], "sun_miss", sun["hh_miss"], "jobs45_wed", round(w8["jobs45"], 1))
