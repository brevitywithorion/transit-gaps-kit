# Reference DuckDB SQL

These files document the original Lawrence SQL shape. The library implementation in
`src/transit_gaps/span.py` is what the CLI runs; it substitutes `analysis.sample_dates`
from the city config instead of hard-coded Lawrence dates.

`01_load.sql` still shows example dates for reading — do not run it unchanged for another city.
