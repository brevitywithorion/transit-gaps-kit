"""Walk+transit access matrices (r5py) driven by city config.

Requires optional deps: r5py, geopandas, pyarrow, Java 21.
Clear ~/.cache/r5py if a prior GTFS zip was nested or corrupt.
"""
from __future__ import annotations
from pathlib import Path
from .config import CityConfig

def run_access(cfg: CityConfig, work: Path) -> Path:
    """Compute access_bg.csv / access_summary.csv under work/out/.

    Implementation for v0.2 lives in scripts/run_access_city.py (used for Topeka).
    This wrapper documents the contract; call the script for full runs.
    """
    raise NotImplementedError(
        "Run: python scripts/run_access_city.py --config configs/<city>.yaml --root ."
    )
