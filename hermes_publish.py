#!/usr/bin/env python3
"""
hermes_publish.py
Writes Hermes JSON output as Hugo markdown and pushes to GitHub.

Usage:
  python3 hermes_publish.py --type brief --input /tmp/hermes_brief.json
  python3 hermes_publish.py --type forecast --input /tmp/hermes_forecast.json
  python3 hermes_publish.py --type brief --input /tmp/hermes_brief.json --dry-run
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_PATH = os.environ.get("NZBRIEF_REPO", "/home/jim-rauch/daymark")
GIT_USER  = os.environ.get("GIT_USER_NAME", "Hermes Agent")
GIT_EMAIL = os.environ.get("GIT_USER_EMAIL", "hermes@daymark.nz")


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {' '.join(cmd)}\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def yaml_str(value):
    if value is None:
        return '""'
    escaped = str(value).replace('"', '\\"')
    return f'"{escaped}"'


def build_brief(data):
    date = data["date"]
    lines = ["---", 'title: "Daily Brief"', f"date: {date}", "draft: false", ""]

    if data.get("alert"):
        lines.append(f'alert: {yaml_str(data["alert"])}')
        lines.append("")

    if data.get("dashboard"):
        lines.append("dashboard:")
        for g in data["dashboard"]:
            lines.append(f'  - label: "{g["label"]}"')
            lines.append(f'    level: "{g["level"]}"')
        lines.append("")

    if data.get("indicators"):
        lines.append("indicators:")
        for ind in data["indicators"]:
            lines.append(f'  - label: "{ind["label"]}"')
            lines.append(f'    value: "{ind["value"]}"')
            lines.append(f'    trend: "{ind["trend"]}"')
        lines.append("")

    if data.get("sections"):
        lines.append("sections:")
        for sec in data["sections"]:
            lines.append(f'  - region: {yaml_str(sec["region"])}')
            lines.append(f'    heading: {yaml_str(sec["heading"])}')
            lines.append(f'    body: {yaml_str(sec["body"])}')
            if sec.get("nz_impact"):
                lines.append("    nz_impact:")
                for tag in sec["nz_impact"]:
                    lines.append(f'      - label: "{tag["label"]}"')
                    lines.append(f'        level: "{tag["level"]}"')
        lines.append("")

    lines.append("---")
    return "\n".join(lines)


def build_forecast(data):
    date = data["date"]
    lines = ["---", 'title: "Weekly Forecast"', f"date: {date}", "draft: false", "",
             f'landscape: {yaml_str(data.get("landscape", ""))}', ""]

    if data.get("scenarios"):
        lines.append("scenarios:")
        for s in data["scenarios"]:
            lines.append(f'  - title: {yaml_str(s["title"])}')
            lines.append(f'    status: "{s["status"]}"')
            lines.append(f'    body: {yaml_str(s["body"])}')
            lines.append(f'    confidence: {s["confidence"]}')
            lines.append(f'    nz_impact: "{s["nz_impact"]}"')
        lines.append("")

    if data.get("items"):
        lines.append("items:")
        for item in data["items"]:
            lines.append(f'  - region: {yaml_str(item["region"])}')
            lines.append(f'    heading: {yaml_str(item["heading"])}')
            lines.append(f'    body: {yaml_str(item["body"])}')
            lines.append(f'    probability: {item["probability"]}')
            lines.append(f'    timeframe: "{item["timeframe"]}"')
            lines.append(f'    impact_level: "{item["impact_level"]}"')
            lines.append(f'    impact_label: "{item["impact_label"]}"')
            lines.append(f'    prepare: {yaml_str(item.get("prepare", ""))}')
            lines.append(f'    urgency: {item.get("urgency", 5)}')
        lines.append("")

    lines.append("---")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, choices=["brief", "forecast"])
    parser.add_argument("--input", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        data = json.load(f)

    repo = Path(REPO_PATH)
    date_str = data["date"]

    if args.type == "brief":
        out_dir = repo / "content" / "briefs"
        content = build_brief(data)
    else:
        out_dir = repo / "content" / "forecast"
        content = build_forecast(data)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{date_str}.md"
    out_file.write_text(content + "\n")
    print(f"Written: {out_file}")

    if args.dry_run:
        print("Dry run — skipping git push.")
        return

    run(["git", "config", "user.name", GIT_USER], cwd=repo)
    run(["git", "config", "user.email", GIT_EMAIL], cwd=repo)
    run(["git", "add", str(out_file)], cwd=repo)
    run(["git", "commit", "-m", f"auto: {args.type} {date_str}"], cwd=repo)
    run(["git", "push"], cwd=repo)
    print(f"Pushed: {args.type} {date_str}")


if __name__ == "__main__":
    main()
