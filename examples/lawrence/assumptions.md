# Assumptions (for the author's review)

## Dates and schedules
- Sample dates: weekday Wed 2026-10-21, Saturday Sat 2026-10-24, Sunday Sun 2026-10-25.
- GTFS feed validity: 2026-08-01 to 2027-07-31 (feed_info.txt, "Updated: Sep 30, 2026").
- KU routes (30s/40s) run only during KU session, 2026-08-24 to 2027-05-14. All sample dates are in session; results do not describe summer/breaks.
- No Sunday service exists in the feed, so Sunday results are walk-only.
- Times in service span tables (out/route_span.csv) are trip departures from the first stop of each trip (not arrival at last stop). gtfs_summary.md instead lists the latest stop time anywhere on the route, for Wed 2026-10-28 / Sat 10-31 / Sun 11-01 (same service_ids, no exceptions).
- Routes 11 and 12: weekday GTFS trips run later than the rider-guide 6 a.m.-8 p.m. span (about 10:15-10:30 p.m. trip starts in out/route_span.csv). Jared Allen (Transit Operations Manager, email 2026-10-27) stated that Route 11/12 runs expanded service when KU classes are in session; see the city service calendar (https://lawrencetransit.org/service-calendar/). Those late trips are seasonal, not year-round systemwide evening service.
- Routing is schedule-based (no real-time delays). r5py analysis times are medians over a 10-minute departure window (08:00-08:10 in the smoke test) and include initial wait.
- Google Maps reality check (decision 2026-10-24) uses the next future Wednesday, since the API only plans future trips. Google is queried at 5 departures (07:55, 07:57, 07:59, 08:01, 08:03 CT) and its best (min) and median door-to-door times are compared with r5py's best (p1) and median (p50) over departures every minute 07:55-08:05 (Wed 2026-10-21 schedule; same service_id). A pair is flagged if either difference exceeds 10 minutes; the threshold is unchanged. Google time includes the initial wait and trailing walk legs (staticDuration). Google samples every 2 min, r5py every minute, so medians can differ when a 30-min-headway bus leaves inside the window.

## Demographics and jobs
- ACS 2023 5-year (2019-2023) estimates, with margins of error (90% MOE). Estimates with MOE/estimate > 0.3 are flagged and never headline.
- B08201 (vehicles available) is not published at block group; block group no-vehicle households come from B25044 (tenure by vehicles: owner + renter no-vehicle). Tract B08201 is the control total source.
- Household control total 49,939 (B08201_001E tract sum, equals B25044_001E bg sum).
- LODES8 2023 WAC S000 JT00 (all jobs, primary and non-primary). Douglas County total 51,342. Jobs reflect 2023, a 3-year lag.
- Block-to-block group by first 12 digits of the 2020 block GEOID (LODES8 uses 2020 blocks, matching TIGER 2023).

## Geography and destinations
- Neighborhood units: 73 Douglas County (20045) block groups, TIGER/Line 2023.
- OSM extract date: Geofabrik kansas-latest 2026-10-20 20:23 UTC (3:23 PM CT). OSM completeness is not guaranteed; no shop=grocery/greengrocer features were tagged in the extract, so small groceries/convenience-grocers are missing.
- Clinics include amenity=doctors and healthcare=clinic. Point = representative point of polygon.

## Session 3 accessibility (2026-10-24)
- Origins: the 73 block group representative points (out/bg_base.csv). Everyone in a block group is given that point's travel time; large rural block groups are approximated poorly.
- Destinations: 65 OSM points. "Grocery" = 15 supermarkets only (small grocers missing from OSM, so grocery gaps are overstated where a small grocer exists). "Doctor" = 34 clinics/doctors + 1 hospital. "Pharmacy" = 15 pharmacies.
- Jobs: LODES8 WAC 2023 jobs placed at each block group's representative point; "jobs within X min" = sum of jobs in block groups whose point is reachable in X min.
- Travel time: r5py walk + transit, median over a 10-minute departure window, initial wait included, 120-minute cap. In out/access_matrix.parquet, travel_time = 120 with reachable = False means not reachable within 120 min.
- Time slots: Wed 2026-10-21 08:00, 18:00, 21:00; Sat 2026-10-24 11:00; Sun 2026-10-25 11:00 (no Sunday service, so Sunday is walking only).
- "Reasonable time" thresholds (for the author to confirm): grocery, doctor and pharmacy within 30 minutes; jobs counted within 30 and 45 minutes.
- Headline rule: no-vehicle household counts are reported only as county-wide sums with root-sum-square MOE, and only when MOE/estimate <= 0.3. No tract passes 0.3 either (B25044 summed or B08201 tract), so tract and block-group no-vehicle figures are context only.
- "Near a stop" = block group point within 800 m (straight line) of any GTFS stop: 47 block groups, 33,009 households.

## Methods note: Google reality check (known limitation, decision 2026-10-24)
5 of 8 test pairs agree with Google Maps (Routes API, 5 departures 07:55-08:03 next Wednesday) within 10 minutes on both best case and median (out/gmaps_compare.csv). The 3 that differ:
- East Hills -> downtown (median -21 min) and East Hills -> Walmart (median -22 min). Best cases agree within 2 min. East Hills is served by route 5 every 30 min with a bus near 08:00. Three of Google's five sampled departures fall before that bus, while r5py, sampling every minute, catches it on fewer than half of its departures (likely boarding slack). The difference comes from which side of one 30-min bus the samples fall, not from a different network.[1]
- Downtown -> KU (best -13 min): Google finds a trip boarding about 08:02 (18 min door to door) that r5py does not use (r5py best 31 min).[2]
The 10-minute threshold was not loosened. Medians used in the analysis can therefore overstate travel time near a 30-min bus at some origins.

[1] out/gmaps_compare_departures.csv: Google boards route 5 at 07:55/08:00 for 07:55-07:59 requests and 08:25 for 08:01-08:03.
[2] Not yet traced in the GTFS; a possible r5py stop-snapping or transfer difference. Left open.

## Illustrative scenarios and costs (scenarios_costs.py, revised 2026-10-24; replaces fixes.py)
- Framing: scenarios show what a gap is worth; they are not recommendations (decision 2026-10-24 ~2:14 PM CT).
- Revenue hours = GTFS trip durations x layover factor 1.144-1.192 (NTD average typical Saturday bus revenue hours 167 in 2024 and 174 in 2025, divided by 146 GTFS Saturday trip hours on city routes 1-12). The fall 2026 schedule may differ from 2024/25.
- Cost per revenue hour, three documented points: $46.00 (2023 contract variable rate, excludes fuel and fixed monthly fees; nearest documented marginal cost; the current operator's rate was not found), $86.99 (2024-2028 operations contract $45,236,994.03 / 5 years / 104,000 approved revenue hours, all-in), $104.63 (NTD FY2024 fully allocated fixed-route bus cost; FY2025 $97.59). Ranges pair low hours with $46 and high hours with $104.63. On 2026-10-27, Jared Allen (Transit Operations Manager, Lawrence Transit) said he did not currently have a better figure for the cost of adding an hour of fixed-route service; the range above is unchanged.
- Peer context: NTD FY2024 fixed-route bus cost per revenue hour, full reporters in urbanized areas of 50,000-200,000 with more than 20,000 revenue hours: median about $123 (directly operated) / $123 (purchased); college-town peers $74 (University of Iowa) to $155 (Champaign-Urbana).
- No separate deadhead factor: the contract pays revenue hours only, and NTD cost per hour is per revenue hour.
- Excluded: capital (extra buses), fuel at the low end, fare revenue (fixed route is fare-free), any reduction in Sunday on-demand hours if fixed routes ran.
- 255 weekdays, 52 Sundays per year.
- Scenario A is simulated in r5py (scenario_sunday.py): Saturday city services added to Sun 2026-10-25 in a copy of the GTFS. B and C are proxies, not simulated.

## On-demand microtransit (not modelled)
- Lawrence Transit On Demand runs Sundays 8 a.m.-6 p.m. and nights 8 p.m.-6 a.m. (Sundays midnight-6 a.m.) within Lawrence city limits, $3 per one-way trip since Mar 1, 2026, booked by app or phone. Confirmed current and city-limits coverage by Jared Allen, Transit Operations Manager, Lawrence Transit, email 2026-10-27. It is about 10% of contracted revenue hours. It is not in the GTFS and has no fixed schedule, so the model treats Sunday and late evening as walking only (or fixed route only). Results therefore describe the fixed-route network, not all public transport.

## Thresholds
- 30 minutes is the headline threshold; out/sensitivity_thresholds.csv shows 20, 45 and 60 minutes.

## Staged scenarios, hours, schools (2026-10-24 ~2:31 PM direction)
- Stages (scenarios_r5.py) are edits to copies of the GTFS: Sunday stages clone Saturday city trips (10:00-16:00, or all) onto Sun 2026-10-25; evening stages repeat each route/direction's last weekday trip at its recent headway (minimum 15 min) until 21:00, 22:00 or 22:30; frequency stages add a trip halfway between existing weekday trips starting 06:00-19:00; new routes are hypothetical straight-line alignments with stops every ~500 m, 1.3 detour factor, 22 km/h, 20 s dwell, every 30 min 06:00-20:00 weekdays and Saturday. Only Wednesday is modelled for weekdays; annual hours use 255 weekdays, 52 Saturdays/Sundays.
- Evaluated times: Sunday 8, 11, 14, 17; evening 20:30, 21:30 and 22:00 (22:00 added 2026-10-24 ~2:51 PM; eve3_2230 is still computed in out/stages_effects.csv but dropped from the report: no added 30-min access over eve2); frequency 8:00 and 12:00; new routes 8:00, 12:00 and Saturday 11:00.
- "Households gaining access" = households in block groups moving from missing to having grocery, doctor and pharmacy all within 30 min, averaged over evaluated times. "Helped" = gaining access OR >=5 min saved on average to the three OR jobs within 45 min up >=10% and >=500 at any evaluated time. Helped households are not riders.
- Rideshare comparison: block group point to nearest supermarket, straight line x 1.3, 25 mph; Lyft $0.60 + $0.99/mi + $0.17/min (min $4.24) + $4.00 service fee; UberX $1.19 + $1.49/mi + $0.12/min (min $7.43) + $2.70 fee (third-party rates); 104 rides/year = one grocery round trip a week; no surge, tips or Allen Fieldhouse fee.
- Peer hours: NTD 2024 MB, urbanized areas 50,000-200,000, >=20,000 annual MB revenue hours, service-area population > 0 (188 agencies). Lawrence Transit and KU report separately.
- Hour-shift illustration (hours_shift.py): every second weekday trip starting 10:00-14:00 on routes 1-9 removed; trips are not chosen by ridership because route/trip ridership is not public.
- Schools: USD 497 middle (Billy Mills, Liberty Memorial Central, Southwest, West) and high (Free State, Lawrence High, College and Career Center) from OSM; bells 8:00 start, 3:11/3:15 dismissal, Wednesday 1:15/1:40 (USD 497 2026-27). Each block group is assigned its nearest school of each level (not attendance zones); "USD 497 area" proxy = block group point within 8 km of a USD 497 school (61 block groups). Morning: latest single departure (every 5 min, 06:30-07:45) arriving by 07:55. Afternoon: median over 15:20-15:30 departures; Wednesday 13:45. Households stand in for students (no student counts at block group).
- School/work overlap: ACS B08302 time leaving home for work, all modes, county; bus loads are not public.

## Site map layers (2026-10-24)
- Employment rate = B23025_004 (employed, civilian) / B23025_001 (population 16+), an employment-to-population ratio, not 1 minus unemployment.
- Transit commute share = B08301_010 (public transportation excl. taxicab) / B08301_001 (workers 16+). Estimate; block-group margins are wide.
- No-vehicle share = noveh_hh / households from out/bg_base.csv (B25044).
- Proportion MOEs: ACS formula sqrt(MOE_num^2 - p^2 MOE_den^2) / den, using + when the radicand is negative. Values with CV = (MOE/1.645)/estimate > 0.3 are labelled low reliability.
- Travel-time layers: weekday 8:00-8:10 AM (out/access_bg.csv, wed_0800); job reach share uses county LODES jobs as the denominator.

## Google check retired (2026-10-24 ~3:38 PM CT)
- The Google key is restricted by the author to websites (https://lawrence-transit-gaps.pages.dev/*) and the Maps JavaScript API only, for the site basemap. Server-side Routes API calls from checks/gmaps_compare.py are therefore expected to fail, so check 3 is retired as a known limitation (non-blocking, no API calls). The last comparison stands: 5 of 8 test trips within 10 minutes (out/gmaps_compare.csv, methods note above).
- Verification call (one Routes computeRoutes request, 15:38 CT): it still returned HTTP 200, so the restriction was not yet in effect at that time (Google says key restriction changes can take up to about 5 minutes). To be re-tested once.

## Potential new bus stops (2026-10-24)
- Candidates: midpoints of gaps longer than 800 m along the route shape between consecutive stops of one Wednesday trip per shape; candidates within the same 150 m grid cell merged. Feasibility (curb, grade, right-of-way, campus or express segments) not assessed.
- Walk access: r5py walk-only on OSM, 4.8 km/h; 5 min treated as about 400 m and 10 min as about 800 m. "Gaining" = census blocks newly within that walk of the candidate and not already within it of an existing stop.
- Households per block = block-group households (ACS 2023) x block share of LODES RAC 2023 residents-employed; a proxy, since ACS has no block household counts. Jobs = LODES WAC 2023.
- 30-min access test: the stop added to every trip on the matching shapes at the midpoint time, with +20 s at all later stops on those trips; weekday 8:00-8:10 AM; block-group points (coarse for a single stop).
- Dwell cost: 12-25 s per bus serving the stop (DDOT toolbox 10-15 s; HCM 2000 15 s dwell + 10 s; London AVL 11.6 s deceleration/acceleration). Annual hours = Wednesday trips x seconds x 255 weekdays; cost at $46 x 1.144 to $104.63 x 1.192 per hour. Weekend trips excluded.
- Construction tiers from published unit costs of other agencies (UTA 2023, CARTA ~2021, SamTrans 2023) and Lawrence's 2021 grant estimate; not inflation-adjusted.

## Funding scenarios (funding.py)
- Operating offsets: low 0% (5307 formula and KDOT amounts are fixed and already in use); high 50% (FTA operating share), an upper bound requiring new money. Capital offsets: low 0%; high 80% (FTA typical capital share). Bus 85% and Low-No 90% shares are not applied to stops.
- Cost per household uses mid stage cost and the same household counts as the stages table; stops use households newly within 800 m (best 188, median 115 of 7 stops with any gain).
- CMAQ is listed for completeness; Douglas County has no nonattainment area and KDOT's applicant list excludes it, so it is not counted as an offset. Areas of Persistent Poverty tract eligibility was not checked.
- KU student-fee funding pays for KU routes only and is not counted as an offset.

## Neighborhood cards (areas.py)
- Block groups are assigned to 10 broad areas by their representative point: Kansas River ~38.977N, 23rd St ~38.942N, Iowa St ~-95.257, Haskell Ave ~-95.223, downtown/Mass St ~-95.245; Eudora east of -95.16; Baldwin City south of 38.84; the rest outside the Lawrence box is "Rural Douglas County". Names are descriptive, not official neighborhood boundaries; "North Lawrence and north of the river" includes rural block groups north of the river.
- Per-area stage effects use the same slots as the stages table, averaged over slots. Costs shown on cards are citywide, not per area.

## Stress test (stress.py)
- Base reproduces the published run (r5py defaults: walk 3.6 km/h, no separate walk-time cap, 10-min departure window, median, up to 8 rides). Variants change one assumption at a time: walk speed 4.0/4.8 km/h; walk cap 10/15/20 min per walking leg; 60-min departure windows starting 7:30, 20:30 and 10:30; single departure time (1-min window); at most 2 rides; 45-min threshold.
- The GTFS feed has no fixed-route service on the Sunday test date, so Sunday results are walking only.
