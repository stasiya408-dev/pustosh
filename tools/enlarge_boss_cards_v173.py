#!/usr/bin/env python3
"""v173: larger, vertically swipeable illustrated boss cards, preserving art and combat."""
from pathlib import Path

p=Path("index.html")
html=p.read_text(encoding="utf-8")
marker="/* v173: swipeable enlarged boss-list cards */"

def prune_old_click_zones(s):
    """Remove fixed invisible hitboxes: new larger cards own all list taps."""
    needle="var LB=[255,380,507,637,768,898,1029,1153,1287];"
    if needle not in s:
        return s
    if s.count(needle)!=1:
        raise SystemExit("Ambiguous old boss-list click zones")
    start=s.index(needle)
    end=s.index("/* бой */",start)
    return s[:start]+"h+='</div>';\\n".replace("\\n","\n")+s[end:]


# v174 prototype: keep the existing nine-boss list; enable the mode + rage
# selection gate only for Ostap. The visual is CSS-based (not an image of UI),
# so keys, HP, and limits can update live without replacing the artwork.
OSTAP_CSS=r'''<style id="ostap-boss-selection-v174">
/* v174: full-screen mobile boss selection drawn in the game's parchment and bronze style */
#ostapChoice{position:absolute;inset:0;z-index:500;overflow-y:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;background:radial-gradient(ellipse at top,#13445b,#071723 63%,#20120a 100%);color:#40200e;font-family:Georgia,serif}
#ostapChoice .osWrap{width:min(100%,620px);min-height:100%;margin:0 auto;box-sizing:border-box;position:relative;padding:12px 13px 23px;background:linear-gradient(180deg,#111b2499 0%,#152d3299 34%,#261205e8 100%)}
#ostapChoice button{cursor:pointer;touch-action:manipulation;font-family:Georgia,serif}
#ostapChoice button:focus-visible{outline:3px solid #ffe8a7;outline-offset:3px}
#ostapChoice .osBack{border:1px solid #e0b97a;background:linear-gradient(#624128,#2a170f);color:#ffe3ad;border-radius:10px;font-size:13px;font-weight:800;padding:11px 14px;position:relative;z-index:2;text-shadow:0 1px 2px #000}
#ostapChoice .osHero{height:clamp(185px,34vh,335px);margin-top:-18px;border-radius:16px 16px 0 0;display:flex;flex-direction:column;justify-content:end;align-items:center;background-position:50% 29%;background-size:cover;background-repeat:no-repeat;box-shadow:inset 0 -65px 55px -15px #27160b}
#ostapChoice .osHeroWords{width:100%;text-align:center;padding:10px 9px 18px;box-sizing:border-box;background:linear-gradient(transparent,#291a10da);display:flex;flex-direction:column;gap:5px;color:#ffe2a7;text-shadow:0 2px 4px #000}
#ostapChoice .osHeroWords span{font-weight:900;font-size:clamp(19px,5.9vw,34px);letter-spacing:1px}
#ostapChoice .osHeroWords strong{font-weight:900;font-size:clamp(17px,4.6vw,26px)}
#ostapChoice .osHeroWords small{font-size:13px;color:#f3d59d}
#ostapChoice .osPaper{margin-top:-1px;padding:15px 11px 19px;border:5px ridge #a9763e;border-radius:5px 5px 16px 16px;background:linear-gradient(140deg,#f8e7bf,#e9ca96 57%,#e1b877);box-shadow:inset 0 0 0 2px #fff1ca,0 5px 26px #000a}
#ostapChoice .osColumns{display:grid;grid-template-columns:1fr 1.24fr;gap:12px}
#ostapChoice .osCaption{text-align:center;font-size:clamp(13px,3.2vw,18px);font-weight:900;margin-bottom:10px;border-bottom:1px solid #9d7849;padding-bottom:9px}
#ostapChoice .osModes,#ostapChoice .osRages{display:flex;flex-direction:column}
#ostapChoice .osMode{height:91px;background:linear-gradient(#f3ddb4,#cfaf78);color:#492513;border:3px solid #9d7043;border-radius:12px;margin-bottom:9px;box-shadow:0 3px 5px #673d205c;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:2px}
#ostapChoice .osMode>span{font-size:27px;line-height:29px}
#ostapChoice .osMode b{font-size:17px}
#ostapChoice .osMode small{font-size:10px;opacity:.8}
#ostapChoice .osMode.chosen{border-color:#f4b42d;background:linear-gradient(#ffe3a1,#edb956);box-shadow:0 0 0 2px #875225,inset 0 2px 3px #fff6}
#ostapChoice .osRage{min-height:55px;text-align:left;margin-bottom:9px;padding:8px 8px;border:3px solid #a97842;border-radius:9px;background:linear-gradient(#2d5167,#0b304b);color:#fff0cb;text-shadow:0 1px 2px #000;font-weight:900;font-size:clamp(11px,2.8vw,16px);display:flex;justify-content:space-between;align-items:center;gap:3px}
#ostapChoice .osRage small{font-size:10px;white-space:nowrap;color:#f4d38c}
#ostapChoice .osRage[data-os-rage="1"]{background:linear-gradient(#92511f,#62260d)}
#ostapChoice .osRage[data-os-rage="2"]{background:linear-gradient(#7d211b,#420f0e)}
#ostapChoice .osRage.chosen{border-color:#ffcd51;box-shadow:0 0 0 2px #50331c,0 0 12px #ffce6580}
#ostapChoice .osStatus,#ostapChoice .osCosts{display:flex;justify-content:space-between;gap:7px;flex-wrap:wrap;padding:9px 5px;margin-top:5px;border-top:1px solid #b99361;font-size:clamp(12px,3.3vw,16px);font-weight:800}
#ostapChoice .osCosts{border:2px solid #bd9764;border-radius:10px;background:#f0d2a4;margin:5px 0 15px;padding:12px 8px}
#ostapChoice .osAttack{display:block;width:100%;min-height:71px;border:5px ridge #e5a54b;border-radius:12px;background:linear-gradient(#d82b18,#9a0d09);box-shadow:inset 0 2px 2px #ff7c54,0 5px 0 #6d240f;color:#fff0ce;text-shadow:0 3px 3px #340800;font-size:clamp(26px,7vw,37px);font-weight:900;letter-spacing:1.5px}
#ostapChoice .osAttack:disabled{background:linear-gradient(#887e6f,#554638);color:#e4d2ae;box-shadow:none;cursor:not-allowed}
#osBattleTag{position:absolute;top:5px;left:50%;transform:translateX(-50%);z-index:70;padding:8px 16px;border-radius:12px;background:#2b160bde;color:#ffe6a6;border:2px solid #b58744;text-align:center;font:bold 16px Georgia,serif;pointer-events:none;white-space:nowrap}
#osDefeat{position:absolute;inset:0;z-index:600;display:flex;align-items:center;justify-content:center;background:#080c12cd;text-align:center;padding:20px}
#osDefeat>div{background:linear-gradient(#f4dcac,#cda66b);border:5px ridge #a16e32;border-radius:14px;padding:23px 15px}
#osDefeat h2{color:#872010;margin:0 0 10px}
#osDefeat button{border:3px solid #bd8139;background:#87200c;color:#ffe7ac;border-radius:11px;padding:14px;font-weight:900}
@media(max-width:350px){#ostapChoice .osPaper{padding-left:5px;padding-right:5px}#ostapChoice .osColumns{gap:6px}#ostapChoice .osRage{padding:5px;font-size:10px}#ostapChoice .osMode{height:81px}}
</style>'''
OSTAP_JS=r'''<script id="ostap-boss-flow-v174">
/* v174 Ostap boss-flow test: selector -> locked battle -> claimed reward */
(function(){
"use strict";
var IDX=1,BID="ostap",COST=[1,2,3],HEALTH=[1,1.6,2.4],REWARD=[1,1.25,1.5];
var RAGE=["ГРОЗНЫЙ","СВИРЕПЫЙ","БЕСПОЩАДНЫЙ"];
var choice={mode:"solo",rage:0},chooseEl=null;
function ready(){
 if(!document.getElementById("nbx")||!window._nb||!window.PG||!window.S||!window.BOSSES){setTimeout(ready,100);return}
 init();
}
function user(){var p=window.PG();p.bossFightKeys=p.bossFightKeys||{};return p}
function count(){return Math.max(0,Number(user().bossFightKeys[BID]||0))}
function persist(){try{localStorage.setItem("kozak3",JSON.stringify(S))}catch(e){}}
function give(n){var p=user();p.bossFightKeys[BID]=Math.max(0,Number(p.bossFightKeys[BID]||0)+n);persist()}
function lock(){return S.ostapBattle&&S.ostapBattle.bid===BID?S.ostapBattle:null}
function locked(){var b=lock();return !!(b&&(b.phase==="fight"||b.phase==="reward"))}
function alertText(message){
 var t=document.getElementById("nbtoast");
 if(!t)return;
 t.textContent=message;t.classList.add("on");
 setTimeout(function(){if(t.textContent===message)t.classList.remove("on")},3200)
}
function attempts(){return window.pgBossRuns?pgBossRuns(BID):0}
function maximum(){return (window.GAME_CONFIG&&GAME_CONFIG.BOSS_RUNS_PER_DAY)||6}
function keyCost(){return COST[choice.rage]}
function maxHp(mode,rage){var boss=BOSSES[IDX];var base=mode==="grp"?boss.hp:Math.round(boss.hp/(boss.fr+1));return Math.round(base*HEALTH[rage])}
function note(){
 if(!chooseEl)return;
 var cost=keyCost(),enough=count()>=cost,available=attempts()<maximum();
 chooseEl.querySelector("#osKeys").textContent="🔑 Ключи Остапа: "+count()+" · нужно "+cost;
 chooseEl.querySelector("#osRuns").textContent="⚔ Боёв сегодня: "+attempts()+"/"+maximum();
 chooseEl.querySelector("#osHp").textContent="❤️ Здоровье: "+maxHp(choice.mode,choice.rage).toLocaleString("ru-RU");
 chooseEl.querySelector("#osRewards").textContent="Награды: ×"+REWARD[choice.rage].toFixed(2);
 chooseEl.querySelectorAll("[data-os-mode]").forEach(function(el){var on=el.dataset.osMode===choice.mode;el.classList.toggle("chosen",on);el.setAttribute("aria-pressed",on?"true":"false")});
 chooseEl.querySelectorAll("[data-os-rage]").forEach(function(el){var on=+el.dataset.osRage===choice.rage;el.classList.toggle("chosen",on);el.setAttribute("aria-pressed",on?"true":"false")});
 var go=chooseEl.querySelector("[data-os-go]");
 go.disabled=!enough||!available;
 go.textContent=!available?"ЛИМИТ ИСЧЕРПАН":!enough?"НЕДОСТАТОЧНО КЛЮЧЕЙ":"⚔ НАПАСТЬ";
}
function hide(){if(chooseEl){chooseEl.remove();chooseEl=null}}
function openChoose(){
 if(locked()){alertText("Сначала заверши текущий бой и забери награду.");return}
 if(attempts()>=maximum()){alertText("Лимит Остапа: "+maximum()+" боёв в день.");return}
 if(count()<1){alertText("Нет ключа Остапа. Найди ключ в походе.");return}
 choice={mode:"solo",rage:0};
 hide();
 chooseEl=document.createElement("section");
 chooseEl.id="ostapChoice";chooseEl.setAttribute("aria-label","Выбор нападения на Остапа");
 chooseEl.innerHTML='<div class="osWrap">'
 +'<button class="osBack" type="button" data-os-back>← К СПИСКУ БОССОВ</button>'
 +'<div class="osHero"><div class="osHeroWords"><span>ВЫБОР НАПАДЕНИЯ</span><strong>ОСТАП ПЕРЕВІЗНИК</strong><small>Владыка призрачной реки</small></div></div>'
 +'<div class="osPaper"><div class="osColumns"><div class="osModes"><div class="osCaption">С КЕМ ИДЁШЬ?</div>'
 +'<button class="osMode chosen" type="button" data-os-mode="solo" aria-pressed="true"><span>⚔️</span><b>СОЛО</b><small>Один против босса</small></button>'
 +'<button class="osMode" type="button" data-os-mode="grp" aria-pressed="false"><span>🛡️</span><b>ОТРЯД</b><small>Казаки помогают в бою</small></button></div>'
 +'<div class="osRages"><div class="osCaption">ЯРОСТЬ БОССА</div>'
 +'<button type="button" class="osRage chosen" data-os-rage="0" aria-pressed="true">🛡️ ГРОЗНЫЙ <small>1 ключ</small></button>'
 +'<button type="button" class="osRage" data-os-rage="1" aria-pressed="false">⚒️ СВИРЕПЫЙ <small>2 ключа</small></button>'
 +'<button type="button" class="osRage" data-os-rage="2" aria-pressed="false">☠️ БЕСПОЩАДНЫЙ <small>3 ключа</small></button></div></div>'
 +'<div class="osStatus"><span id="osHp"></span><span id="osRewards"></span></div>'
 +'<div class="osCosts"><span id="osKeys"></span><span id="osRuns"></span></div>'
 +'<button type="button" class="osAttack" data-os-go>⚔ НАПАСТЬ</button>'
 +'</div></div>';
 var host=document.getElementById("nbx");host.appendChild(chooseEl);
 var bg=window.NBI&&window.NBI.ost;
 if(bg)chooseEl.querySelector(".osHero").style.backgroundImage='linear-gradient(180deg,rgba(4,14,24,.18),rgba(11,17,24,.60)),url("'+bg+'")';
 chooseEl.addEventListener("click",function(ev){
   ev.stopPropagation();
   var el=ev.target.closest("button");if(!el)return;
   if(el.dataset.osBack!==undefined){hide();return}
   if(el.dataset.osMode){choice.mode=el.dataset.osMode;note();return}
   if(el.dataset.osRage!==undefined){choice.rage=+el.dataset.osRage;note();return}
   if(el.dataset.osGo!==undefined)attack();
 });
 note();
}
function attack(){
 if(!chooseEl||locked())return;
 if(attempts()>=maximum()){note();alertText("Лимит Остапа исчерпан.");return}
 var price=keyCost();
 if(count()<price){note();alertText("Нужно "+price+" ключа. У тебя "+count()+".");return}
 var access=window.bossAccess?bossAccess(IDX):{ok:1};
 if(!access.ok&&!access.ready){alertText("Сначала открой доступ к Остапу.");return}
 var selected={bid:BID,mode:choice.mode,rage:choice.rage,phase:"fight",paid:price,started:Date.now(),endAt:0};
 if(window.VIC&&!window.VIC.done){alertText("Сначала забери предыдущую награду.");return}
 S.ostapBattle=selected;S.mode=choice.mode;
 window._nb.pick(IDX);
 if(S.cb!==IDX){S.ostapBattle=null;alertText("Пока нельзя войти к этому боссу.");return}
 var b=S.bd[choice.mode],hp=maxHp(choice.mode,choice.rage);
 if(!b){S.ostapBattle=null;alertText("Бой временно недоступен.");return}
 if(!window.pgBossMarkRun||!pgBossMarkRun(BID)){S.ostapBattle=null;alertText("Лимит на сегодня.");return}
 give(-price);
 b.max=hp;b.hp=hp;b.end=Date.now()+BOSS_TIME;
 b.pe=b.end;b.pd=0;
 if(choice.mode==="solo"){S.bd.grp.hp=0;S.bd.grp.end=b.end}
 if(choice.mode==="grp"){b.my=0;b.fd={};b.ft=Date.now()+10000}
 selected.endAt=b.end;persist();
 hide();
 window._nb.show("fight");window._nb.ui();
 var tag=document.getElementById("osBattleTag");
 if(!tag){tag=document.createElement("div");tag.id="osBattleTag";document.getElementById("nbx").appendChild(tag)}
 tag.textContent="🔒 "+(choice.mode==="grp"?"ОТРЯД":"СОЛО")+" · "+RAGE[choice.rage];
 tag.style.display="block";
}
function release(){
 S.ostapBattle=null;persist();
 var tag=document.getElementById("osBattleTag");if(tag)tag.style.display="none";
 hide();
 window._nb.show("list");
}
function claim(){
 var b=lock();
 if(!b||b.phase!=="reward"||!window.VIC||VIC.ph!==1||VIC.done)return false;
 VIC.done=1;VIC.ph=2;
 var win=document.getElementById("nbwn");if(win)win.classList.remove("on");
 release();return true;
}
function init(){
 var host=document.getElementById("nbx");
 if(!S.ostapTestKeysSeeded&&window.GAME_CONFIG&&GAME_CONFIG.ALPHA_MODE){
   S.ostapTestKeysSeeded=1;give(6);
 }
 var baseMax=window.bmax;
 if(typeof baseMax==="function"){
   window.bmax=function(m){
     var n=baseMax(m),b=lock();
     return b&&b.phase==="fight"&&S.cb===IDX?Math.round(n*HEALTH[b.rage]):n;
   };
 }
 var baseWin=window.bossWin;
 if(typeof baseWin==="function"){
   window.bossWin=function(g){
     var active=locked()&&S.cb===IDX,previousSilver=S.sv,previousPower=S.pw,b=lock();
     var r=baseWin.apply(this,arguments);
     if(active&&b){
       var factor=REWARD[b.rage],silver=Math.round(Math.max(0,S.sv-previousSilver)*(factor-1));
       var power=Math.round(Math.max(0,S.pw-previousPower)*(factor-1));
       S.sv+=silver;S.pw+=power;
       if(window.VIC){VIC.v+=silver;VIC.pw+=power}
       b.phase="reward";b.reward=window.VIC?{v:VIC.v,pw:VIC.pw,xp:VIC.xp,g:VIC.g}:null;
       persist();
     }
     return r;
   };
 }
 var saved=lock();
 if(saved&&saved.phase==="reward"&&!window.VIC&&saved.reward){window.VIC=Object.assign({ph:1,done:0,shown:0,t:Date.now()},saved.reward)}
 var oldHike=window.pgHikeEnd;
 if(typeof oldHike==="function"){
   window.pgHikeEnd=function(ok,r){
     var ret=oldHike.apply(this,arguments);
     if(ok&&Math.random()<.16){
       give(1);
       if(r)r.pg=(r.pg||"")+" 🔑 Знайдено ключ Остапа!";
     }
     return ret;
   };
 }
 host.addEventListener("click",function(ev){
   var target=ev.target.closest?ev.target.closest("[data-a]"):null;
   if(!target)return;
   if(target.dataset.a==="confirmboss"){
     var title=document.querySelector("#nbmp h2");
     if(title&&title.textContent.indexOf("Остап")>=0){
       ev.preventDefault();ev.stopImmediatePropagation();
       if(attempts()>=maximum()||count()<1){alertText(count()<1?"Сначала найди ключ Остапа в походе.":"Лимит босса на сегодня исчерпан.");return}
       document.getElementById("nbmd").classList.remove("on");
       openChoose();return;
     }
   }
   if(locked()&&target.dataset.a==="mode"){
     ev.preventDefault();ev.stopImmediatePropagation();
     alertText("Режим выбран до боя. Изменить его нельзя.");return;
   }
   if(locked()&&target.dataset.a==="wclose"){
     ev.preventDefault();ev.stopImmediatePropagation();
     if(!claim())alertText("Сначала одержи победу и забери награду.");
   }
 },true);
 var nav=document.getElementById("nav2");
 if(nav)nav.addEventListener("click",function(ev){
   if(!locked())return;
   ev.preventDefault();ev.stopImmediatePropagation();
   alertText("Бой начался: выход после победы и получения награды.");
 },true);
 ["nbClose","bossClose"].forEach(function(name){
   var old=window[name];
   if(typeof old==="function")window[name]=function(){
     if(locked()){alertText("Бой нельзя покинуть до завершения.");return}
     hide();return old.apply(this,arguments);
   };
 });
 var oldBossOpen=window.bossOpen;
 if(typeof oldBossOpen==="function")window.bossOpen=function(){
   var r=oldBossOpen.apply(this,arguments);
   if(locked()){S.cb=IDX;S.mode=lock().mode;window._nb.show("fight")}
   return r;
 };
 var oldShow=window._nb.show;
 window._nb.show=function(where){
   if(locked()&&where==="list"){alertText("Забери награду после победы.");return}
   return oldShow.apply(this,arguments);
 };
 var oldSet=window.setMode;
 if(typeof oldSet==="function")window.setMode=function(mode){
   if(locked()){alertText("Нельзя менять режим во время боя.");return}
   return oldSet.apply(this,arguments);
 };
 setInterval(function(){
   var b=lock();
   if(!b)return;
   if(b.phase==="fight"){
     if(S.mode!==b.mode)S.mode=b.mode;
     if(b.endAt&&Date.now()>=b.endAt){
       b.phase="failed";persist();
       var el=document.createElement("div");el.id="osDefeat";
       el.innerHTML='<div><h2>БОСС СБЕЖАЛ</h2><p>Время боя вышло. Попытка и ключи потрачены.</p><button type="button">ВЕРНУТЬСЯ К БОССАМ</button></div>';
       document.getElementById("nbx").appendChild(el);
       el.querySelector("button").onclick=function(){el.remove();release()};
     }
   }
 },1000);
 window.ostapTest={get:function(){return{keys:count(),runs:attempts(),lock:lock()}},open:openChoose,claim:claim};
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",ready,{once:true});else ready();
})();
</script>'''

