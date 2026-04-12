# Stars list JSON

Place your exported catalog here as:

**`master_stars_all.json`**

Shape (minimal): top-level `{ "repos": [ { "full_name", "html_url", "description", "stars", "language", ... } ] }`.

This file is **gitignored** by default so you don’t accidentally publish your full stars list. Remove the ignore line in `.gitignore` if you want it in the repo (prefer a **private** repo for that).
