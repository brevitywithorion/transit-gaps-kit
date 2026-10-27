"""Download and unzip a public GTFS feed into a city work directory."""
from __future__ import annotations
import io, zipfile
from pathlib import Path
import requests
from .config import CityConfig

REQUIRED = ("agency.txt", "stops.txt", "routes.txt", "trips.txt", "stop_times.txt")


def fetch_gtfs(cfg: CityConfig, work: Path, timeout: int = 120) -> Path:
    """Download cfg.gtfs_url into work/data/gtfs.zip and extract to work/data/gtfs/."""
    gtfs_dir = work / "data" / "gtfs"
    zip_path = work / "data" / "gtfs.zip"
    gtfs_dir.mkdir(parents=True, exist_ok=True)
    r = requests.get(cfg.gtfs_url, timeout=timeout, headers={"User-Agent": "transit-gaps-kit/0.1"})
    r.raise_for_status()
    zip_path.write_bytes(r.content)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        # Strip any top-level folder nesting
        for info in z.infolist():
            name = Path(info.filename).name
            if not name or info.is_dir():
                continue
            target = gtfs_dir / name
            with z.open(info) as src, open(target, "wb") as dst:
                dst.write(src.read())
    missing = [f for f in REQUIRED if not (gtfs_dir / f).exists()]
    if missing:
        raise RuntimeError(f"GTFS missing required files: {missing}")
    # calendar.txt or calendar_dates.txt needed for service days
    if not (gtfs_dir / "calendar.txt").exists() and not (gtfs_dir / "calendar_dates.txt").exists():
        raise RuntimeError("GTFS needs calendar.txt and/or calendar_dates.txt")
    return gtfs_dir
