# Transit Gaps Kit

**Question it answers:** *Who can get where without a car, and when?*

A town-agnostic, config-driven toolkit for measuring fixed-route transit **span-of-service gaps** (Sunday, evenings, short days) from a public GTFS feed — with optional hooks for ACS demographics, LODES jobs, and walk+transit access modeling (r5py).

Born from a real local question in **Lawrence, Kansas** ([live report](https://lawrence-transit-gaps.pages.dev)). Generalized so another town can drop in a city config and get the same kind of schedule-gap report. Prepared for [strongtowns.dev](https://strongtowns.dev) (Strong Towns Community Developers).

> **Not affiliated with Strong Towns** ([strongtowns.org](https://www.strongtowns.org)). MIT-licensed open source by Orion Wills, 2026.

## Why this exists

Small and mid-size U.S. cities often publish a GTFS feed but never answer, in plain language:

- Is there **Sunday** service?
- What time does the last bus leave on a weekday?
- Which routes (if any) cover **evening / second shift**?

This kit makes that answer reproducible from the published schedule, then leaves a clear path to deeper access modeling (can a household reach a grocery, clinic, and job in 30–45 minutes by walking + bus?).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Pick a city config (or copy configs/_template.yaml)
transit-gaps -c configs/topeka.yaml run
```

Outputs land in `runs/topeka-ks/`:

| Path | What |
|---|---|
| `data/gtfs/` | Downloaded feed |
| `out/route_span.csv` | First/last trip per route × day type |
| `out/route_hourly.csv` | Trips per hour + headways |
| `out/system_hourly.csv` | System-wide trips/routes per hour |
| `out/gaps_summary.json` | Machine-readable Sunday / evening flags |
| `report/span_report.md` | Plain-language report |
| `report/span_report.html` | Same report as HTML |

Commands:

```bash
transit-gaps -c configs/lawrence.yaml fetch-gtfs
transit-gaps -c configs/lawrence.yaml span
transit-gaps -c configs/lawrence.yaml report
transit-gaps -c configs/lawrence.yaml fetch-acs   # needs CENSUS_API_KEY
```

## Config reference

One YAML file per city. See `configs/lawrence.yaml` and `configs/topeka.yaml`.

| Key | Required | Meaning |
|---|---|---|
| `city.name` / `city.state` | yes | Display name |
| `city.state_fips` / `city.county_fips` | yes | Census FIPS (zero-padded strings) |
| `city.timezone` | no | Default `America/Chicago` |
| `city.branding.title` | no | Report / site title |
| `gtfs.url` | yes | Public static GTFS zip URL |
| `boundary.bbox` | yes | `[west, south, east, north]` for OSM clip / maps |
| `boundary.geoid_prefix` | yes | State+county GEOID prefix (e.g. `20045`) |
| `boundary.local_crs` | no | Projected CRS for meter buffers |
| `analysis.sample_dates` | yes | `weekday` / `saturday` / `sunday` ISO dates inside the feed calendar |
| `analysis.evening_cutoff` | no | Default `21:00` — routes with last trip at/after this count as evening service |
| `acs.*` / `lodes.*` / `peers.*` | no | Optional deeper modules |

**Never put API keys in the config.** Set `CENSUS_API_KEY` in the environment for ACS pulls.

## Data sources

| Source | License / terms | Used for |
|---|---|---|
| Agency **GTFS** (public zip) | Agency terms; typically open for analysis | Span, headways |
| [U.S. Census ACS](https://www.census.gov/data/developers/data-sets.html) | Public data; API requires free key | Zero-car HH, employment (optional) |
| [LEHD LODES](https://lehd.ces.census.gov/data/) | Public domain | Jobs by block (optional) |
| [TIGER/Line](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html) | Public domain | Block group shapes (optional) |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) via Geofabrik | ODbL | Walk network + destinations (optional r5py) |
| [FTA NTD](https://www.transit.dot.gov/ntd) | Public | Peer hours (optional) |

ACS attribution (required when ACS is used): *This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.*

## Limitations

- **Schedule ≠ reality.** GTFS is the published plan; it ignores missed trips, snow, and On Demand / paratransit.
- **Trip-start spans.** “Last trip” is the departure at the trip’s first stop, not the last arrival at every stop (both are useful; the report uses trip starts for comparability).
- **Sample dates.** Results depend on dates you pick inside the feed calendar (KU-session vs summer, holidays via `calendar_dates`).
- **Access modeling (optional)** needs Java 21 + r5py, a clipped OSM extract, and careful ACS MOE handling. The core kit does **not** require that stack.
- Example prose under `examples/lawrence/` is Lawrence-specific fact-checking; do not paste it into another city’s report.

## Repo layout

```
configs/           # one YAML per city
src/transit_gaps/  # library + CLI
sql/               # reference DuckDB SQL (span/hourly)
templates/         # HTML/CSS starting points for a fuller site
examples/lawrence/ # origin-city prose + sample span CSVs
examples/topeka/   # notes from the second-city test
docs/              # third-party licenses, optional pipeline notes
runs/              # local only (gitignored) — per-city outputs
```

## Credits

- Origin: Lawrence, KS transit access gaps project (2026), live at https://lawrence-transit-gaps.pages.dev
- Author: Orion Wills
- Intended submission venue: [strongtowns.dev](https://strongtowns.dev)
- **Not affiliated with Strong Towns**

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Orion Wills.

Third-party dependency licenses: [docs/THIRD_PARTY.md](docs/THIRD_PARTY.md).
