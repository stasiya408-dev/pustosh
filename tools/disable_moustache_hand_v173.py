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
strip_marker="/* v173: all hand atlas frames and moustache sprite code removed */"
arm_renderer_original='var hf=val("hf",now);if(window._hpOv!=null)hf=1;else if(window._nsOn&&window._nsOn.ntop)hf=0;'
arm_renderer_static='var hf=0;/* v173: arm sprite is always still, including overrides */'
if arm_renderer_original in html:
    if html.count(arm_renderer_original)!=1:
        raise SystemExit("Unexpected number of hand renderer blocks")
    html=html.replace(arm_renderer_original,arm_renderer_static,1)
elif strip_marker not in html and arm_renderer_static not in html:
    raise SystemExit("Could not find hero arm renderer to freeze")

mustache_renderer_original='var mL=val("musL",now),mR=val("musR",now),mT=val("musT",now);if(window._musOv){mL=_musOv[0];mR=_musOv[1];mT=_musOv[2]}'
mustache_renderer_static='var mL=0,mR=0,mT=0;/* v173: no moustache/hand overlay even from overrides */'
if mustache_renderer_original in html:
    if html.count(mustache_renderer_original)!=1:
        raise SystemExit("Unexpected number of moustache renderer blocks")
    html=html.replace(mustache_renderer_original,mustache_renderer_static,1)
elif strip_marker not in html and mustache_renderer_static not in html:
    raise SystemExit("Could not find hero moustache renderer to freeze")


# The static arm lives in srcFig. Remove the now-unused entire image atlases,
# face overlay cutouts, and their animation compositing code. This reduces
# memory/decode work and makes the hand animation impossible to restart.
import re
resource_ids=("handAtlas0","handAtlas1","handAtlas2","handMask","musImg","skinImg")
removed_bytes=0
for image_id in resource_ids:
    rx=re.compile(r'<img\s+id="' + re.escape(image_id) + r'"[^>]*>')
    found=rx.findall(html)
    if len(found)>1:
        raise SystemExit(f"Unexpected duplicate hand asset: {image_id}")
    if not found and strip_marker not in html:
        raise SystemExit(f"Missing expected hand asset: {image_id}")
    if found:
        removed_bytes+=len(found[0])
        html=rx.sub("",html)

if strip_marker not in html:
    start_token=mustache_renderer_static
    end_token="/* верёвка: крепится к узлу, качается как маятник */"
    if html.count(start_token)!=1 or html.count(end_token)!=1:
        raise SystemExit("Hand rendering removal anchors have changed")
    a=html.index(start_token)
    b=html.index(end_token,a)
    old=html[a:b]
    for token in ('if((mL||mR||mT)', 'if(hf>.002', 'hcx.drawImage(', 'ctx.drawImage(hcv'):
        if token not in old:
            raise SystemExit(f"Unexpected missing hand renderer token: {token}")
    html=html[:a]+strip_marker+"\n"+html[b:]

    # The three hand sprite sheets and mask are no longer referenced.
    a_token='var HAT=el("headAtlas"),HATB=el("headAtlasB"),MU=el("musImg")'
    b_token='var FW=910,FH=1465,STRIP=3;'
    if html.count(a_token)!=1 or html.count(b_token)!=1:
        raise SystemExit("Animated hand frame list changed unexpectedly")
    a=html.index(a_token)
    b=html.index(b_token,a)
    kept=('var HAT=el("headAtlas"),HATB=el("headAtlasB"),'
          'src=el("srcFig"),cv=el("herocv"),cord=el("cord"),'
          'hat=el("L_hat"),nhat=el("L_nhat"),'
          'ctx=cv?cv.getContext("2d"):null;\n')
    html=html[:a]+kept+html[b:]

    # Remove old unused moustache offscreen compositors too.
    a_token='var pc=document.createElement("canvas");'
    b_token='var ev=[];/* события: {t0,dur,ch,f} */'
    if html.count(a_token)!=1 or html.count(b_token)!=1:
        raise SystemExit("Moustache compositor structure changed unexpectedly")
    a=html.index(a_token)
    b=html.index(b_token,a)
    html=html[:a]+html[b:]

for image_id in resource_ids:
    if re.search(r'<img[^>]*\bid="' + image_id + r'"',html):
        raise SystemExit(f"Animated hand frames still embedded: {image_id}")
assert strip_marker in html
assert 'id="srcFig"' in html
assert 'id="herocv"' in html
assert 'id="headAtlas"' in html and 'id="headAtlasB"' in html
assert 'if(hf>.002' not in html and 'if((mL||mR||mT)' not in html
assert 'var HAT=el("headAtlas"),HATB=el("headAtlasB"),src=el("srcFig")' in html
print(f"Removed {len(resource_ids)} hand/moustache image resources ({removed_bytes:,} HTML chars)")


source.write_text(html,encoding="utf-8")

updated=source.read_text(encoding="utf-8")
assert marker in updated
assert 'function hand(){/* no movement:' in updated
assert 'function mustache(){/* no movement:' in updated
assert 'if(rr<.3)glance();else clench(' in updated
assert 'if(rr<.42)hand()' not in updated
assert 'add("hp",7000' not in updated
assert 'add("musL",5000' not in updated
assert strip_marker in updated
assert arm_renderer_static not in updated
assert mustache_renderer_static not in updated
assert arm_renderer_original not in updated
assert mustache_renderer_original not in updated
print("All animated hand frames removed; Cossack keeps original static arm")
