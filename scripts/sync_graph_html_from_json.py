#!/usr/bin/env python3
"""Embed graph.json nodes/links into graph.html as RAW_NODES, RAW_EDGES, LEGEND."""

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH_JSON = ROOT / "graph.json"
GRAPH_HTML = ROOT / "graph.html"

# Tableau 10 / extended — stable, high-contrast cycle for cluster colors.
_PALETTE = [
    "#4E79A7",
    "#F28E2B",
    "#E15759",
    "#76B7B2",
    "#59A14F",
    "#EDC948",
    "#B07AA1",
    "#FF9DA7",
    "#9C755F",
    "#BAB0AC",
    "#D37295",
    "#86BCB6",
    "#79706E",
    "#FABFD2",
    "#666666",
    "#7293CB",
    "#E7298A",
    "#66A61E",
    "#E6AB02",
    "#A6761D",
    "#666666",
    "#CC79A7",
    "#56B4E9",
    "#F0E442",
    "#0072B2",
    "#D55E00",
]


def _replace_const(html: str, name: str, obj: object) -> str:
    blob = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    pat = rf"(const {re.escape(name)} = )(.*?)(;\n)"
    m = re.search(pat, html, flags=re.S)
    if not m:
        raise ValueError(f"Could not find const {name} in graph.html")
    return html[: m.start()] + m.group(1) + blob + m.group(3) + html[m.end() :]


def main() -> int:
    if not GRAPH_JSON.is_file():
        print(f"Missing {GRAPH_JSON}", file=sys.stderr)
        return 1
    if not GRAPH_HTML.is_file():
        print(f"Missing {GRAPH_HTML}", file=sys.stderr)
        return 1
    data = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    nodes = data.get("nodes") or []
    links = data.get("links") or []

    deg = Counter()
    for e in links:
        s, t = e.get("source"), e.get("target")
        if s is not None:
            deg[s] += 1
        if t is not None:
            deg[t] += 1

    by_comm: dict[int, int] = Counter()
    nodes_by_comm: dict[int, list[dict]] = {}
    for n in nodes:
        c = n.get("community")
        if c is None:
            continue
        cid = int(c)
        by_comm[cid] += 1
        nodes_by_comm.setdefault(cid, []).append(n)

    def _legend_label(cid: int, members: list[dict]) -> str:
        """Name a community from its highest-degree repo-style node, else fallback."""
        repoish = [
            m
            for m in members
            if m.get("catalog_category") == "github_star"
            or str(m.get("id") or "").endswith("_repo")
        ]
        pool = repoish if repoish else members
        best = max(pool, key=lambda m: deg.get(m.get("id"), 0))
        lab = str(best.get("label") or "").strip()
        if len(lab) > 44:
            lab = lab[:41] + "…"
        return lab if lab else f"Cluster {cid}"

    legend_rows = []
    for cid in sorted(by_comm.keys()):
        members = nodes_by_comm.get(cid, [])
        legend_rows.append(
            {
                "cid": cid,
                "color": _PALETTE[cid % len(_PALETTE)],
                "label": _legend_label(cid, members),
                "count": by_comm[cid],
            }
        )
    cid_to_label = {r["cid"]: r["label"] for r in legend_rows}
    cid_to_color = {r["cid"]: r["color"] for r in legend_rows}

    raw_nodes = []
    for n in nodes:
        nid = n.get("id")
        lab = n.get("label") or nid
        cid = int(n["community"]) if n.get("community") is not None else -1
        d = deg.get(nid, 0)
        col = cid_to_color.get(cid, "#7aa2ff")
        size = round(8.0 + 4.0 * math.log(d + 1), 1)
        size = max(10.0, min(28.0, size))
        title = str(lab)
        su = n.get("source_url")
        if su:
            title = f"{title}\n{su}"
        raw_nodes.append(
            {
                "id": nid,
                "label": lab,
                "color": {
                    "background": col,
                    "border": col,
                    "highlight": {"background": "#ffffff", "border": col},
                },
                "size": size,
                "font": {"size": 0, "color": "#ffffff"},
                "title": title,
                "community": cid,
                "community_name": cid_to_label.get(cid, f"Cluster {cid}"),
                "source_file": n.get("source_file"),
                "file_type": n.get("file_type"),
                "degree": d,
            }
        )
        if su:
            raw_nodes[-1]["source_url"] = su

    raw_edges = []
    for e in links:
        rel = e.get("relation") or "related"
        conf = str(e.get("confidence") or "UNKNOWN")
        w = float(e.get("confidence_score") or e.get("weight") or 1.0)
        width = max(1.0, min(4.0, 1.0 + w * 2.0))
        raw_edges.append(
            {
                "from": e.get("source"),
                "to": e.get("target"),
                "label": rel,
                "title": f"{rel} [{conf}]",
                "dashes": conf.upper() != "EXTRACTED",
                "width": round(width, 2),
                "color": {"opacity": 0.7},
                "confidence": conf,
            }
        )

    html = GRAPH_HTML.read_text(encoding="utf-8")
    html = _replace_const(html, "RAW_NODES", raw_nodes)
    html = _replace_const(html, "RAW_EDGES", raw_edges)
    html = _replace_const(html, "LEGEND", legend_rows)
    GRAPH_HTML.write_text(html, encoding="utf-8")
    print(f"Updated {GRAPH_HTML} ({len(raw_nodes)} nodes, {len(raw_edges)} edges, {len(legend_rows)} legend rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
