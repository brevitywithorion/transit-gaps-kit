# Topeka Metro — full report results (preview)

**Preview URL (noindex):** https://preview.topeka-transit-gaps.pages.dev  
**Deployment:** https://980877ff.topeka-transit-gaps.pages.dev  
**Production `topeka-transit-gaps.pages.dev`:** intentionally empty (404) — no production deploy.

## Key findings (public data only)

| Metric | Value | Source |
|---|---|---|
| Sunday fixed-route service | **None** (0 trips) | Topeka Metro GTFS calendar |
| Weekday last trip start | ~**6:28 PM**; 0 routes past 9 PM | GTFS sample Wed 2026-10-21 |
| Saturday last trip start | ~**6:11 PM** | GTFS sample Sat 2026-10-24 |
| Shawnee Co. households | 74,528 | ACS 2023 B25044 |
| No-vehicle households | 5,578 | ACS 2023 B25044 |
| Jobs (LODES 2023) | 103,349 | LODES8 WAC |
| HH missing 30-min needs (Wed 8 AM) | **55,277** | r5py + ACS |
| HH missing 30-min needs (Sun 11 AM) | **63,300** | r5py + ACS (walk-only) |
| HH-weighted jobs in 45 min (Wed 8 AM) | **11.8%** | r5py + LODES |
| Same, Sunday | **6.0%** | r5py + LODES |
| NTD 2024 MB VRH / $/hr | 50,975 / $129.25 | FTA NTD (70014) |

## Screenshots

- `local_home.png` — built site homepage (local render; box cannot TLS to pages.dev)
- `local_map.png` — map page local render
- Span-only earlier screenshots also in this folder

## Not replicated (needs records request / local knowledge)

See report §5: marginal $/revenue-hour, On Demand hours, APC/ridership, school bells, Title VI, budget detail, stop-candidate siting, neighborhood cards, Google travel-time validation, agency-confirmed stage costs.
