# Spellbook + GitHub stars — unified viewer

Fork of https://github.com/raufer/graphify repo built out with Claude Code, Grok and Cursor to accomodate my specific (growing) tech stack.

<img width="1710" height="1112" alt="Screenshot 2026-04-12 at 3 55 10 PM" src="https://github.com/user-attachments/assets/b764b940-9ad8-4eb2-b99d-35a7cf6480b3" />

![Screenshot_2026-04-12_at_3 43 36_PM-d68192af-9140-](https://github.com/user-attachments/assets/24f4a799-cb34-4f79-9e56-bcf447b98445)

![Screenshot_2026-04-12_at_3 44 17_PM-570df729-7b81-](https://github.com/user-attachments/assets/37704e54-5cec-4a6c-8dc2-1af5e29e3d31)

![Screenshot_2026-04-12_at_3 43 06_PM-46c1846c-6384-](https://github.com/user-attachments/assets/3a744dda-db87-4b84-b4ba-835a6affd440)






Static HTML tools that combine a **Spellbook knowledge graph** and a **GitHub stars “nebula”** in one tab, with **clean README** rendering in the parent page.

**Live repo:** [github.com/nickarchuleta/graphify-viewer](https://github.com/nickarchuleta/graphify-viewer)

## Quick start

```bash
git clone https://github.com/nickarchuleta/graphify-viewer.git
cd graphify-viewer
python3 -m http.server 8765
```

Open **http://localhost:8765/graph_unified.html** (use a local server so README `fetch` works; `file://` often hits CORS).

- **Left strip:** switch **Spellbook map** ↔ **Stars nebula** (collapsible).
- **Right strip:** hints + **Selected repo** README when viewing stars (collapsible).
- **Keys:** `1` / `2` switch views; `[` / `]` collapse/expand the right details panel.

## Files

| File | Purpose |
|------|---------|
| `graph_unified.html` | Main shell: iframes + docks + README pipeline |
| `readme_render.js` | Strip badge HTML, render Markdown (`ReadmeSkin`) |
| `graph.html` | Spellbook graph (your graphify export) |
| `github_stars_mirror.html` | Stars hub-and-spoke graph (regenerate from JSON) |
| `graph_hub.html` | Redirects to `graph_unified.html` |

Full architecture and recovery notes: **[README-unified.md](./README-unified.md)**.

## Regenerate stars mirror

Place `master_stars_all.json` (see `data/README.md`), then:

```bash
python3 scripts/render_github_stars_mirror.py
```

The script also runs from `~/spellbook_oracle/` if you keep stars JSON there (see script docstring).

## Publishing updates (you)

After editing files in your clone:

```bash
cd graphify-viewer   # or ~/graphify-out if that’s your working copy
git add -A
git commit -m "Describe your change"
git push
```

**First-time push from a new machine:** create an empty repo on GitHub, then `git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git` and `git push -u origin main`. Use a [Personal Access Token](https://github.com/settings/tokens) if HTTPS asks for a password.

## License

MIT — see [LICENSE](./LICENSE).
