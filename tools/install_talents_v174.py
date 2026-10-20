#!/usr/bin/env python3
"""Additive v174 skill tree. Run against v173 index.html in its own branch."""
from pathlib import Path
p=Path("index.html")
s=p.read_text(encoding="utf-8")
assert '<meta name="ver" content="173">' in s, "Expected v173; refuse to patch another version"
assert 'id="talents-v174"' not in s
def one(before,after):
 global s
 n=s.count(before)
 assert n==1,(n,before[:90])
 s=s.replace(before,after)
one('<meta name="ver" content="173">','<meta name="ver" content="174">')
one('var VER=173;','var VER=174;')
if 'id="hver">v173<' in s:one('id="hver">v173<','id="hver">v174<')
old='''  var jb=window.bossBonus?bossBonus():0;if(jb>0){pd=Math.round(pd*(1+jb));hn+=" 💍+"+Math.round(jb*100)+"%"}
  b.hp=Math.max(0,b.hp-pd);if(S.mode=="grp")b.my=(b.my||0)+pd;b.pd=(b.pd||0)+pd;try{if(!(window.bossDevOnly&&bossDevOnly(S.cb)))pgBossShot(pd)}catch(e){}
  fx(pd,hn);lastEv="🔥 твій постріл: −"+nf(pd)+hn;'''
new='''  var jb=window.bossBonus?bossBonus():0;if(jb>0){pd=Math.round(pd*(1+jb));hn+=" 💍+"+Math.round(jb*100)+"%"}
  if(window.TALENTS){var boost=TALENTS.shot(pd,b.hp,b.max,S.hs);pd=boost.damage;if(boost.critical)hn+=" 🎯 КРИТ!"}
  pd=Math.min(Math.max(0,b.hp),pd); /* no excess-HP damage credit */
  b.hp=Math.max(0,b.hp-pd);if(S.mode=="grp")b.my=(b.my||0)+pd;b.pd=(b.pd||0)+pd;try{if(!(window.bossDevOnly&&bossDevOnly(S.cb)))pgBossShot(pd)}catch(e){}
  fx(pd,hn);lastEv="🔥 твій постріл: −"+nf(pd)+hn;'''
one(old,new)
one('window.pgBossShot=function(dmg){EV({type:"boss_shot",dmg:dmg})};','window.pgBossShot=function(dmg){if(dmg>0){EV({type:"boss_shot",dmg:dmg});sv()}};')
css=Path('tools/talents_v174.css').read_text(encoding='utf-8')
js=Path('tools/talents_v174.js').read_text(encoding='utf-8')
one('</body></html>','<style id="talents-css-v174">'+css+'</style><script id="talents-v174">'+js+'</script></body></html>')
p.write_text(s,encoding='utf-8')
print("v174 talent tree installed",p.stat().st_size)
