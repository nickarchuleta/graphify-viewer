#!/usr/bin/env python3
"""
Build a 1:1 vis-network HTML from master_stars_all.json (your GitHub stars list).
No graphify / LLM — just your catalog → nodes + hub edges so layout is readable.

Output:
  - When run from the graphify repo: ./github_stars_mirror.html next to readme_render.js
  - Legacy: ~/graphify-out/github_stars_mirror.html when run from spellbook_oracle/

Usage:
  python3 ~/spellbook_oracle/render_github_stars_mirror.py
  python3 scripts/render_github_stars_mirror.py   # from graphify-out repo clone
"""
from __future__ import annotations

import html
import json
import hashlib
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve()
_HOME = Path.home()
# graphify-out repo layout: graphify-out/scripts/this.py + ../readme_render.js
if _SCRIPT.parent.name == "scripts" and (_SCRIPT.parent.parent / "readme_render.js").is_file():
    _REPO = _SCRIPT.parent.parent
    MASTER = _REPO / "data" / "master_stars_all.json"
    if not MASTER.is_file():
        MASTER = _HOME / "spellbook_oracle" / "master_stars_all.json"
    OUT = _REPO / "github_stars_mirror.html"
else:
    MASTER = _HOME / "spellbook_oracle" / "master_stars_all.json"
    OUT = _HOME / "graphify-out" / "github_stars_mirror.html"

if not MASTER.is_file():
    print(f"Missing stars JSON: {MASTER}", file=sys.stderr)
    print("Add data/master_stars_all.json (see data/README.md) or ~/spellbook_oracle/master_stars_all.json", file=sys.stderr)
    sys.exit(1)


def _color_for(s: str) -> str:
    h = hashlib.sha256(s.encode()).hexdigest()
    return f"#{h[:6]}"


