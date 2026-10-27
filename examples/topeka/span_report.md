# Topeka transit access gaps

*Generated 2026-10-27 17:20 (America/Chicago). Independent analysis; not affiliated with the transit agency or Strong Towns.*

## The question

Who in Topeka can get where without a car, and **when**? This report starts with the published schedule (GTFS): which days and hours buses actually run.

## Headline gaps

- **No Sunday service.** On the sample Sunday (2026-10-25), zero routes ran. Anyone who needs a bus on Sunday cannot use the fixed-route system.
- **Weekday evening gap.** Last trip start about 6:28 PM (evening cutoff in config: 21:00). Second-shift workers and evening appointments are out of reach on most or all routes.
- Saturday: 12 routes, last trip start about 6:11 PM.

## Span of service (trip start times)

### Weekday (2026-10-21)

12 routes, 385 trips. First trip 5:40 AM, last trip 6:28 PM.

| Route | Name | Trips | First | Last |
|---|---|---:|---|---|
| 5 | Indiana | 24 | 06:15 | 17:41 |
| 29 | West 29th | 24 | 06:15 | 17:43 |
| 12 | Huntoon | 25 | 06:09 | 18:09 |
| 17 | West 17th | 25 | 06:09 | 18:09 |
| 2 | North Kansas | 25 | 06:10 | 18:10 |
| 7 | Washburn | 25 | 06:11 | 18:11 |
| 6 | West  6th | 50 | 06:10 | 18:15 |
| 1 | Oakland | 26 | 05:50 | 18:15 |
| 4 | California | 38 | 05:40 | 18:15 |
| 10 | West 10th | 36 | 06:11 | 18:15 |
| 21 | West 21st | 37 | 06:10 | 18:15 |
| 3 | East 6th | 50 | 06:15 | 18:28 |

### Saturday (2026-10-24)

12 routes, 258 trips. First trip 8:15 AM, last trip 6:11 PM.

| Route | Name | Trips | First | Last |
|---|---|---:|---|---|
| 3 | East 6th | 38 | 08:15 | 17:28 |
| 4 | California | 20 | 08:15 | 17:40 |
| 6 | West  6th | 20 | 08:15 | 17:40 |
| 5 | Indiana | 20 | 08:15 | 17:40 |
| 21 | West 21st | 20 | 08:15 | 17:40 |
| 10 | West 10th | 20 | 08:15 | 17:41 |
| 29 | West 29th | 20 | 08:15 | 17:43 |
| 1 | Oakland | 20 | 08:15 | 17:44 |
| 17 | West 17th | 20 | 08:45 | 18:09 |
| 12 | Huntoon | 20 | 08:45 | 18:09 |
| 2 | North Kansas | 20 | 08:45 | 18:10 |
| 7 | Washburn | 20 | 08:45 | 18:11 |

### Sunday (2026-10-25)

*No service.*

## How to read this

- **First/last trip** = earliest/latest trip *start* time (departure at the trip's first stop), not the last arrival at every stop.
- Sample dates come from the city config and must fall inside the GTFS calendar.
- This is schedule analysis only. Real-time reliability, On Demand / paratransit, and walk-access to stops are out of scope for the span report (see optional ACS/r5py modules for access modeling).

## Data

- GTFS: `https://gtfs.remix.com/topeka_metro_ks_us.zip`
- Outputs: `out/route_span.csv`, `out/route_hourly.csv`, `out/system_hourly.csv`, `out/gaps_summary.json`

## Credits

Kit originated from a Lawrence, Kansas local question ([lawrence-transit-gaps.pages.dev](https://lawrence-transit-gaps.pages.dev)). Generalized as an open-source kit for other towns. **Not affiliated with Strong Towns** (strongtowns.org / strongtowns.dev).

MIT License. Copyright Orion Wills 2026.
