#!/usr/bin/env python3
"""Temporary diagnostic for the v173 Cossack-hand animation (no game mutations)."""
from pathlib import Path

html = Path("index.html").read_text(encoding="utf-8")
anchors = [
    "function mustache(){",
    "function hand(){",
    "function swat(",
    "function clench(",
    "function tick(",
    "window.heroDemo=",
    "/* ===== v50",
]
for needle in anchors:
    pos = html.find(needle)
    print(f"===== ANCHOR {needle!r} OFFSET {pos} =====")
    if pos < 0:
        continue
    before = 1800 if needle.startswith("function mustache") else 180
    after = 7000 if needle.startswith("function mustache") else 1900
    print(html[max(0,pos-before):pos+after].replace("\n", "\n"))
