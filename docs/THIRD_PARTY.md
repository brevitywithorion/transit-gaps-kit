# Third-party licenses (bundled / declared dependencies)

All **required** Python dependencies of this kit are MIT, BSD, or Apache-2.0 compatible with the kit’s MIT license.

| Package | License (as commonly published) | Role |
|---|---|---|
| duckdb | MIT | GTFS SQL analysis |
| pandas | BSD-3-Clause | Tables |
| pyyaml | MIT | City config |
| requests | Apache-2.0 | GTFS / ACS download |
| markdown | BSD-3-Clause | HTML report |

### Optional (not installed by default)

| Package | License notes | Role |
|---|---|---|
| geopandas / shapely / pyogrio | BSD / MIT-family | Boundaries, maps |
| matplotlib | PSF-based | Charts |
| r5py | **GPL-3.0** (and Conveyal R5) | Walk+transit travel times |

**Important:** The optional `r5py` stack is GPL-licensed. Do not distribute a combined binary that statically or tightly couples this MIT kit with r5py if that would create a GPL obligation you do not intend. Running r5py locally as a separate analysis step on your own machine is fine for research; keep GPL code out of the default install and out of any Strong Towns / public release artifact unless you deliberately accept GPL terms.

### Data (not code)

- GTFS: agency terms (Lawrence Transit / Topeka Metro public feeds used for examples).
- ACS / LODES / TIGER: U.S. government public data.
- OSM: ODbL — share-alike for derived *map databases*; attribution required.

No API keys, tokens, or private credentials are bundled. Census API keys must stay in the environment.
