COPY (SELECT day_type, route, route_long_name, COUNT(*) trips,
  printf('%02d:%02d', MIN(start_s)//3600, MIN(start_s)%3600//60) first_trip,
  printf('%02d:%02d', MAX(start_s)//3600, MAX(start_s)%3600//60) last_trip,
  ROUND(MIN(start_s)/3600.0,2) first_h, ROUND(MAX(start_s)/3600.0,2) last_h,
  ROUND((MAX(start_s)-MIN(start_s))/3600.0,2) span_h
FROM trip_first GROUP BY day_type, route, route_long_name ORDER BY day_type, TRY_CAST(route AS INT), route) TO 'out/route_span.csv' (HEADER);
