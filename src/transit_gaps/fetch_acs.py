"""Optional ACS 5-year pull for the city county (tract + block group).

Requires CENSUS_API_KEY in the environment. Never prints or writes the key.
This product uses the Census Bureau Data API but is not endorsed or certified
by the Census Bureau.
"""
from __future__ import annotations
import os, sys, json, time
from pathlib import Path
import requests
import pandas as pd
from .config import CityConfig


def fetch_acs(cfg: CityConfig, work: Path) -> list[Path]:
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        sys.exit("CENSUS_API_KEY not set (required for ACS pull; never commit the key)")
    year = str(cfg.acs.get("year", "2023"))
    tables = cfg.acs.get("tables") or ["B08201", "B25044"]
    state, county = cfg.state_fips, cfg.county_fips
    out_dir = work / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for table in tables:
        for geo in ("tract", "block group"):
            params = {
                "get": f"NAME,group({table})",
                "for": f"{geo}:*",
                "in": f"state:{state} county:{county}" if geo == "tract"
                      else f"state:{state} county:{county} tract:*",
                "key": key,
            }
            r = None
            for i in range(4):
                r = requests.get(
                    f"https://api.census.gov/data/{year}/acs/acs5",
                    params=params, timeout=60,
                    headers={"User-Agent": "transit-gaps-kit/0.1"},
                    allow_redirects=False,
                )
                if r.status_code == 200 and r.text.strip().startswith("["):
                    break
                time.sleep(3 * (i + 1))
            if r is None or r.status_code != 200 or not r.text.strip().startswith("["):
                msg = (r.text[:200] if r is not None else "no response").replace(key, "***")
                print(f"FAILED {table} {geo}: {msg}")
                continue
            rows = r.json()
            df = pd.DataFrame(rows[1:], columns=rows[0])
            df = df.loc[:, ~df.columns.duplicated()]
            slug = f"acs{year}_{table.lower()}_{'bg' if geo == 'block group' else 'tract'}"
            (out_dir / f"{slug}.json").write_text(json.dumps(rows))
            csv_path = out_dir / f"{slug}.csv"
            df.to_csv(csv_path, index=False)
            written.append(csv_path)
            print(f"{slug}: {len(df)} rows")
    return written
