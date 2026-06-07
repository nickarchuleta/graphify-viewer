#!/usr/bin/env python3
"""Regression contract snapshot for unified UI chrome (docks + arrows)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "graph_unified.html"
SNAP_DIR = ROOT / "docs" / "ui-chrome-snapshot"
BASELINE = SNAP_DIR / "baseline.json"
CURRENT = SNAP_DIR / "current.json"


def grab_block(css: str, selector: str) -> str:
    m = re.search(rf"{re.escape(selector)}\s*\{{(.*?)\}}", css, flags=re.S)
    return m.group(1) if m else ""


def prop(block: str, key: str) -> str:
    m = re.search(rf"{re.escape(key)}\s*:\s*([^;]+);", block)
    return (m.group(1).strip() if m else "")


def extract_snapshot(html: str) -> dict:
    css_m = re.search(r"<style>(.*?)</style>", html, flags=re.S)
    css = css_m.group(1) if css_m else ""
    root = grab_block(css, ":root")
    dock = grab_block(css, ".dock-toggle")
    left = grab_block(css, "#dock-toggle")
    right = grab_block(css, "#detail-toggle")
    view_exp = grab_block(css, ".view-dock.expanded .view-dock-inner")
    detail_exp = grab_block(css, ".detail-dock.expanded .detail-dock-inner")
    detail = grab_block(css, ".detail-dock")

    return {
        "side_open": prop(root, "--side-open"),
        "detail_open": prop(root, "--detail-open"),
        "dock_toggle": {
            "width": prop(dock, "width"),
            "height": prop(dock, "height"),
            "border": prop(dock, "border"),
            "font_size": prop(dock, "font-size"),
        },
        "left_toggle": {
            "border_left": prop(left, "border-left"),
            "border_right": prop(left, "border-right"),
            "border_radius": prop(left, "border-radius"),
            "right": prop(left, "right"),
        },
        "right_toggle": {
            "border_left": prop(right, "border-left"),
            "border_right": prop(right, "border-right"),
            "border_radius": prop(right, "border-radius"),
            "right": prop(right, "right"),
        },
        "panels": {
            "left_width": prop(view_exp, "width"),
            "right_width": prop(detail_exp, "width"),
            "right_border_base": prop(detail, "border-left"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    html = HTML.read_text(encoding="utf-8", errors="ignore")
    snap = extract_snapshot(html)
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    CURRENT.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {CURRENT}")

    if args.update_baseline or not BASELINE.exists():
        BASELINE.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {BASELINE}")
        return 0

    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    if base != snap:
        print("UI chrome snapshot mismatch")
        print("Compare:")
        print(f"- baseline: {BASELINE}")
        print(f"- current:  {CURRENT}")
        return 1

    print("UI chrome snapshot passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
