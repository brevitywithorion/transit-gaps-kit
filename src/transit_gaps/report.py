"""Build a plain-language Markdown + HTML report from span outputs."""
from __future__ import annotations
import json, html
from datetime import datetime
from pathlib import Path
from .config import CityConfig

try:
    import pandas as pd
except ImportError:
    pd = None


def _fmt_h(h) -> str:
    if h is None: return "—"
    hr = int(h); mi = int(round((h - hr) * 60))
    if mi == 60: hr += 1; mi = 0
    ampm = "AM" if hr < 12 else "PM"
    hr12 = hr % 12 or 12
    return f"{hr12}:{mi:02d} {ampm}"


def build_report(cfg: CityConfig, work: Path) -> Path:
    out = work / "out"
    report_dir = work / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    summary = json.loads((out / "gaps_summary.json").read_text())
    span = pd.read_csv(out / "route_span.csv") if pd is not None else None
    md = _markdown(cfg, summary, span)
    md_path = report_dir / "span_report.md"
    md_path.write_text(md)
    html_path = report_dir / "span_report.html"
    html_path.write_text(_html(cfg, md, summary))
    return md_path


def _markdown(cfg: CityConfig, s: dict, span) -> str:
    city = cfg.name
    lines = [
        f"# {cfg.title}",
        "",
        f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} ({cfg.timezone}). "
        f"Independent analysis; not affiliated with the transit agency or Strong Towns.*",
        "",
        "## The question",
        "",
        f"Who in {city} can get where without a car, and **when**? "
        "This report starts with the published schedule (GTFS): which days and hours buses actually run.",
        "",
        "## Headline gaps",
        "",
    ]
    by = s["by_day"]
    if s["sunday_gap"]:
        lines.append(f"- **No Sunday service.** On the sample Sunday ({s['sample_dates'].get('sunday')}), "
                     f"zero routes ran. Anyone who needs a bus on Sunday cannot use the fixed-route system.")
    else:
        sun = by["sunday"]
        lines.append(f"- Sunday service: {sun['routes']} routes, last trip about {_fmt_h(sun['last_trip_h'])}.")
    wd = by["weekday"]
    if s["evening_gap_weekday"]:
        lines.append(f"- **Weekday evening gap.** Last trip start about {_fmt_h(wd['last_trip_h'])} "
                     f"(evening cutoff in config: {s['evening_cutoff']}). "
                     "Second-shift workers and evening appointments are out of reach on most or all routes.")
    else:
        lines.append(f"- Weekday evening: {wd['routes_running_past_evening_cutoff']} route(s) run past "
                     f"{s['evening_cutoff']}; system last trip start about {_fmt_h(wd['last_trip_h'])}.")
    sat = by["saturday"]
    if sat["has_service"]:
        lines.append(f"- Saturday: {sat['routes']} routes, last trip start about {_fmt_h(sat['last_trip_h'])}.")
    else:
        lines.append("- **No Saturday service** on the sample date.")
    lines += ["", "## Span of service (trip start times)", ""]
    for day in ("weekday", "saturday", "sunday"):
        d = by[day]
        lines.append(f"### {day.title()} ({s['sample_dates'].get(day, '?')})")
        lines.append("")
        if not d["has_service"]:
            lines.append("*No service.*")
            lines.append("")
            continue
        lines.append(f"{d['routes']} routes, {d['trips']} trips. "
                     f"First trip {_fmt_h(d['first_trip_h'])}, last trip {_fmt_h(d['last_trip_h'])}.")
        lines.append("")
        if span is not None:
            sub = span[span.day_type == day].sort_values("last_h")
            lines.append("| Route | Name | Trips | First | Last |")
            lines.append("|---|---|---:|---|---|")
            for _, r in sub.iterrows():
                name = str(r.route_long_name)[:50]
                lines.append(f"| {r.route} | {name} | {int(r.trips)} | {r.first_trip} | {r.last_trip} |")
            lines.append("")
    lines += [
        "## How to read this",
        "",
        "- **First/last trip** = earliest/latest trip *start* time (departure at the trip's first stop), "
        "not the last arrival at every stop.",
        "- Sample dates come from the city config and must fall inside the GTFS calendar.",
        "- This is schedule analysis only. Real-time reliability, On Demand / paratransit, and walk-access "
        "to stops are out of scope for the span report (see optional ACS/r5py modules for access modeling).",
        "",
        "## Data",
        "",
        f"- GTFS: `{s['gtfs_url']}`",
        f"- Outputs: `out/route_span.csv`, `out/route_hourly.csv`, `out/system_hourly.csv`, `out/gaps_summary.json`",
        "",
        "## Credits",
        "",
        "Kit originated from a Lawrence, Kansas local question "
        "([lawrence-transit-gaps.pages.dev](https://lawrence-transit-gaps.pages.dev)). "
        "Generalized as an open-source kit for other towns. "
        "**Not affiliated with Strong Towns** (strongtowns.org / strongtowns.dev).",
        "",
        "MIT License. Copyright Orion Wills 2026.",
        "",
    ]
    return "\n".join(lines)


def _html(cfg: CityConfig, md: str, summary: dict) -> str:
    # Minimal HTML; optional markdown lib
    try:
        import markdown
        body = markdown.markdown(md, extensions=["tables", "sane_lists"])
    except Exception:
        body = "<pre>" + html.escape(md) + "</pre>"
    title = html.escape(cfg.title)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:system-ui,sans-serif;line-height:1.5;max-width:52rem;margin:2rem auto;padding:0 1rem;color:#1a1a1a}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}}
th,td{{border:1px solid #ccc;padding:.35rem .5rem;text-align:left}}
th{{background:#f4f4f4}}
.muted{{color:#555;font-size:.9rem}}
h1,h2,h3{{line-height:1.2}}
</style></head><body>
<main>{body}</main>
<footer class="muted"><p>Independent analysis. Not affiliated with the transit agency or Strong Towns.</p></footer>
</body></html>"""
