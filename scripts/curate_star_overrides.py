#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.home() / "graphify-out"
MASTER = Path.home() / "spellbook_oracle" / "master_stars_all.json"
OVERRIDES = ROOT / "stars_group_overrides.json"
REPORT = ROOT / "stars_override_curation_report.md"

GROUPS = [
    ("mac", ["swift", "mlx", "macos", "darwin", "xcode", "ios", "appkit", "catalyst", "apple-silicon", "metal", "swiftui", "cocoa", "foundation", "objc", "watchos", "tvos"]),
    ("ai_code", ["claude", "mcp", "cursor", "copilot", "codex", "openclaw", "aider", "windsurf", "opencode", "gemini-cli", "cline", "continue.dev"]),
    ("agents", ["agent", "multi-agent", "autogen", "crewai", "langgraph", "orchestr", "swarm", "droid"]),
    ("local_ai", ["ollama", "llama.cpp", "gguf", "vllm", "onnx", "tensorrt", "quantization", "mlx", "inference", "ggml"]),
    ("graphs", ["graph", "rag", "vector", "embedding", "neo4j", "chromadb", "graphrag", "lancedb"]),
    ("browser", ["playwright", "puppeteer", "browser-use", "selenium", "cdp", "headless"]),
    ("data", ["dataset", "pandas", "spark", "pytorch", "jupyter", "notebook", "huggingface", "keras"]),
    ("sec", ["security", "osint", "pentest", "cve", "malware", "forensic"]),
]


def score_groups(repo: dict) -> dict[str, int]:
    fn = str(repo.get("full_name") or "").lower()
    desc = str(repo.get("description") or "").lower()
    topics = " ".join(str(t).lower() for t in (repo.get("topics") or []))
    lang = str(repo.get("language") or "").lower()
    blob = f"{fn} {desc} {topics} {lang}"
    out: dict[str, int] = {}
    for gid, kws in GROUPS:
        s = sum(1 for kw in kws if kw in blob)
        if gid == "agents" and ("agent" in fn or "agent" in topics):
            s += 2
        if gid == "mac" and ("mlx" in fn or "swift" in fn):
            s += 2
        if gid == "browser" and ("playwright" in fn or "browser" in fn):
            s += 2
        if s > 0:
            out[gid] = s
    return out


def infer_high_conf_override(repo: dict, scores: dict[str, int]) -> str | None:
    fn = str(repo.get("full_name") or "").lower()
    if not scores:
        return None
    ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    top_gid, top_score = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0
    # only take decisive wins
    if top_score < 3 or top_score - second < 2:
        return None
    # extra guardrails for strongest clusters
    if top_gid == "mac" and ("mlx" in fn or "swift" in fn or "apple" in fn):
        return "mac"
    if top_gid == "agents" and ("agent" in fn or "crew" in fn or "autogen" in fn):
        return "agents"
    if top_gid == "browser" and ("playwright" in fn or "puppeteer" in fn or "browser" in fn):
        return "browser"
    if top_gid in {"graphs", "data", "sec"}:
        return top_gid
    return None


def main() -> None:
    data = json.loads(MASTER.read_text(encoding="utf-8"))
    repos = data.get("repos") or []
    existing = {}
    if OVERRIDES.is_file():
        existing = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    existing = {str(k).lower(): str(v) for k, v in existing.items()}

    added: dict[str, str] = {}
    ambiguous = 0
    for repo in repos:
        fn = str(repo.get("full_name") or "").lower()
        if not fn or fn in existing:
            continue
        scores = score_groups(repo)
        if len(scores) > 1:
            ambiguous += 1
        gid = infer_high_conf_override(repo, scores)
        if gid:
            added[fn] = gid

    merged = dict(sorted({**existing, **added}.items()))
    OVERRIDES.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Stars Override Curation",
        "",
        f"- repos scanned: **{len(repos)}**",
        f"- ambiguous scored repos: **{ambiguous}**",
        f"- existing overrides: **{len(existing)}**",
        f"- new overrides added: **{len(added)}**",
        f"- total overrides now: **{len(merged)}**",
        "",
        "## Added (this run)",
    ]
    if not added:
        lines.append("- none")
    else:
        for k, v in sorted(added.items()):
            lines.append(f"- `{k}` -> `{v}`")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"updated {OVERRIDES} (+{len(added)})")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()