def main() -> None:
    data = json.loads(MASTER.read_text(encoding="utf-8"))
    repos = data.get("repos") or []
    nodes = []
    edges = []
    hub_id = "_github_stars_hub"
    nodes.append(
        {
            "id": hub_id,
            "label": "★ GitHub stars",
            "color": {"background": "#f59e0b", "border": "#d97706"},
            "size": 28,
            "font": {"size": 14, "color": "#fff"},
            "title": html.escape(
                f"Hub — {len(repos)} repos from {MASTER.name}. Click a node for GitHub."
            ),
        }
    )
    for i, r in enumerate(repos):
        fn = r.get("full_name") or ""
        if not fn:
            continue
        nid = "star_" + fn.replace("/", "_").replace(".", "_")
        url = r.get("html_url") or f"https://github.com/{fn}"
        label = fn.split("/")[-1][:40] if "/" in fn else fn[:40]
        desc = (r.get("description") or "")[:180]
        stars = r.get("stars") or 0
        lang = r.get("language") or "—"
        title = f"{fn}\n{stars}★ · {lang}\n{desc}"
        col = _color_for(fn)
        nodes.append(
            {
                "id": nid,
                "label": label,
                "full_name": fn,
                "color": {"background": col, "border": col},
                "size": 10 + min(18, (int(stars) ** 0.33) if stars else 8),
                "font": {"size": 0},
                "title": html.escape(title),
                "url": url,
            }
        )
        edges.append({"from": hub_id, "to": nid})

    html_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>GitHub stars mirror ({len(repos)} repos)</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="./readme_render.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ background: #0f0f1a; color: #e0e0e0; font-family: system-ui, sans-serif; height: 100vh; display: flex; flex-direction: column; }}
  header {{ padding: 10px 14px; border-bottom: 1px solid #2a2a4e; font-size: 13px; color: #aaa; }}
  header a {{ color: #60a5fa; }}
  body.embed header {{ display: none; }}
  #graph {{ flex: 1; min-height: 0; touch-action: none; }}
  #panel {{ width: min(400px, 42vw); border-left: 1px solid #2a2a4e; padding: 12px 14px; font-size: 12px; overflow: auto; min-width: 0; }}
  body.embed #panel {{ display: none; }}
  body.embed .wrap {{ flex: 1; }}
  #panel h2 {{ font-size: 11px; text-transform: uppercase; color: #888; margin-bottom: 8px; }}
  #panel a {{ color: #60a5fa; word-break: break-all; }}
  .wrap {{ display: flex; flex: 1; min-height: 0; }}
  #readme-local {{ margin-top: 10px; font-size: 12px; line-height: 1.5; color: #ccc; max-height: 55vh; overflow: auto; width: 100%; min-width: 0; }}
  #readme-local.readme-prose img {{ max-width: 100% !important; height: auto !important; }}
  #readme-local.readme-prose h1 {{ font-size: 15px; color: #f0f0f0; margin: 0.5em 0 0.25em; }}
  #readme-local.readme-prose h2, #readme-local.readme-prose h3 {{ font-size: 13px; color: #e8e8e8; }}
  #readme-local.readme-prose pre, #readme-local.readme-prose code {{ font-size: 10px; }}
</style>
</head>
<body>
<header>
  <strong>Stars</strong> · <a href="https://github.com/nickarchuleta?tab=stars" target="_blank" rel="noopener">nickarchuleta</a>
  · {len(repos)} repos + hub · Use <a href="./graph_unified.html" style="color:#93c5fd">graph_unified.html</a> for spellbook + stars in one window.
</header>
<div class="wrap">
  <div id="graph"></div>
  <div id="panel">
    <h2>Selected</h2>
    <div id="info">Click a repo node…</div>
    <div id="readme-local"></div>
  </div>
</div>
<script>
const EMBED = new URLSearchParams(location.search).get('embed') === '1';
if (EMBED) document.body.classList.add('embed');
const RAW_NODES = {json.dumps(nodes)};
const RAW_EDGES = {json.dumps(edges)};
const nodesDS = new vis.DataSet(RAW_NODES.map(n => ({{
  id: n.id, label: n.label, color: n.color, size: n.size, font: n.font, title: n.title,
  _url: n.url || '', _full_name: n.full_name || ''
}})));
const edgesDS = new vis.DataSet(RAW_EDGES.map((e, i) => ({{
  id: i, from: e.from, to: e.to,
  color: {{ opacity: 0.25 }},
  width: 1,
}})));
const container = document.getElementById('graph');
const network = new vis.Network(container, {{ nodes: nodesDS, edges: edgesDS }}, {{
  physics: {{
    enabled: true,
    solver: 'forceAtlas2Based',
    forceAtlas2Based: {{ gravitationalConstant: -80, springLength: 140, springConstant: 0.06, damping: 0.45 }},
    stabilization: {{ iterations: 120, fit: true }},
  }},
  interaction: {{
    hover: true, tooltipDelay: 80, hideEdgesOnDrag: true, hideEdgesOnZoom: true,
    zoomSpeed: 0.32, keyboard: false,
  }},
  nodes: {{ shape: 'dot', borderWidth: 1.2 }},
  edges: {{ smooth: {{ type: 'continuous' }} }},
}});
network.once('stabilizationIterationsDone', () => {{
  network.setOptions({{ physics: {{ enabled: false }} }});
}});
async function fetchReadmeMd(owner, repo) {{
  const tryUrls = [
    'https://api.github.com/repos/' + encodeURIComponent(owner) + '/' + encodeURIComponent(repo) + '/readme',
  ];
  for (const url of tryUrls) {{
    try {{
      const r = await fetch(url, {{ headers: {{ 'Accept': 'application/vnd.github.raw' }} }});
      if (r.ok) return await r.text();
    }} catch (e) {{}}
  }}
  const raw = 'https://raw.githubusercontent.com/' + owner + '/' + repo + '/HEAD/README.md';
  try {{
    const r = await fetch(raw);
    if (r.ok) return await r.text();
  }} catch (e) {{}}
  return null;
}}
network.on('click', async (p) => {{
  if (!p.nodes.length) return;
  const id = p.nodes[0];
  const n = nodesDS.get(id);
  const u = n._url;
  const fn = n._full_name || '';
  if (EMBED && window.parent !== window) {{
    window.parent.postMessage({{ type: 'stars-node', fullName: fn, url: u || '', label: n.label || id, id }}, '*');
    return;
  }}
  const rd = document.getElementById('readme-local');
  if (rd) {{ rd.textContent = ''; rd.innerHTML = '<span style=color:#666>Loading README…</span>'; }}
  if (!u) {{
    if (document.getElementById('info')) document.getElementById('info').innerHTML = '<code>' + id + '</code> (hub)';
    if (rd) rd.innerHTML = '';
    return;
  }}
  const head = '<div><b>' + (n.label || id) + '</b></div><p><a href=\"' + u + '\" target=\"_blank\" rel=\"noopener\">Open on GitHub</a></p>';
  if (document.getElementById('info')) document.getElementById('info').innerHTML = head;
  let md = '';
  if (fn && fn.indexOf('/') !== -1) {{
    const [o, r] = fn.split('/', 2);
    md = await fetchReadmeMd(o, r);
  }}
  if (rd) {{
    if (md && typeof ReadmeSkin !== 'undefined' && typeof marked !== 'undefined') {{
      ReadmeSkin.render(md, rd, marked);
    }} else if (md) {{
      rd.textContent = md;
    }} else {{
      rd.innerHTML = '<span style=color:#888>No README fetched (rate limit / private / CORS).</span>';
    }}
  }}
}});
</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_page, encoding="utf-8")
    print(f"Wrote {OUT} ({len(nodes)} nodes, {len(edges)} edges)")


if __name__ == "__main__":
    main()