def enable_ostap_one_boss(s):
    marker='id="ostap-boss-selection-v174"'
    if marker in s:
        begin='<style id="ostap-boss-selection-v174">'
        finish='</script>'
        if s.count(begin)!=1:
            raise SystemExit("Ostap selector style marker is ambiguous")
        a=s.index(begin)
        b=s.index(finish,a)+len(finish)
        desired=OSTAP_CSS+"\n"+OSTAP_JS
        return s[:a]+desired+s[b:] if s[a:b]!=desired else s
    end='</body></html>'
    if s.count(end)!=1:
        raise SystemExit("Unexpected HTML closing tag for Ostap selector")
    if 'window._nb={show:show,pick:pick,fit:fit,ui:ui}' not in s:
        raise SystemExit("Boss screen internals changed; cannot install selector safely")
    return s.replace(end,OSTAP_CSS+"\n"+OSTAP_JS+"\n"+end,1)


if marker in html:
    newer=enable_ostap_one_boss(prune_old_click_zones(html))
    if newer!=html:
        p.write_text(newer,encoding="utf-8")
        print("Pruned duplicate invisible boss-list hotspots")
    else:
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

html=enable_ostap_one_boss(prune_old_click_zones(html))
p.write_text(html,encoding="utf-8")
print("Installed large vertical-swipe boss cards (9 bosses), original art preserved")
