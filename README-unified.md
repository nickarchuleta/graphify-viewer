# Unified viewer — implementation breadcrumb

Use this file to **resume work** in a new chat or with Claude Code: it maps what exists in this folder and how it connects.

## File map

| Path | Role |
|------|------|
| `graph_unified.html` | **Main app**: iframes + left view dock + right detail dock + `postMessage` + README `fetch` |
| `readme_render.js` | **`ReadmeSkin`**: strip leading logo/badge HTML, `marked` render, cleanup |
| `graph.html` | Spellbook map (loaded in iframe) |
| `github_stars_mirror.html` | Generated stars graph; `?embed=1` hides chrome and `postMessage`s selection to parent |
| `graph_hub.html` | Redirect to `graph_unified.html` |
| `scripts/render_github_stars_mirror.py` | Builds `github_stars_mirror.html` from stars JSON |

## Architecture

### Layout (`graph_unified.html`)

Flex row: **`[ view-dock | graph-slot | detail-dock ]`**, `100vh`, `overflow: hidden` on `.layout`.

- **Left `view-dock`:** tabs Spellbook / Stars → toggles which iframe has class `on`. Collapsible; `localStorage` key `graphUnifiedDockExpanded`. Keys `1` / `2`.
- **Center `graph-slot`:** `flex: 1; min-width: 0`; iframes `graph.html`, `github_stars_mirror.html?embed=1`.
- **Right `detail-dock`:** spellbook hint vs **Selected repo** + README. Collapsible; `localStorage` `graphUnifiedDetailExpanded`. Keys `[` / `]`.

### README pipeline

- Stars iframe sends: `postMessage({ type: 'stars-node', fullName, url, label, id }, '*')`.
- Parent calls GitHub API raw README, then raw.githubusercontent.com fallback.
- Render: **`ReadmeSkin.render(md, el, marked)`** (not raw `innerHTML` of Markdown).

### Scrolling (right column)

Flex gotcha: children default to `min-height: auto` and grow past the viewport. Fixes:

- `.detail-dock-inner`: `display: flex; flex-direction: column; min-height: 0; overflow: hidden`.
- `.panel`: `flex: 1 1 auto; min-height: 0; overflow-y: auto`.

### README width

`#star-readme` uses overrides so common README wrappers (`max-width`, `article`, etc.) don’t leave a narrow column with empty margin.

### CORS

Serve over **http**, not `file://`, for README fetch.

### Regenerator paths

`scripts/render_github_stars_mirror.py` resolves:

1. If it lives in `…/scripts/` next to `readme_render.js` → repo root `data/master_stars_all.json`, else fallback `~/spellbook_oracle/master_stars_all.json`.
2. If run from `spellbook_oracle/` → legacy `~/graphify-out/github_stars_mirror.html`.

---

*Last aligned with the session that added docks, ReadmeSkin wiring, and scroll fixes.*
