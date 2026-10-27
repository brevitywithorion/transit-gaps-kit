-- REFERENCE ONLY. Sample dates below are examples from Lawrence; the CLI uses city config.
CREATE OR REPLACE TABLE routes AS SELECT * FROM read_csv_auto('data/gtfs/routes.txt', all_varchar=true);
CREATE OR REPLACE TABLE trips AS SELECT * FROM read_csv_auto('data/gtfs/trips.txt', all_varchar=true);
CREATE OR REPLACE TABLE stops AS SELECT * FROM read_csv_auto('data/gtfs/stops.txt', all_varchar=true);
CREATE OR REPLACE TABLE stop_times AS SELECT * FROM read_csv_auto('data/gtfs/stop_times.txt', all_varchar=true);
CREATE OR REPLACE TABLE calendar AS SELECT * FROM read_csv_auto('data/gtfs/calendar.txt', all_varchar=true);
CREATE OR REPLACE TABLE calendar_dates AS SELECT * FROM read_csv_auto('data/gtfs/calendar_dates.txt', all_varchar=true);
-- seconds since midnight
CREATE OR REPLACE TABLE st AS SELECT trip_id, stop_id, CAST(stop_sequence AS INT) seq,
  CAST(split_part(departure_time,':',1) AS INT)*3600+CAST(split_part(departure_time,':',2) AS INT)*60+CAST(split_part(departure_time,':',3) AS INT) dep_s
FROM stop_times WHERE departure_time IS NOT NULL AND departure_time<>'';
-- active services on sample days (Wed 2026-10-21, Sat 2026-10-24, Sun 2026-10-25)
CREATE OR REPLACE TABLE day_services AS
WITH d(day_type, dt, dow) AS (VALUES ('weekday', DATE '2026-10-21', 'wednesday'), ('saturday', DATE '2026-10-24','saturday'), ('sunday', DATE '2026-10-25','sunday')),
base AS (SELECT d.day_type, c.service_id FROM d JOIN calendar c ON d.dt BETWEEN strptime(c.start_date,'%Y%m%d') AND strptime(c.end_date,'%Y%m%d')
  AND ((d.dow='wednesday' AND c.wednesday='1') OR (d.dow='saturday' AND c.saturday='1') OR (d.dow='sunday' AND c.sunday='1'))),
ex AS (SELECT d.day_type, cd.service_id, cd.exception_type FROM d JOIN calendar_dates cd ON strptime(cd.date,'%Y%m%d')=d.dt)
SELECT * FROM base WHERE (day_type, service_id) NOT IN (SELECT day_type, service_id FROM ex WHERE exception_type='2')
UNION SELECT day_type, service_id FROM ex WHERE exception_type='1';
CREATE OR REPLACE TABLE trip_first AS
SELECT ds.day_type, r.route_short_name route, r.route_long_name, t.trip_id, t.direction_id, MIN(st.dep_s) start_s
FROM trips t JOIN day_services ds USING(service_id) JOIN routes r USING(route_id) JOIN st USING(trip_id)
GROUP BY ALL;
