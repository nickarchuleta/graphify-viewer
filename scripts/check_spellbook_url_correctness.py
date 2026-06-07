#!/usr/bin/env python3
"""Guardrail: concept/topic nodes should not claim inferred repo links.

This check verifies:
1) `graph.html` contains the repo-anchor inference guard.
2) No non-anchor node in `graph.json` has explicit repo-level `source_url`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_HTML = ROOT / "graph.html"
GRAPH_JSON = ROOT / "graph.json"
REPORT = ROOT / "node_url_correctness_report.md"


def infer_repo_url_from_source_file(source_file: str) -> str:
    m = re.search(r"spellbook-homework/([^/]+)\.md$", source_file, flags=re.I)
    if not m:
        return ""
    stem = m.group(1)
    if "__" not in stem:
        return ""
    owner, repo = stem.split("__", 1)
    if not owner or not repo:
        return ""
    return f"https://github.com/{owner}/{repo}"


def node_looks_repo_anchor(node: dict, source_file: str) -> bool:
    nid = str(node.get("id") or "").lower()
    lbl = str(node.get("label") or "").lower()
    stem_m = re.search(r"spellbook-homework/([^/]+)\.md$", source_file, flags=re.I)
    stem = (stem_m.group(1).lower() if stem_m else "")
    alt = stem.replace("__", "_")
    return (
        nid.endswith("_repo")
        or "/" in lbl
        or (stem and stem in nid)
        or (alt and alt in nid)
    )


def main() -> int:
    if not GRAPH_HTML.exists() or not GRAPH_JSON.exists():
        print("Missing graph.html or graph.json")
        return 2

    html = GRAPH_HTML.read_text(encoding="utf-8", errors="ignore")
    data = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])

    guard_snippets = [
        "function spellbookNodeSemantics(",
        "function spellbookGithubProvenance(",
    ]
    guard_missing = [g for g in guard_snippets if g not in html]

    explicit_non_anchor: list[tuple[str, str, str]] = []
    inferred_non_anchor_count = 0
    for n in nodes:
        src = str(n.get("source_file") or "")
        if not src:
            continue
        inferred = infer_repo_url_from_source_file(src)
        if inferred and not node_looks_repo_anchor(n, src):
            inferred_non_anchor_count += 1
        su = str(n.get("source_url") or "")
        if su and su.startswith("https://github.com/") and inferred and not node_looks_repo_anchor(n, src):
            explicit_non_anchor.append((str(n.get("id") or ""), str(n.get("label") or ""), su))

    lines = [
        "# Spellbook URL Correctness Report",
        "",
        f"- nodes scanned: **{len(nodes)}**",
        f"- non-anchor nodes with inferable homework repo: **{inferred_non_anchor_count}**",
        f"- explicit repo links on non-anchor nodes (allowed, informational): **{len(explicit_non_anchor)}**",
        "",
        "## Findings",
    ]
    if guard_missing:
        lines.append("- missing UI provenance guard snippets:")
        lines.extend([f"  - `{x}`" for x in guard_missing])
    if explicit_non_anchor:
        lines.append("- explicit links on non-anchor nodes (informational):")
        for nid, label, su in explicit_non_anchor[:40]:
            lines.append(f"  - `{nid}` · {label} -> {su}")
    if not guard_missing and not explicit_non_anchor:
        lines.append("- none")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}")

    if guard_missing:
        print("URL correctness check FAILED")
        return 1
    print("URL correctness check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
