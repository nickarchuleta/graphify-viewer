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
<script src="./stars_live_graph.js"></script>
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
  body.embed .stars-dash {{
    position: fixed; top: 8px; left: 8px; z-index: 30; display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
    font-size: 11px; background: rgba(15, 15, 26, 0.94); border: 1px solid #2a2a4e; padding: 6px 10px; border-radius: 8px;
    max-width: min(380px, 94vw); color: #ccc;
  }}
  body:not(.embed) .stars-dash {{ display: none; }}
  .stars-dash label {{ display: flex; align-items: center; gap: 6px; cursor: pointer; }}
  .stars-dash button {{
    margin: 0; padding: 4px 8px; border-radius: 6px; border: 1px solid #2a2a4e; background: #1a1a2e; color: #e0e0e0;
    cursor: pointer; font-size: 10px;
  }}
  .stars-dash #stars-link-st {{ font-size: 10px; color: #888; min-width: 4em; }}
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
  <strong>GitHub stars</strong> · {len(repos)} repos + hub · Open <a href="./graph_unified.html" style="color:#93c5fd">graph_unified.html</a> (Spellbook + stars, same folder).
</header>
<div class="wrap">
  <div id="graph"></div>
  <div id="stars-dash" class="stars-dash" aria-label="Draw custom links">
    <label><input type="checkbox" id="stars-link-mode"/> Link mode</label>
    <span id="stars-link-st">Off</span>
    <button type="button" id="stars-link-can">Cancel</button>
    <button type="button" id="stars-link-clr">Clear my links</button>
  </div>
  <div id="panel">
    <h2>Selected</h2>
    <div id="info">Click a repo node…</div>
    <div id="readme-local"></div>
  </div>
