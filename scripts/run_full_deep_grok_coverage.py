#!/usr/bin/env python3
"""Plan/run full deep-grok coverage for every starred repo.

Default mode: plan only (no mutations) and write queue/report.
Run mode: invoke spellbook_oracle/deep_grok_repo.py for missing repos.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORACLE = Path.home() / "spellbook_oracle"
MASTER = ORACLE / "master_stars_all.json"
DEEP = ORACLE / "deep_grok_analysis.json"
QUEUE = ROOT / "cache" / "deep_grok_missing_queue.json"
REPORT = ROOT / "cache" / "deep_grok_full_coverage_report.md"


def load_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="execute deep_grok_repo.py for missing repos")
    ap.add_argument("--limit", type=int, default=0, help="max repos to process in run mode")
    ap.add_argument("--sleep", type=float, default=0.2, help="seconds between runs")
    ap.add_argument("--force", action="store_true", help="pass --force to deep_grok_repo.py")
    args = ap.parse_args()

    master = load_json(MASTER, {})
    deep = load_json(DEEP, {})
    stars = master.get("repos") if isinstance(master, dict) else None
    deep_repos = deep.get("repos") if isinstance(deep, dict) else None
    if not isinstance(stars, list):
        print(f"Missing/invalid stars catalog: {MASTER}", file=sys.stderr)
        return 2
    if not isinstance(deep_repos, dict):
        deep_repos = {}

    all_names = sorted(
        {
            str(r.get("full_name") or "").lower().strip()
            for r in stars
            if str(r.get("full_name") or "").strip()
        }
    )
    covered = {str(k).lower().strip() for k in deep_repos.keys() if str(k).strip()}
    missing = [n for n in all_names if n not in covered]

    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(
        json.dumps(
            {
                "total_stars": len(all_names),
                "covered": len(covered),
                "missing": len(missing),
                "repos": missing,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Deep Grok Full Coverage Plan",
        "",
        f"- total stars repos: **{len(all_names)}**",
        f"- deep-grok covered: **{len(covered)}**",
        f"- missing: **{len(missing)}**",
        f"- queue file: `{QUEUE}`",
        "",
    ]

    ran = 0
    failed: list[str] = []
    if args.run and missing:
        cmd_base = [sys.executable, str(ORACLE / "deep_grok_repo.py")]
        if args.force:
            cmd_base.append("--force")
        work = missing[: args.limit] if args.limit and args.limit > 0 else missing
        for repo in work:
            proc = subprocess.run(cmd_base + [repo], cwd=str(ORACLE), capture_output=True, text=True)
            ran += 1
            if proc.returncode != 0:
                failed.append(repo)
            time.sleep(max(0.0, args.sleep))
        lines.extend(
            [
                "## Run results",
                f"- attempted: **{ran}**",
                f"- failed: **{len(failed)}**",
            ]
        )
        if failed:
            lines.append("")
            lines.append("### Failed repos")
            lines.extend([f"- `{r}`" for r in failed[:120]])

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {QUEUE}")
    print(f"Wrote {REPORT}")
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
