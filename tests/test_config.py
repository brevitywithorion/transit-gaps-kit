from pathlib import Path
from transit_gaps.config import load_config

ROOT = Path(__file__).resolve().parents[1]

def test_topeka_config_loads():
    cfg = load_config(ROOT / "configs" / "topeka.yaml")
    assert cfg.name == "Topeka"
    assert cfg.geoid_prefix == "20177"
    assert "topeka" in cfg.gtfs_url

def test_lawrence_config_loads():
    cfg = load_config(ROOT / "configs" / "lawrence.yaml")
    assert cfg.name == "Lawrence"
    assert cfg.geoid_prefix == "20045"