</div>
<script>
const EMBED = new URLSearchParams(location.search).get('embed') === '1';
if (EMBED) document.body.classList.add('embed');
const STARS_GITHUB_USER = 'nickarchuleta';
const FALLBACK_NODES = {json.dumps(nodes)};
const FALLBACK_EDGES = {json.dumps(edges)};
function starsRawList() {{
  return window.STARS_RAW_NODES_REF || FALLBACK_NODES;
}}
const nodesDS = new vis.DataSet(FALLBACK_NODES.map(n => ({{
  id: n.id, label: n.label, color: n.color, size: n.size, font: n.font, title: n.title,
  _url: n.url || '', _full_name: n.full_name || ''
}})));
const edgesDS = new vis.DataSet(FALLBACK_EDGES.map((e, i) => ({{
  id: i, from: e.from, to: e.to,
  color: {{ opacity: 0.25 }},
  width: 1,
}})));
const STARS_LINKS_KEY = 'starsCustomLinks_v1';
function starsLoadLinks() {{
  try {{ return JSON.parse(localStorage.getItem(STARS_LINKS_KEY) || '[]'); }} catch (e) {{ return []; }}
}}
function starsSaveLinks(rows) {{
  try {{ localStorage.setItem(STARS_LINKS_KEY, JSON.stringify(rows)); }} catch (e) {{}}
}}
function starsHydrateLinks() {{
  const seen = new Set(edgesDS.getIds());
  starsLoadLinks().forEach(function (r) {{
    if (!r || !r.id || !r.from || !r.to) return;
    if (seen.has(r.id)) return;
    if (!nodesDS.get(r.from) || !nodesDS.get(r.to)) return;
    edgesDS.add({{
      id: r.id, from: r.from, to: r.to,
      dashes: [5, 3], width: 2.2,
      color: {{ color: '#a78bfa', opacity: 0.95 }},
      arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
      title: 'Your drawn link',
    }});
    seen.add(r.id);
  }});
}}
starsHydrateLinks();
let starsLinkDraft = null;
function starsLinkOn() {{
  const el = document.getElementById('stars-link-mode');
  return !!(el && el.checked);
}}
function starsLinkSet(msg) {{
  const s = document.getElementById('stars-link-st');
  if (s) s.textContent = msg;
}}
function starsTryLinkClick(nodeId) {{
  if (!EMBED || !starsLinkOn()) return false;
  if (!nodesDS.get(nodeId)) return false;
  if (starsLinkDraft == null) {{
    starsLinkDraft = nodeId;
    starsLinkSet('Pick 2nd node…');
    network.selectNodes([nodeId]);
    return true;
  }}
  if (starsLinkDraft === nodeId) {{
    starsLinkSet('Different node');
    return true;
  }}
  const id = 'stars_l_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  const rows = starsLoadLinks();
  rows.push({{ id: id, from: starsLinkDraft, to: nodeId }});
  starsSaveLinks(rows);
  edgesDS.add({{
    id: id, from: starsLinkDraft, to: nodeId,
    dashes: [5, 3], width: 2.2,
    color: {{ color: '#a78bfa', opacity: 0.95 }},
    arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
    title: 'Your drawn link',
  }});
  starsLinkDraft = null;
  starsLinkSet('Added');
  network.selectNodes([nodeId]);
  if (window.parent !== window) {{
    const nn = nodesDS.get(nodeId);
    const u = nn._url;
    const fn = nn._full_name || '';
    window.parent.postMessage({{ type: 'stars-node', fullName: fn, url: u || '', label: nn.label || nodeId, id: nodeId }}, '*');
  }}
  return true;
}}
(function starsDashBind() {{
  const lm = document.getElementById('stars-link-mode');
  if (lm) lm.addEventListener('change', function () {{
    starsLinkDraft = null;
    starsLinkSet(lm.checked ? 'Pick first…' : 'Off');
  }});
  const c = document.getElementById('stars-link-can');
  if (c) c.addEventListener('click', function () {{
    starsLinkDraft = null;
    starsLinkSet(starsLinkOn() ? 'Pick first…' : 'Off');
  }});
  const x = document.getElementById('stars-link-clr');
  if (x) x.addEventListener('click', function () {{
    starsSaveLinks([]);
    edgesDS.getIds().filter(function (id) {{ return String(id).indexOf('stars_l_') === 0; }})
      .forEach(function (id) {{ try {{ edgesDS.remove(id); }} catch (e) {{}} }});
    starsLinkDraft = null;
    starsLinkSet(starsLinkOn() ? 'Pick first…' : 'Off');
  }});
}})();
const container = document.getElementById('graph');
const network = new vis.Network(container, {{ nodes: nodesDS, edges: edgesDS }}, {{
  physics: {{
    enabled: true,
    solver: 'forceAtlas2Based',
    forceAtlas2Based: {{
      gravitationalConstant: -88,
      centralGravity: 0.018,
      springLength: 88,
      springConstant: 0.065,
      damping: 0.52,
      avoidOverlap: 0.92,
    }},
    stabilization: {{ iterations: 420, fit: true, updateInterval: 25 }},
  }},
  interaction: {{
    hover: true, tooltipDelay: 90, hideEdgesOnDrag: true, hideEdgesOnZoom: true,
    navigationButtons: false,
    zoomSpeed: 0.32, keyboard: false,
  }},
  nodes: {{ shape: 'dot', borderWidth: 1.5 }},
  edges: {{ smooth: {{ type: 'continuous', roundness: 0.2 }}, selectionWidth: 3 }},
}});
function spellbookStarsFit() {{
  try {{
    network.fit({{ padding: 72, animation: {{ duration: 420, easingFunction: 'easeInOutQuad' }} }});
  }} catch (e) {{}}
}}
function spellbookStarsRefit() {{
  try {{ network.redraw(); }} catch (e) {{}}
  spellbookStarsFit();
}}
function spellbookStarsMaybeFitWhenSized() {{
  const w = container.clientWidth;
  const h = container.clientHeight;
  if (w > 48 && h > 48) spellbookStarsRefit();
}}
function spellbookStarsReshuffle() {{
  network.setOptions({{ physics: {{ enabled: true }} }});
  network.startSimulation();
  window.clearTimeout(window.__starsShuffleT);
  window.__starsShuffleT = window.setTimeout(() => {{
    try {{ network.stopSimulation(); }} catch (e) {{}}
    network.setOptions({{ physics: {{ enabled: false }} }});
    setTimeout(spellbookStarsFit, 40);
  }}, 5000);
}}
network.once('stabilizationIterationsDone', () => {{
  network.setOptions({{ physics: {{ enabled: false }} }});
  if (EMBED) {{
    setTimeout(spellbookStarsMaybeFitWhenSized, 50);
    let tries = 0;
    const iv = setInterval(() => {{
      tries += 1;
      spellbookStarsMaybeFitWhenSized();
      if ((container.clientWidth > 48 && container.clientHeight > 48) || tries > 45) clearInterval(iv);
    }}, 120);
  }} else {{
    setTimeout(spellbookStarsFit, 50);
  }}
}});
if (EMBED) {{
  try {{
    new ResizeObserver(() => spellbookStarsMaybeFitWhenSized()).observe(container);
  }} catch (e) {{}}
}}
window.addEventListener('message', (ev) => {{
  const d = ev.data;
  if (!d || typeof d !== 'object') return;
  if (d.type === 'stars-refit') {{
    setTimeout(spellbookStarsRefit, 0);
    setTimeout(spellbookStarsRefit, 80);
    return;
  }}
  if (d.type === 'stars-shuffle') spellbookStarsReshuffle();
  if (d.type === 'stars-community-apply' && Array.isArray(d.keywords)) {{
    const kws = d.keywords.map((k) => String(k).toLowerCase().trim()).filter(Boolean);
    const updates = starsRawList().map((n) => {{
      if (n.id === '_github_stars_hub') return {{ id: n.id, hidden: false }};
      const blob = (
        String(n.full_name || '') + ' ' + String(n.label || '') + ' ' + String(n.title || '')
      ).toLowerCase();
      const hit = kws.some((kw) => blob.indexOf(kw) !== -1);
      return {{ id: n.id, hidden: !hit }};
    }});
    nodesDS.update(updates);
    setTimeout(spellbookStarsFit, 60);
  }}
  if (d.type === 'stars-community-clear') {{
    nodesDS.update(starsRawList().map((n) => ({{ id: n.id, hidden: false }})));
    setTimeout(spellbookStarsFit, 60);
  }}
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
  if (p.nodes.length && EMBED && starsTryLinkClick(p.nodes[0])) return;
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

function starsMapVisNodes(raw) {{
  return raw.map(n => ({{
    id: n.id, label: n.label, color: n.color, size: n.size, font: n.font, title: n.title,
    _url: n.url || '', _full_name: n.full_name || ''
  }}));
}}
function starsMapVisEdges(raw) {{
  return raw.map((e, i) => ({{
    id: i, from: e.from, to: e.to,
    color: {{ opacity: 0.25 }},
    width: 1,
  }}));
}}

(async function starsLiveRefresh() {{
  if (typeof StarsLive === 'undefined') return;
  try {{
    const api = await StarsLive.fetchAllStarred(STARS_GITHUB_USER);
    if (!api || api.length === 0) return;
    const b = await StarsLive.buildNodesEdges(api);
    window.STARS_RAW_NODES_REF = b.nodes;
    nodesDS.clear();
    edgesDS.clear();
    nodesDS.add(starsMapVisNodes(b.nodes));
    edgesDS.add(starsMapVisEdges(b.edges));
    starsHydrateLinks();
    network.setData({{ nodes: nodesDS, edges: edgesDS }});
    network.setOptions({{ physics: {{ enabled: true }} }});
    network.startSimulation();
    network.once('stabilizationIterationsDone', () => {{
      network.setOptions({{ physics: {{ enabled: false }} }});
      setTimeout(spellbookStarsFit, 50);
      if (EMBED) setTimeout(spellbookStarsMaybeFitWhenSized, 80);
    }});
    const st = document.getElementById('stars-link-st');
    if (st && !starsLinkOn()) st.textContent = 'Live · ' + b.nodes.length + ' nodes';
  }} catch (err) {{
    console.warn('[stars] Live refresh skipped:', err);
    const st = document.getElementById('stars-link-st');
    if (st && !starsLinkOn()) st.textContent = 'Snapshot (API limit?)';
  }}
}})();
</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_page, encoding="utf-8")
    print(f"Wrote {OUT} ({len(nodes)} nodes, {len(edges)} edges)")


if __name__ == "__main__":
    main()
