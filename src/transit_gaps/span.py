"""GTFS span-of-service analysis (weekday / Saturday / Sunday).

Answers: when does the bus run, and are there Sunday or evening gaps?
Uses DuckDB; sample dates come from the city config.
"""
from __future__ import annotations
from datetime import date, datetime
from pathlib import Path
import json
import duckdb
import pandas as pd
from .config import CityConfig

DAY_COLS = {
    "weekday": "wednesday",
    "saturday": "saturday",
    "sunday": "sunday",
}


def _ensure_calendar_files(gtfs: Path) -> None:
    if not (gtfs / "calendar.txt").exists():
        (gtfs / "calendar.txt").write_text(
            "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
        )
    if not (gtfs / "calendar_dates.txt").exists():
        (gtfs / "calendar_dates.txt").write_text("service_id,date,exception_type\n")


def run_span(cfg: CityConfig, work: Path) -> dict:
    """Compute route spans and hourly trip counts; write CSVs under work/out/."""
    gtfs = work / "data" / "gtfs"
    out = work / "out"
    out.mkdir(parents=True, exist_ok=True)
    sample = cfg.sample_dates
    if not sample or not all(k in sample for k in ("weekday", "saturday", "sunday")):
        raise ValueError("analysis.sample_dates must include weekday, saturday, sunday")
    _ensure_calendar_files(gtfs)

    db_path = work / "transit.duckdb"
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))
    g = str(gtfs)

    # Load tables
    for table, fname in [
        ("routes", "routes.txt"),
        ("trips", "trips.txt"),
        ("stops", "stops.txt"),
        ("stop_times", "stop_times.txt"),
        ("calendar", "calendar.txt"),
        ("calendar_dates", "calendar_dates.txt"),
    ]:
        con.execute(
            f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto(?, all_varchar=true)",
            [f"{g}/{fname}"],
        )

    con.execute("""
CREATE OR REPLACE TABLE st AS
SELECT trip_id, stop_id, CAST(stop_sequence AS INT) AS seq,
  CAST(split_part(departure_time,':',1) AS INT)*3600
  + CAST(split_part(departure_time,':',2) AS INT)*60
  + CAST(split_part(departure_time,':',3) AS INT) AS dep_s
FROM stop_times
WHERE departure_time IS NOT NULL AND departure_time <> ''
""")

    # day_services from sample dates
    rows = []
    for day_type, iso in sample.items():
        dow = DAY_COLS[day_type]
        rows.append((day_type, iso, dow))
    con.execute("CREATE OR REPLACE TABLE sample_days (day_type VARCHAR, iso VARCHAR, dow VARCHAR)")
    con.executemany("INSERT INTO sample_days VALUES (?, ?, ?)", rows)

    con.execute("""
CREATE OR REPLACE TABLE day_services AS
WITH d AS (
  SELECT day_type, strptime(iso, '%Y-%m-%d')::DATE AS dt, dow FROM sample_days
),
base AS (
  SELECT d.day_type, c.service_id FROM d
  JOIN calendar c
    ON d.dt BETWEEN strptime(c.start_date, '%Y%m%d') AND strptime(c.end_date, '%Y%m%d')
   AND (
        (d.dow = 'wednesday' AND c.wednesday = '1') OR
        (d.dow = 'saturday'  AND c.saturday  = '1') OR
        (d.dow = 'sunday'    AND c.sunday    = '1') OR
        (d.dow = 'monday'    AND c.monday    = '1') OR
        (d.dow = 'tuesday'   AND c.tuesday   = '1') OR
        (d.dow = 'thursday'  AND c.thursday  = '1') OR
        (d.dow = 'friday'    AND c.friday    = '1')
   )
),
ex AS (
  SELECT d.day_type, cd.service_id, cd.exception_type
  FROM d JOIN calendar_dates cd ON strptime(cd.date, '%Y%m%d') = d.dt
)
SELECT * FROM base
WHERE (day_type, service_id) NOT IN (
  SELECT day_type, service_id FROM ex WHERE exception_type = '2'
)
UNION
SELECT day_type, service_id FROM ex WHERE exception_type = '1'
""")

    con.execute("""
CREATE OR REPLACE TABLE trip_first AS
SELECT ds.day_type, r.route_short_name AS route, r.route_long_name,
       t.trip_id, t.direction_id,
       MIN(st.dep_s) AS start_s, MAX(st.dep_s) AS end_s
FROM trips t
JOIN day_services ds USING (service_id)
JOIN routes r USING (route_id)
JOIN st USING (trip_id)
GROUP BY ALL
""")

    span_path = str(out / "route_span.csv")
    hourly_path = str(out / "route_hourly.csv")
    system_path = str(out / "system_hourly.csv")

    con.execute(f"""
COPY (
  SELECT day_type, route, route_long_name, COUNT(*) AS trips,
    printf('%02d:%02d', MIN(start_s)//3600, MIN(start_s)%3600//60) AS first_trip,
    printf('%02d:%02d', MAX(start_s)//3600, MAX(start_s)%3600//60) AS last_trip,
    printf('%02d:%02d', MAX(end_s)//3600, MAX(end_s)%3600//60) AS last_stop,
    ROUND(MIN(start_s)/3600.0, 2) AS first_h,
    ROUND(MAX(start_s)/3600.0, 2) AS last_h,
    ROUND((MAX(start_s) - MIN(start_s))/3600.0, 2) AS span_h
  FROM trip_first
  GROUP BY day_type, route, route_long_name
  ORDER BY day_type, TRY_CAST(route AS INT), route
) TO '{span_path}' (HEADER)
""")
    con.execute(f"""
COPY (
  WITH g AS (
    SELECT *, start_s - LAG(start_s) OVER (
      PARTITION BY day_type, route, direction_id ORDER BY start_s
    ) AS gap
    FROM trip_first
  )
  SELECT day_type, route, start_s//3600 AS hour, COUNT(*) AS trips_starting,
    ROUND(AVG(gap)/60.0, 1) AS avg_headway_min_by_dir,
    ROUND(MIN(gap)/60.0, 1) AS min_headway_min,
    ROUND(MAX(gap)/60.0, 1) AS max_headway_min
  FROM g GROUP BY day_type, route, hour
  ORDER BY day_type, TRY_CAST(route AS INT), route, hour
) TO '{hourly_path}' (HEADER)
""")
    con.execute(f"""
COPY (
  SELECT day_type, start_s//3600 AS hour,
         COUNT(*) AS trips_starting, COUNT(DISTINCT route) AS routes_active
  FROM trip_first GROUP BY ALL ORDER BY day_type, hour
) TO '{system_path}' (HEADER)
""")

    span = pd.read_csv(span_path)
    agency = ""
    try:
        agency = con.execute("SELECT agency_name FROM routes LIMIT 1").fetchone()
        # routes may not have agency_name; try agency table
    except Exception:
        pass
    try:
        agency = con.execute("SELECT agency_name FROM agency LIMIT 1").fetchone()[0]
    except Exception:
        try:
            con.execute(
                "CREATE OR REPLACE TABLE agency AS SELECT * FROM read_csv_auto(?, all_varchar=true)",
                [f"{g}/agency.txt"],
            )
            agency = con.execute("SELECT agency_name FROM agency LIMIT 1").fetchone()[0]
        except Exception:
            agency = cfg.raw.get("gtfs", {}).get("agency_hint", "")

    summary = _summarize(cfg, span, agency)
    (out / "gaps_summary.json").write_text(json.dumps(summary, indent=2))
    con.close()
    return summary


