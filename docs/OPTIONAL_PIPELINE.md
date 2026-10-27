# Optional deeper pipeline (ACS + LODES + r5py)

The core kit (`fetch-gtfs` → `span` → `report`) needs only a public GTFS URL.

The Lawrence origin project went further:

1. **ACS** zero-vehicle households and commute mode (Census Data API).
2. **LODES** jobs at the block level, rolled to block groups.
3. **OSM** groceries / clinics / pharmacies + walk network.
4. **r5py** travel-time matrices (walk + transit) for several departure slots.
5. Illustrative **service stages** (Sunday midday, later evenings, frequency) with rough costs.
6. A static **site** with map, neighborhood cards, and methods.

Those steps are city-agnostic *in principle* once `boundary.geoid_prefix`, `bbox`, and ACS/LODES settings come from the city YAML. They are **not** fully ported into `0.1.0` of this kit (r5py needs Java 21; runs are heavy). Use the Lawrence live site as a reference implementation, and treat city YAML fields under `acs`, `lodes`, and `analysis` as the contract for a future module.

If you port them:

- Filter TIGER / LODES by `geoid_prefix`.
- Clip OSM with `boundary.bbox`.
- Drive departure slots from `analysis.sample_dates` (and optional extra slots).
- Keep Lawrence-specific prose in `examples/lawrence/` — never hard-code city names in library code.
