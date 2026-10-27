"""CLI: transit-gaps <command> --config configs/<city>.yaml"""
from __future__ import annotations
import argparse
from pathlib import Path
from .config import load_config
from .fetch_gtfs import fetch_gtfs
from .span import run_span
from .report import build_report


def main(argv=None):
    p = argparse.ArgumentParser(prog="transit-gaps", description="Town-agnostic transit span / access-gap kit")
    p.add_argument("--config", "-c", required=True, help="Path to city YAML config")
    p.add_argument("--root", default=".", help="Kit root (runs/<city>/ created here)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("fetch-gtfs", help="Download and unzip the city's GTFS feed")
    sub.add_parser("span", help="Compute route spans and gap summary from GTFS")
    sub.add_parser("report", help="Build Markdown + HTML span report")
    sub.add_parser("run", help="fetch-gtfs + span + report (quickstart)")
    sub.add_parser("fetch-acs", help="Optional: pull ACS tables (needs CENSUS_API_KEY)")

    args = p.parse_args(argv)
    cfg = load_config(args.config)
    root = Path(args.root).resolve()
    work = cfg.work_dir(root)
    print(f"City: {cfg.name}, {cfg.state}  work={work}")

    if args.cmd in ("fetch-gtfs", "run"):
        d = fetch_gtfs(cfg, work)
        print(f"GTFS -> {d}")
    if args.cmd in ("span", "run"):
        if not (work / "data" / "gtfs" / "trips.txt").exists():
            fetch_gtfs(cfg, work)
        summary = run_span(cfg, work)
        print("Gaps summary:")
        import json
        print(json.dumps(summary, indent=2))
    if args.cmd in ("report", "run"):
        if not (work / "out" / "gaps_summary.json").exists():
            raise SystemExit("Run `span` first")
        path = build_report(cfg, work)
        print(f"Report -> {path}")
        print(f"HTML   -> {path.with_suffix('.html')}")
    if args.cmd == "fetch-acs":
        from .fetch_acs import fetch_acs
        fetch_acs(cfg, work)


if __name__ == "__main__":
    main()
