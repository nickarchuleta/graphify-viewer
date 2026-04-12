# Privacy notes for this repo

## What we scrubbed for a safe public repo

- **`graph.html`:** `SPELLBOOK_FILES_ROOT` is **empty by default**, so the UI shows **relative** `source_file` paths only—no baked-in home directory. To restore “Open file” / `file://` links on **your** machine, set before the graph runs, e.g. in DevTools console:  
  `window.__SPELLBOOK_FILES_ROOT = "/Users/yourname/"`  
  or inject a one-line script when you open the file locally.
- **`github_stars_mirror.html`:** Header no longer links to a specific GitHub profile by default (regenerate via `scripts/render_github_stars_mirror.py`).
- **`data/master_stars_all.json`:** **gitignored** so a full export of starred repos is not committed by accident.

## What may still be sensitive

- **`graph.html` embedded graph data** may include **names, repo titles, and relative project paths** from your graphify export—review if you fork this publicly with your own `graph.html`.
- **Screenshots** in `docs/screenshots/` were chosen to avoid obvious system paths; if you replace them, avoid captures that show your username in a file path or Finder.
- **Git history** may list committer names/emails—use `git log` and [GitHub email privacy](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address) if needed.

## Files not intended for git (local only)

- `GRAPH_REPORT.md`, large `graph.json` caches, etc.—see `.gitignore`.
