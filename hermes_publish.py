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
        # Check for specific "nothing to commit" message from git
        if "git" in cmd and "commit" in cmd and "nothing to commit" in result.stderr:
            print(f"INFO: Git commit skipped - nothing to commit for {' '.join(cmd)}", file=sys.stderr)
            return "" # Return empty string for successful no-op
        else:
            print(f"ERROR: {' '.join(cmd)}\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def yaml_str(value):
    if value is None:
        return '""'
    # Sanitize: replace internal double quotes with single quotes to avoid YAML escaping issues
    sanitized = str(value).replace('"', "'")
    return f'"{sanitized}"'


def build_brief(data):
    date = data["date"]
    lines = ["---", 'title: "Daily Brief"', f"date: {date}", "draft: false", ""]

    if data.get("alert"):
        lines.append(f'alert: {yaml_str(data["alert"])}')
        lines.append("")

    if data.get("independent_signals"):
        lines.append(f'independent_signals: {yaml_str(data["independent_signals"])}')
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
    data.pop("items", None)
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



    if data.get("week"):
        lines.append(f'week: {yaml_str(data["week"])}')
    if data.get("month"):
        lines.append(f'month: {yaml_str(data["month"])}')
    if data.get("sixmonth"):
        lines.append(f'sixmonth: {yaml_str(data["sixmonth"])}')
    if data.get("practical_prep"):
        lines.append(f'practical_prep: {yaml_str(data["practical_prep"])}')
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
    run(["git", "add", "-A"], cwd=repo) # Stage all changes
    run(["git", "commit", "-m", f"auto: {args.type} {date_str}"], cwd=repo)
    run(["git", "push", "origin", "HEAD:main"], cwd=repo)
    print(f"Pushed: {args.type} {date_str}")


if __name__ == "__main__":
    main()
