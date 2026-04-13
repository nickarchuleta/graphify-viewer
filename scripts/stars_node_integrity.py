#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path.home() / "graphify-out"
STARS_HTML = ROOT / "github_stars_mirror.html"
REPORT = ROOT / "stars_node_integrity_report.md"
VALID_GROUPS = {"hub", "mac", "ai_code", "agents", "local_ai", "graphs", "browser", "data", "sec", "misc"}


def parse_const(name: str, html: str):
    m = re.search(rf"const {name} = (.*?);\n", html, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def main() -> int:
    html = STARS_HTML.read_text(encoding="utf-8")
    nodes = parse_const("FALLBACK_NODES", html) or []
    edges = parse_const("FALLBACK_EDGES", html) or []

    issues: list[str] = []
    hub = [n for n in nodes if n.get("id") == "_github_stars_hub"]
    if len(hub) != 1:
        issues.append(f"hub count != 1 (got {len(hub)})")

    ids = [n.get("id") for n in nodes]
    dup = sorted({x for x in ids if ids.count(x) > 1 and x is not None})
    if dup:
        issues.append(f"duplicate node ids: {len(dup)}")
    idset = set(ids)

    bad_edge = [e for e in edges if e.get("from") not in idset or e.get("to") not in idset]
    if bad_edge:
        issues.append(f"edges with missing endpoint: {len(bad_edge)}")

    non_hub = [n for n in nodes if n.get("id") != "_github_stars_hub"]
    missing_url = [n.get("id") for n in non_hub if not str(n.get("url") or "").startswith("http")]
    if missing_url:
        issues.append(f"nodes missing valid url: {len(missing_url)}")

    missing_full = [n.get("id") for n in non_hub if "/" not in str(n.get("full_name") or "")]
    if missing_full:
        issues.append(f"nodes missing full_name owner/repo: {len(missing_full)}")

    bad_group = [n.get("id") for n in non_hub if n.get("_star_group") not in VALID_GROUPS]
    if bad_group:
        issues.append(f"nodes with invalid _star_group: {len(bad_group)}")

    # Expect star layout: every non-hub node has direct edge from hub.
    hub_id = "_github_stars_hub"
    has_hub_edge = {n.get("id"): False for n in non_hub}
    for e in edges:
        if e.get("from") == hub_id and e.get("to") in has_hub_edge:
            has_hub_edge[e.get("to")] = True
    missing_hub_edge = [nid for nid, ok in has_hub_edge.items() if not ok]
    if missing_hub_edge:
        issues.append(f"nodes missing hub edge: {len(missing_hub_edge)}")

    lines = [
        "# Stars Node Integrity Report",
        "",
        f"- nodes: **{len(nodes)}**",
        f"- non-hub nodes: **{len(non_hub)}**",
        f"- edges: **{len(edges)}**",
        "",
        "## Findings",
    ]
    if issues:
        lines.extend([f"- {x}" for x in issues])
    else:
        lines.append("- none")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}")
    if issues:
        print("Stars integrity FAILED")
        return 1
    print("Stars integrity passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