def _summarize(cfg: CityConfig, span: pd.DataFrame, agency: str) -> dict:
    cutoff = cfg.evening_cutoff
    ch, cm = map(int, cutoff.split(":"))
    cutoff_h = ch + cm / 60.0
    by_day = {}
    for day in ("weekday", "saturday", "sunday"):
        d = span[span.day_type == day] if len(span) else span
        n_routes = int(d.route.nunique()) if len(d) else 0
        n_trips = int(d.trips.sum()) if len(d) else 0
        last = float(d.last_h.max()) if len(d) else None
        first = float(d.first_h.min()) if len(d) else None
        evening = int((d.last_h >= cutoff_h).sum()) if len(d) else 0
        by_day[day] = {
            "routes": n_routes,
            "trips": n_trips,
            "first_trip_h": first,
            "last_trip_h": last,
            "routes_running_past_evening_cutoff": evening,
            "has_service": n_trips > 0,
        }
    return {
        "city": cfg.name,
        "state": cfg.state,
        "agency": agency,
        "gtfs_url": cfg.gtfs_url,
        "sample_dates": cfg.sample_dates,
        "evening_cutoff": cutoff,
        "by_day": by_day,
        "sunday_gap": not by_day["sunday"]["has_service"],
        "evening_gap_weekday": (
            by_day["weekday"]["has_service"]
            and (
                by_day["weekday"]["last_trip_h"] is None
                or by_day["weekday"]["routes_running_past_evening_cutoff"] == 0
            )
        ),
        "generated": datetime.now().isoformat(timespec="seconds"),
    }
