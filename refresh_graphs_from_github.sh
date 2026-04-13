#!/usr/bin/env bash
# Refresh local star catalog + HTML mirrors from GitHub (run before opening graph_unified if you want disk + spellbook stubs in sync).
# Stars nebula in the browser also loads live from the API on each page load.
# After this script, use "Reload graphs" in graph_unified or hard-refresh; saved highlight keywords (localStorage) re-apply when the Stars iframe loads or finishes live fetch.
set -euo pipefail
ORACLE="${SPELLBOOK_ORACLE:-$HOME/spellbook_oracle}"
OUT="${GRAPHIFY_OUT:-$HOME/graphify-out}"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

if [[ -f "$ORACLE/sync_github_stars_homework.py" ]]; then
  python3 "$ORACLE/sync_github_stars_homework.py" --fetch
fi
if [[ -f "$ORACLE/render_github_stars_mirror.py" ]]; then
  python3 "$ORACLE/render_github_stars_mirror.py"
fi
if [[ -f "$ORACLE/rebuild_spellbook_graph.py" ]]; then
  python3 "$ORACLE/rebuild_spellbook_graph.py" || true
fi
if [[ -f "$ORACLE/fix_graph_html_spellbook.py" ]]; then
  python3 "$ORACLE/fix_graph_html_spellbook.py" || true
fi
if [[ -f "$OUT/scripts/node_integrity_guard.py" ]]; then
  python3 "$OUT/scripts/node_integrity_guard.py"
fi
if [[ -f "$OUT/scripts/stars_node_integrity.py" ]]; then
  python3 "$OUT/scripts/stars_node_integrity.py"
fi
echo "Done. Open: file://$OUT/graph_unified.html (or serve $OUT over HTTP)."
