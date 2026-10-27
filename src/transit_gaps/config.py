"""Load and validate a city config YAML."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml


@dataclass
class CityConfig:
    path: Path
    raw: dict[str, Any]

    @property
    def city(self) -> dict: return self.raw["city"]
    @property
    def name(self) -> str: return self.city["name"]
    @property
    def state(self) -> str: return self.city["state"]
    @property
    def state_fips(self) -> str: return str(self.city["state_fips"])
    @property
    def county_fips(self) -> str: return str(self.city["county_fips"])
    @property
    def geoid_prefix(self) -> str: return str(self.raw["boundary"]["geoid_prefix"])
    @property
    def bbox(self) -> list[float]: return list(self.raw["boundary"]["bbox"])
    @property
    def local_crs(self) -> str: return self.raw["boundary"].get("local_crs", "EPSG:4326")
    @property
    def gtfs_url(self) -> str: return self.raw["gtfs"]["url"]
    @property
    def branding(self) -> dict: return self.city.get("branding", {})
    @property
    def title(self) -> str: return self.branding.get("title") or f"{self.name} transit access gaps"
    @property
    def timezone(self) -> str: return self.city.get("timezone", "America/Chicago")
    @property
    def analysis(self) -> dict: return self.raw.get("analysis", {})
    @property
    def sample_dates(self) -> dict: return self.analysis.get("sample_dates", {})
    @property
    def evening_cutoff(self) -> str: return self.analysis.get("evening_cutoff", "21:00")
    @property
    def acs(self) -> dict: return self.raw.get("acs", {})
    @property
    def lodes(self) -> dict: return self.raw.get("lodes", {})

    def work_dir(self, root: Path | None = None) -> Path:
        """Per-city working directory under runs/<slug>/."""
        root = root or Path.cwd()
        slug = f"{self.name}-{self.state}".lower().replace(" ", "-")
        d = root / "runs" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "data" / "gtfs").mkdir(parents=True, exist_ok=True)
        (d / "out").mkdir(parents=True, exist_ok=True)
        (d / "report").mkdir(parents=True, exist_ok=True)
        return d


def load_config(path: str | Path) -> CityConfig:
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(p)
    raw = yaml.safe_load(p.read_text())
    _validate(raw, p)
    return CityConfig(path=p, raw=raw)


def _validate(raw: dict, path: Path) -> None:
    for key in ("city", "gtfs", "boundary"):
        if key not in raw:
            raise ValueError(f"{path}: missing required top-level key '{key}'")
    for key in ("name", "state", "state_fips", "county_fips"):
        if key not in raw["city"]:
            raise ValueError(f"{path}: city.{key} is required")
    if "url" not in raw["gtfs"]:
        raise ValueError(f"{path}: gtfs.url is required")
    b = raw["boundary"]
    if "bbox" not in b or len(b["bbox"]) != 4:
        raise ValueError(f"{path}: boundary.bbox must be [west, south, east, north]")
    if "geoid_prefix" not in b:
        raise ValueError(f"{path}: boundary.geoid_prefix is required")
