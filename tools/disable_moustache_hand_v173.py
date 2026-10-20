#!/usr/bin/env python3
"""Disable only the hero's automatic hand-to-moustache and moustache motions.

The rest of the character animation engine (head, breathing, cat/fly reactions,
leg stomp, clothing and layered rendering) stays intact. Idempotent on v173.
"""
from pathlib import Path

source=Path("index.html")
html=source.read_text(encoding="utf-8")
marker="/* v173: idle moustache-hand animation removed at user request */"

if marker not in html:
    begin="function hand(){"
    finish="function glance(){"
    if html.count(begin)!=1 or html.count(finish)!=1:
        raise SystemExit("Unexpected hero animation source: refusing unsafe change")
    start=html.index(begin)
    end=html.index(finish,start)
    old=html[start:end]
    for token in ('add("hp",7000', 'add("hf",7000', 'function mustache(){', 'add("musL",5000', 'add("musR",5000'):
        if token not in old:
            raise SystemExit(f"Missing required hero animation token: {token}")
    replacement = (
        marker+"\n"
        "function hand(){/* no movement: hand remains in its natural resting pose */}\n"
        "function mustache(){/* no movement: no moustache twirl */}\n"
    )
    html=html[:start]+replacement+html[end:]
    old_idle='if(rr<.42)hand();else if(rr<.52)mustache();else clench(Math.random()<.5?"L":"R")'
    if html.count(old_idle)!=1:
        raise SystemExit("Unexpected idle chooser: refusing unsafe change")
    # Preserve non-hand idle movement so the character does not appear lifeless.
    html=html.replace(old_idle,'if(rr<.3)glance();else clench(Math.random()<.5?"L":"R")',1)
    source.write_text(html,encoding="utf-8")
    print("Disabled Cossack hand-to-moustache and moustache twirl motions")
else:
    print("Idle moustache-hand animation already disabled")

# A second guard in the CANVAS RENDERER is required. A legacy hero overlay or
# developer override can request the animated hand even when idle callbacks are off.
# Keep the original painted resting hand in the base illustration; never draw
# animated replacement frames. Head movement, breathing, cat and background stay.
arm_renderer_original='var hf=val("hf",now);if(window._hpOv!=null)hf=1;else if(window._nsOn&&window._nsOn.ntop)hf=0;'
arm_renderer_static='var hf=0;/* v173: arm sprite is always still, including overrides */'
if arm_renderer_original in html:
    if html.count(arm_renderer_original)!=1:
        raise SystemExit("Unexpected number of hand renderer blocks")
    html=html.replace(arm_renderer_original,arm_renderer_static,1)
elif arm_renderer_static not in html:
    raise SystemExit("Could not find hero arm renderer to freeze")

mustache_renderer_original='var mL=val("musL",now),mR=val("musR",now),mT=val("musT",now);if(window._musOv){mL=_musOv[0];mR=_musOv[1];mT=_musOv[2]}'
mustache_renderer_static='var mL=0,mR=0,mT=0;/* v173: no moustache/hand overlay even from overrides */'
if mustache_renderer_original in html:
    if html.count(mustache_renderer_original)!=1:
        raise SystemExit("Unexpected number of moustache renderer blocks")
    html=html.replace(mustache_renderer_original,mustache_renderer_static,1)
elif mustache_renderer_static not in html:
    raise SystemExit("Could not find hero moustache renderer to freeze")

source.write_text(html,encoding="utf-8")

updated=source.read_text(encoding="utf-8")
assert marker in updated
assert 'function hand(){/* no movement:' in updated
assert 'function mustache(){/* no movement:' in updated
assert 'if(rr<.3)glance();else clench(' in updated
assert 'if(rr<.42)hand()' not in updated
assert 'add("hp",7000' not in updated
assert 'add("musL",5000' not in updated
assert arm_renderer_static in updated
assert mustache_renderer_static in updated
assert arm_renderer_original not in updated
assert mustache_renderer_original not in updated
print("Canvas-rendered Cossack arm stays in its original, still position")
