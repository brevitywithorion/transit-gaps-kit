# Example: Topeka, Kansas (second-city test)

Config: `../../configs/topeka.yaml`  
GTFS: https://gtfs.remix.com/topeka_metro_ks_us.zip (Topeka Metro; also linked from https://www.topekametro.org/GTFS/)

**This example is for local verification only — do not deploy a public Topeka site from this kit without a separate decision.**

After `transit-gaps -c configs/topeka.yaml run`, see `runs/topeka-ks/report/`.

Expected pattern (Oct 2026 feed): no Sunday service; weekday last trip starts ~18:40 (earlier evening cutoff than Lawrence).
