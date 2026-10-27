-- trips per hour and headway (per route, per direction, avg gap between consecutive trip starts in that hour)
COPY (WITH g AS (SELECT *, start_s - LAG(start_s) OVER (PARTITION BY day_type, route, direction_id ORDER BY start_s) gap FROM trip_first)
SELECT day_type, route, start_s//3600 AS hour, COUNT(*) trips_starting,
  ROUND(AVG(gap)/60.0,1) avg_headway_min_by_dir, ROUND(MIN(gap)/60.0,1) min_headway_min, ROUND(MAX(gap)/60.0,1) max_headway_min
FROM g GROUP BY day_type, route, hour ORDER BY day_type, TRY_CAST(route AS INT), route, hour) TO 'out/route_hourly.csv' (HEADER);
COPY (SELECT day_type, start_s//3600 AS hour, COUNT(*) trips_starting, COUNT(DISTINCT route) routes_active
FROM trip_first GROUP BY ALL ORDER BY day_type, hour) TO 'out/system_hourly.csv' (HEADER);
