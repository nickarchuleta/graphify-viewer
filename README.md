# Spellbook + GitHub stars — unified viewer

<<<<<<< HEAD
Fork of https://github.com/raufer/graphify repo built out with Claude Code, Grok and Cursor to accomodate my specific (growing) tech stack.

<img width="1710" height="1112" alt="Screenshot 2026-04-12 at 3 55 10 PM" src="https://github.com/user-attachments/assets/b764b940-9ad8-4eb2-b99d-35a7cf6480b3" />

![Screenshot_2026-04-12_at_3 43 36_PM-d68192af-9140-](https://github.com/user-attachments/assets/24f4a799-cb34-4f79-9e56-bcf447b98445)

![Screenshot_2026-04-12_at_3 44 17_PM-570df729-7b81-](https://github.com/user-attachments/assets/37704e54-5cec-4a6c-8dc2-1af5e29e3d31)

![Screenshot_2026-04-12_at_3 43 06_PM-46c1846c-6384-](https://github.com/user-attachments/assets/3a744dda-db87-4b84-b4ba-835a6affd440)






Static HTML tools that combine a **Spellbook knowledge graph** and a **GitHub stars “nebula”** in one tab, with **clean README** rendering in the parent page.
=======
**Source repo:** [github.com/nickarchuleta/graphify-viewer](https://github.com/nickarchuleta/graphify-viewer)
>>>>>>> e832845 (Docs: thesis, screenshots, privacy sweep; redact graph data; neutral stars header)

This is a **local-first** HTML bundle: there is no hosted app URL. You clone or download the repo and open the files from disk (or a tiny static server).

## Why this exists

Flat lists of repos don’t match how a lot of us think. This viewer is for **fast capability assessment**: see your **Spellbook** (ideas, docs, wiring) and your **GitHub stars** as **living graphs**, drag nodes around, cluster by community, and read READMEs in context—closer to **flipping through samples in Ableton** than scrolling a spreadsheet. Same energy as *“what if I put this hip-hop loop with that dubstep bass?”*—**serendipity**: *what if I combine this with that?* Built for brains that like **non-linear, visual remixing** over linear bookmarks.

<p align="center">
  <img src="./docs/screenshots/stars-nebula.png" alt="GitHub stars hub-and-spoke graph" width="720" />
  <br />
  <sub>Stars “nebula”: one hub, hundreds of repos, colored by hash—scan your whole star field at once.</sub>
</p>

<p align="center">
  <img src="./docs/screenshots/unified-readme.png" alt="Unified viewer with README panel" width="720" />
  <br />
  <sub>Unified viewer: Spellbook ↔ Stars on the left, cleaned README on the right (serve over http for GitHub API).</sub>
</p>

## Run it (your machine)

**Option A — same as you’ve been using:** open the file directly (some features may still work):

`file:///…/graphify-out/graph_unified.html`  
(on your Mac, that is often under `~/graphify-out/graph_unified.html`.)

**Option B — recommended:** local server so README fetch from GitHub works reliably:

```bash
git clone https://github.com/nickarchuleta/graphify-viewer.git
cd graphify-viewer
python3 -m http.server 8765
```

Then open **http://localhost:8765/graph_unified.html**

- **Left strip:** **Spellbook map** ↔ **Stars nebula** (collapsible).
- **Right strip:** hints + **Selected repo** README in stars mode (collapsible, scrollable).
- **Keys:** `1` / `2` switch views; `[` / `]` collapse/expand the right panel.

## Files

| File | Purpose |
|------|---------|
| `graph_unified.html` | Main shell: iframes + docks + README pipeline |
| `readme_render.js` | Strip badge HTML, render Markdown (`ReadmeSkin`) |
| `graph.html` | Spellbook graph (your graphify export) |
| `github_stars_mirror.html` | Stars hub-and-spoke graph (regenerate from JSON) |
| `graph_hub.html` | Redirects to `graph_unified.html` |

Architecture / recovery notes: **[README-unified.md](./README-unified.md)** · **Privacy / what’s safe to publish:** **[docs/PRIVACY.md](./docs/PRIVACY.md)**

## Regenerate stars mirror

Put `master_stars_all.json` under `data/` (see `data/README.md`), then:

```bash
python3 scripts/render_github_stars_mirror.py
```

## Publishing updates

```bash
git add -A && git commit -m "Your message" && git push
```

## License

MIT — see [LICENSE](./LICENSE).
