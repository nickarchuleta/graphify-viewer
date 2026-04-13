#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.home() / "graphify-out"
GRAPH_JSON = ROOT / "graph.json"
GRAPH_HTML = ROOT / "graph.html"
STARS_HTML = ROOT / "github_stars_mirror.html"
OVERRIDES_JSON = ROOT / "stars_group_overrides.json"
REPORT = ROOT / "node_integrity_extreme_report.md"

VALID_STAR_GROUPS = {"mac", "ai_code", "agents", "local_ai", "graphs", "browser", "data", "sec", "misc"}


def parse_const_json(html: str, name: str):
    m = re.search(rf"const {name} = (.*?);\n", html, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def main() -> int:
    hard_failures: list[str] = []
    soft_findings: list[str] = []

    graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    nodes = graph.get("nodes") or []
    links = graph.get("links") or []

    node_ids = [n.get("id") for n in nodes]
    dup_node_ids = [k for k, v in Counter(node_ids).items() if v > 1 and k is not None]
    if dup_node_ids:
        hard_failures.append(f"duplicate graph.json node ids: {len(dup_node_ids)}")
    node_id_set = set(node_ids)

    broken_links = []
    for e in links:
        s = e.get("source")
        t = e.get("target")
        if s not in node_id_set or t not in node_id_set:
            broken_links.append((s, t))
    if broken_links:
        hard_failures.append(f"graph.json links with missing endpoint: {len(broken_links)}")

    missing_community = [n.get("id") for n in nodes if "community" not in n or n.get("community") is None]
    if missing_community:
        hard_failures.append(f"nodes missing community id: {len(missing_community)}")

    graph_html = GRAPH_HTML.read_text(encoding="utf-8")
    raw_nodes = parse_const_json(graph_html, "RAW_NODES") or []
    raw_edges = parse_const_json(graph_html, "RAW_EDGES") or []
    legend = parse_const_json(graph_html, "LEGEND") or []

    if len(raw_nodes) != len(nodes):
        hard_failures.append(f"graph.html RAW_NODES ({len(raw_nodes)}) != graph.json nodes ({len(nodes)})")
    if len(raw_edges) != len(links):
        hard_failures.append(f"graph.html RAW_EDGES ({len(raw_edges)}) != graph.json links ({len(links)})")

    legend_cids = {int(x.get("cid")) for x in legend if x.get("cid") is not None}
    bad_cid_nodes = [n.get("id") for n in raw_nodes if int(n.get("community", -999999)) not in legend_cids]
    if bad_cid_nodes:
        hard_failures.append(f"RAW_NODES community ids not present in LEGEND: {len(bad_cid_nodes)}")

    stars_html = STARS_HTML.read_text(encoding="utf-8")
    fallback_nodes = parse_const_json(stars_html, "FALLBACK_NODES") or []
    fallback_edges = parse_const_json(stars_html, "FALLBACK_EDGES") or []

    hub_nodes = [n for n in fallback_nodes if n.get("id") == "_github_stars_hub"]
    if len(hub_nodes) != 1:
        hard_failures.append(f"stars mirror hub node count != 1 (got {len(hub_nodes)})")

    fallback_ids = {n.get("id") for n in fallback_nodes}
    broken_star_edges = [
        e for e in fallback_edges if e.get("from") not in fallback_ids or e.get("to") not in fallback_ids
    ]
    if broken_star_edges:
        hard_failures.append(f"stars fallback edges with missing endpoint: {len(broken_star_edges)}")

    bad_groups = [
        n.get("id")
        for n in fallback_nodes
        if n.get("id") != "_github_stars_hub" and n.get("_star_group") not in VALID_STAR_GROUPS
    ]
    if bad_groups:
        hard_failures.append(f"stars nodes with invalid _star_group: {len(bad_groups)}")

    if OVERRIDES_JSON.is_file():
        overrides = json.loads(OVERRIDES_JSON.read_text(encoding="utf-8"))
        bad_override_keys = [k for k in overrides if str(k).strip().lower() != str(k).strip()]
        bad_override_groups = [k for k, v in overrides.items() if str(v) not in VALID_STAR_GROUPS]
        if bad_override_keys:
            soft_findings.append(f"override keys not normalized lowercase: {len(bad_override_keys)}")
        if bad_override_groups:
            hard_failures.append(f"override entries with invalid group id: {len(bad_override_groups)}")

    lines = [
        "# Extreme Node Integrity Report",
        "",
        f"- graph.json nodes: **{len(nodes)}**",
        f"- graph.json links: **{len(links)}**",
        f"- graph.html RAW_NODES: **{len(raw_nodes)}**",
        f"- graph.html RAW_EDGES: **{len(raw_edges)}**",
        f"- stars fallback nodes: **{len(fallback_nodes)}**",
        f"- stars fallback edges: **{len(fallback_edges)}**",
        "",
        "## Hard failures",
    ]
    if hard_failures:
        lines.extend([f"- {x}" for x in hard_failures])
    else:
        lines.append("- none")
    lines += ["", "## Soft findings"]
    if soft_findings:
        lines.extend([f"- {x}" for x in soft_findings])
    else:
        lines.append("- none")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}")
    if hard_failures:
        print("Integrity check FAILED")
        return 1
    print("Integrity check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

