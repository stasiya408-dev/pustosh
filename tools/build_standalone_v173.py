#!/usr/bin/env python3
"""Produce a no-server, single-file v173 preview (including boss artwork).

This file is an export, NOT the optimized production build.
Keep optimized index.html + assets/boss/*.webp for deployment.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "index.html"
boss_dir = ROOT / "assets" / "boss"
target = ROOT / "game_v173_standalone.html"

html = source.read_text(encoding="utf-8")
boss_files = sorted(boss_dir.glob("*.webp"))
if len(boss_files) != 10:
    raise SystemExit(f"Expected 10 boss images, found {len(boss_files)}")

for file in boss_files:
    old = "assets/boss/" + file.name
    count = html.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one use of {old}, found {count}")
    inline = "data:image/webp;base64," + base64.b64encode(file.read_bytes()).decode("ascii")
    html = html.replace(old, inline, 1)

if "assets/boss/" in html:
    raise SystemExit("Unresolved boss asset path in standalone preview")
if 'name="ver" content="173"' not in html:
    raise SystemExit("Expected game v173")

target.write_text(html, encoding="utf-8")
print(f"Standalone preview: {target.name}, {target.stat().st_size:,} bytes")
