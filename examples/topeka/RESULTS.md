# Topeka Metro — span results (local test, not deployed)

Feed: `https://gtfs.remix.com/topeka_metro_ks_us.zip`  
Feed version note: Updated Oct 26, 2026. Sample dates 2026-10-21 (Wed) / 10-24 (Sat) / 10-25 (Sun).  
Generated locally under `runs/topeka-ks/` (gitignored). Copies of key outputs sit beside this file.

## Key numbers

| Day | Routes | Trips | First trip (start) | Last trip (start) | Past 21:00? |
|---|---:|---:|---|---|---|
| Weekday | 12 | 385 | ~5:40 AM | ~6:28 PM | **No** (0 routes) |
| Saturday | 12 | 258 | ~8:15 AM | ~6:11 PM | **No** |
| Sunday | **0** | **0** | — | — | — |

- **Sunday gap:** yes (no `sunday=1` service_ids in calendar).
- **Weekday evening gap:** yes vs kit cutoff 21:00; system ends mid-evening (~18:40–18:47 trip starts). Earlier end than Lawrence’s city routes (~19:17–20:00) and far earlier than Lawrence routes 11/12 (~22:15+).
- Stops in feed: ~607. Agency: Topeka Metro.

## Sanity check vs Lawrence origin

Both cities show **zero Sunday fixed-route service**. Topeka’s weekday span is shorter in the evening. That is a plausible peer contrast for the kit’s gap flags — not a ranking or recommendation.

## Artifacts

- `gaps_summary.json`, `route_span.csv`, `span_report.md`, `span_report.html` (this folder)
- Full run (including GTFS extract): `runs/topeka-ks/` on a machine that executed `transit-gaps -c configs/topeka.yaml run`
- Screenshot of HTML report: `span_report_screenshot.png` (if present)
