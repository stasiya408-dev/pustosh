#!/usr/bin/env python3
"""v173: larger, vertically swipeable illustrated boss cards, preserving art and combat."""
from pathlib import Path

p=Path("index.html")
html=p.read_text(encoding="utf-8")
marker="/* v173: swipeable enlarged boss-list cards */"
if marker in html:
    print("Enlarged boss cards already installed")
    raise SystemExit(0)

def once(old,new):
    global html
    count=html.count(old)
    if count!=1:
        raise SystemExit(f"Expected one exact source match, got {count}: {old[:140]!r}")
    html=html.replace(old,new,1)

once('var OYS={list:98,fight:128},HC={list:1294,fight:1370},OY=98;',
     'var OYS={list:98,fight:128},HC={list:2940,fight:1370},OY=98;')

once('function modal(t,body){x.scrollTop=0;g("nbmp").innerHTML=',
     'function modal(t,body){if(scr=="list"){g("nbmd").style.top=(OY+x.scrollTop/(window._nbk||1))+"px"}'
     'else{x.scrollTop=0;g("nbmd").style.top="0px"}g("nbmp").innerHTML=')

once('scr=w;g("nbL").style.display=w=="list"?"block":"none";g("nbF").style.display=w=="fight"?"block":"none";',
     'scr=w;g("nbL").style.display=w=="list"?"block":"none";g("nbF").style.display=w=="fight"?"block":"none";'
     'g("nbbg").style.display=w=="list"?"none":"block";'
     'x.classList.toggle("nbLongBossList",w=="list");')

once('if(w=="list"){bg("list");listUI()}else{bg(BOSSES[S.cb].fk);lastFd=fdSum();lastEv=""}',
     'if(w=="list"){bg("list");g("nbL").style.setProperty("--nb-poster",'
     '\'url("\'+window.NBI.list+\'")\');listUI()}'
     'else{bg(BOSSES[S.cb].fk);lastFd=fdSum();lastEv=""}')

begin='function listUI(){'
end='function fdSum(){'
if html.count(begin)!=1 or html.count(end)!=1:
    raise SystemExit("Boss-list render function not uniquely identified")
a=html.index(begin)
b=html.index(end,a)
new_list=r'''function listUI(){
 var h='<div class="nbBossHeader"><div class="nbBossInfoBtn" data-a="linfo" title="Про босів"></div>'
  +'<div class="nbBossSwipeHint">↓ ГОРТАЙ ВНИЗ — ЩЕ БОСИ ↓</div></div>';
 /* Exact upper edges of portraits on original 941×1294 illustration. */
 var cropY=[126,253,382,510,639,769,898,1029,1158];
 BOSSES.forEach(function(b,i){
  var ac=window.bossAccess?bossAccess(i):{ok:1};
  var locked=!ac.ok,cta=locked?(ac.ready?"ВІДКРИТИ":"ЗАКРИТО"):"АТАКУВАТИ";
  var active=S.cb==i&&B().hp>0&&B().max&&B().hp<B().max;
  h+='<div class="nbBossRow'+(locked?' nbBossLocked':'')+(active?' nbBossActive':'')+'"'
   +' data-pk="'+i+'" style="top:'+(148+i*300)+'px" role="button" tabindex="0"'
   +' aria-label="'+b.n+'">';
  h+='<div class="nbBossArt" style="background-position:-98px -'+Math.round(cropY[i]*1.85)+'px"></div>';
  h+='<div class="nbBossRank">'+(i+1)+'</div>';
  h+='<div class="nbBossText"><div class="nbBossName">'+b.n+'</div>'
   +'<div class="nbBossDesc">'+b.w+'</div>'
   +'<div class="nbBossHealth">❤️ Здоров’я: '+nf(b.hp)+'</div></div>';
  h+='<div class="nbBossAction">'+cta+'</div>'
   +'<div class="nbBossItems">🔑 🧩 💍 💎</div></div>';
 });
 if(g("nbLo").innerHTML!==h)g("nbLo").innerHTML=h;
}
'''
html=html[:a]+new_list+html[b:]

# Keep the existing unlock route accessible when a boss is ready to unlock.
once("if(!a.ok)body+='<p>🔒 Бос поки недоступний: виконай вимоги глави й збери ключі.</p>';",
     "if(!a.ok){body+='<p>🔒 Бос поки недоступний: виконай вимоги глави й збери ключі.</p>';"
     "if(a.ready)body+='<div class=\"nbb\" data-a=\"confirmboss\">ВІДКРИТИ БОСА</div>';}")

