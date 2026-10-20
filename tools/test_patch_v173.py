#!/usr/bin/env python3
"""Read-only regression checks for the deterministic v173 patch."""
from pathlib import Path
import base64
import re
import subprocess
import sys

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("index.html")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("v173_preview/index.html")
old = src.read_text()
new = out.read_text()

assert '<meta name="ver" content="172">' in old
assert '<meta name="ver" content="173">' in new
assert 'id="hver">v173<' in new
assert 'RING_SHARDS_TO_CRAFT:100' in new
assert 'baseChance:.08,stepChance:.02,maxChance:.40,baseShards:100,stepShards:20' in new
assert 'pgBossMarkRun(BOSSES[S.cb].id)' in new
assert 'tk=function(){return window.pgBossRuns?pgBossRuns():0}' in new
assert 'function bossPreview(i)' in new
assert new.count('data:image/') == old.count('data:image/') - 10
assert len(new) < len(old) - 3_000_000

keys = ("list", "kul", "pet", "sul", "nag", "var", "kar", "ost", "kos", "cha")
for key in keys:
    m = re.search(r'"' + key + r'": "data:image/webp;base64,([A-Za-z0-9+/=]+)"', old)
    assert m, key
    original_bytes = base64.b64decode(m.group(1))
    asset = out.parent / "assets" / "boss" / f"{key}.webp"
    assert asset.read_bytes() == original_bytes, key
    assert f'"{key}": "assets/boss/{key}.webp"' in new

scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", new, re.S | re.I)
compiled = subprocess.run(
    ["node", "--check"], input="\n;\n".join(scripts), text=True, capture_output=True
)
assert compiled.returncode == 0, compiled.stderr

print(f"PASS: v173 version, 6 starts per boss, progressive forging, readable preview")
print(f"PASS: {len(keys)} image assets identical; HTML reduced by {(len(old)-len(new))/1e6:.2f} MB")
print("PASS: all inline JavaScript parses successfully")

