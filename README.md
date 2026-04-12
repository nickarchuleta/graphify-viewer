# Spellbook + GitHub stars — unified viewer

![Screenshot_2026-04-12_at_3 44 17_PM-570df729-7b81-](https://github.com/user-attachments/assets/37704e54-5cec-4a6c-8dc2-1af5e29e3d31)

![Screenshot_2026-04-12_at_3 43 36_PM-d68192af-9140-](https://github.com/user-attachments/assets/24f4a799-cb34-4f79-9e56-bcf447b98445)

![Screenshot_2026-04-12_at_3 43 06_PM-46c1846c-6384-](https://github.com/user-attachments/assets/3a744dda-db87-4b84-b4ba-835a6affd440)

![Screenshot_2026-04-12_at_3 42 49_PM-1255ff39-bf5b-](https://github.com/user-attachments/assets/eb23fd48-9c88-418a-a36c-a311a0e9199e)



Static HTML tools that combine a **Spellbook knowledge graph** and a **GitHub stars “nebula”** in one tab, with **clean README** rendering in the parent page.


## Quick start

```bash
git clone https://github.com/YOUR_USER/REPO_NAME.git
cd REPO_NAME
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

## Push to your GitHub

`gh` CLI isn’t required. From this folder (after `git` is configured with your name/email):

1. Create a **new empty repo** on GitHub (no README) — e.g. `graphify-viewer` or `spellbook-stars-ui`.
2. Add the remote and push:

```bash
cd /path/to/graphify-out   # this repo root
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Use **SSH** instead if your keys work: `git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git`

If `git push` asks for credentials, use a [Personal Access Token](https://github.com/settings/tokens) as the password for HTTPS, or run `ssh-add` for SSH.

## License

MIT — see [LICENSE](./LICENSE).