style=r'''<style id="boss-swipe-v173">
''' + marker + r'''
#nbx.nbLongBossList{scroll-snap-type:none;touch-action:pan-y;-webkit-overflow-scrolling:touch}
#nbL{position:absolute;left:0;top:98px;width:941px;height:2940px}
#nbL>.nz{display:none!important}
#nbLo{position:absolute;inset:0}
.nbBossHeader{position:absolute;left:0;top:0;width:941px;height:131px;background-image:var(--nb-poster);background-size:941px 1294px;background-repeat:no-repeat;background-position:center top}
.nbBossInfoBtn{position:absolute;right:29px;top:8px;width:94px;height:105px;cursor:pointer}
.nbBossSwipeHint{position:absolute;left:245px;top:107px;width:500px;height:35px;text-align:center;font:bold 25px/33px Georgia,serif;letter-spacing:1px;color:#ffe6a5;text-shadow:0 2px 5px #230f08,0 1px 2px #000;background:linear-gradient(90deg,transparent,#321a0ebd 12%,#321a0ebd 88%,transparent);pointer-events:none}
.nbBossRow{position:absolute;left:14px;width:913px;height:284px;box-sizing:border-box;overflow:hidden;border-radius:16px;border:6px solid #6b3b16;background:linear-gradient(165deg,#f5e2b9 0%,#ead2a2 55%,#cfab70 100%);box-shadow:inset 0 0 0 3px #bf8d43,inset 0 7px 16px #fff6,0 8px 13px #090401aa;cursor:pointer;color:#3b2010}
.nbBossRow:active{filter:brightness(1.06)}
.nbBossArt{position:absolute;left:12px;top:13px;width:310px;height:248px;border:4px solid #6a3815;border-radius:10px;box-sizing:border-box;background-image:var(--nb-poster);background-size:1741px 2394px;background-repeat:no-repeat;box-shadow:0 3px 9px #30130866;pointer-events:none}
.nbBossRank{position:absolute;left:18px;top:16px;width:63px;height:73px;display:flex;align-items:center;justify-content:center;background:linear-gradient(#432916,#1d130d);clip-path:polygon(0 0,100% 0,100% 77%,50% 100%,0 77%);border:2px solid #c99a49;color:#ffe9b9;font:bold 45px Georgia,serif;text-shadow:0 2px 3px #000;pointer-events:none}
.nbBossText{position:absolute;left:345px;top:15px;width:319px;height:257px;pointer-events:none}
.nbBossName{font:900 42px/45px Georgia,serif;color:#4a1a0e;max-height:90px;overflow:hidden;text-transform:uppercase;text-shadow:0 1px 0 #fff4d4}
.nbBossDesc{margin-top:7px;font:bold 28px/32px Georgia,serif;color:#613e21;max-height:96px;overflow:hidden;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3}
.nbBossHealth{position:absolute;left:0;bottom:11px;font:bold 32px/38px Georgia,serif;white-space:nowrap;color:#472516}
.nbBossAction{position:absolute;right:17px;top:83px;width:221px;height:110px;border-radius:15px;border:6px solid #e8ad62;background:linear-gradient(#df3828,#bd1710 55%,#88110a);box-shadow:0 6px 0 #651d0f,inset 0 3px 0 #ff7865,0 8px 12px #34170666;display:flex;align-items:center;justify-content:center;color:#fff3db;font:900 34px/37px Georgia,serif;text-shadow:0 2px 3px #310800;text-align:center;pointer-events:none}
.nbBossItems{position:absolute;right:16px;bottom:22px;width:226px;text-align:center;white-space:nowrap;font:40px/50px Georgia,serif;text-shadow:0 2px 2px #704c21;pointer-events:none}
.nbBossLocked .nbBossAction{background:linear-gradient(#817365,#53463a);border-color:#aa9270}
.nbBossActive{border-color:#ffbb53;box-shadow:0 0 0 3px #ffb638,0 8px 16px #100600aa}
@media(prefers-reduced-motion:reduce){.nbBossRow,.nbBossAction{transition:none!important}}
</style>'''
once('</body></html>',style+'\n</body></html>')

p.write_text(html,encoding="utf-8")
print("Installed large vertical-swipe boss cards (9 bosses), original art preserved")
