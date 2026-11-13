(function(){
/* v369: «Рейд місяця» (замість «Колоди»). Один спільний бос на весь місяць із величезною міцністю. Руйнують його козаки-боти (самі, до 70%) і ти.
   «Зброя місяця» б'є в рейді ×2 (з «Набором рейду» за талери — ×3). Заряди цієї зброї фармляться весь місяць: безкоштовно повільніше (пайок, боси, походи, кості),
   за талери швидше (пачки, набір). Нагороди: 4 рубежі спільного прогресу (25/50/75/100%) + 4 особисті щаблі за внесок (є стеля). Без сервера боти умовні.
   ВСІ числа — мої (UNAPPROVED). Реальні гроші/Stars підключимо потім на те саме місце, що й талери (магазин зарядів). */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc,fs=P.fs;
var BOTSHARE=.7,HPK=10,REFR=500,NEEDK=.5,AVG=1.1,KITMUL=3,BASEMUL=2;
var WEAP=["cannon","rifle","volley","samopal","dagger"];
var WIC={cannon:"💣",rifle:"🔫",volley:"🏹",samopal:"🔫",dagger:"🗡"};
var BOSS=[["Морозяка-велетень","🥶"],["Вовкулак Сірий","🐺"],["Відьма з Лисої Гори","🧙"],["Змій Горинич","🐉"],["Мавка-цариця","🧝"],["Водяник Бездонний","🌊"],["Перун-відступник","⚡"],["Вій Залізні Повіки","👁"],["Бик із Дикого поля","🐂"],["Упир Чорний","🦇"],["Лісовик-хазяїн","🌲"],["Крижаний цар","❄️"]];
var MS=[[.25,{sv:5000,junk:10}],[.5,{sv:10000,tl:3,junk:20}],[.75,{sv:18000,tl:6,junk:30}],[1,{sv:35000,tl:15,junk:50,en:30}]];
var TIERS=[[.5,"Учасник",{sv:4000,junk:8,en:10},0],[1,"Лицар",{sv:10000,tl:3,junk:15},0],[2,"Курінний",{sv:22000,tl:8,junk:30},30],[3,"Легенда",{sv:45000,tl:20,junk:60},100]];
var SRC={bk:{n:"Перемога над босом",per:4,cap:6},hn:{n:"Похід",per:3,cap:4},dw:{n:"Перемога в кістках",per:1,cap:8}};
var RATION=5;
var SHOP=[[10,5],[50,20],[200,70]];
var KIT={tl:45,am:100};
var JOK=["Постріл влучив. Бос вдав, що не помітив.","Бух! Хтось із глядачів перехрестився.","Заряд полетів, як тесть на весіллі: гучно й невідворотно.","Чути було аж у корчмі — шинкарка наливає «за здоров'я».","Влучно! Бос пробурмотів щось про профспілку чудовиськ.","Козацький привіт доставлено: «Здрастуйте, ми до вас».","Гопак із вогнем — улюблений танець боса. Ну, був."];
function WL(){try{return GAME_CONFIG.BOSSCFG.WEAPONS.LIST}catch(e){return []}}
function wBy(id){var L=WL();for(var i=0;i<L.length;i++)if(L[i].id==id)return L[i];return {id:id,uk:id,base:100}}
function dim(m){var p=m.split("-");return new Date(Date.UTC(+p[0],+p[1],0)).getUTCDate()}
function mkey(){return P.day().slice(0,7)}
function fuse(){return (typeof FUSE_DMG=="number"&&FUSE_DMG>0)?FUSE_DMG:180}
function wid(m){var p=m.split("-"),i=((+p[0])*12+(+p[1]))%WEAP.length;return WEAP[i]}
function boss(m){return BOSS[(+m.split("-")[1]-1)%BOSS.length]}
function unitFor(w,mul){return fuse()*(w.base/180)*mul}
function msLeft(){var m=mkey(),n=dim(m),d=+P.day().slice(8);return ((n-d+1)*86400-P.secOfDay())*1000}
function fracTime(m){var n=dim(m),d=+P.day().slice(8);return Math.max(0,Math.min(1,((d-1)*86400+P.secOfDay())/(n*86400)))}
function mulNow(s){return s.kit?KITMUL:BASEMUL}
function cur(){return {bk:S.bossKills||0,hn:S.hn||0,dw:(S.ds&&S.ds.w)||0}}
function botsNow(s,fin){return Math.round(s.hp*BOTSHARE*(fin?1:fracTime(s.m)))}
function total(s){return Math.min(s.hp,s.dm+botsNow(s))}
function frac(s){return total(s)/s.hp}
function need(s){return s.ref*NEEDK}
function mkRw(a){var o={};for(var k in a)o[k]=a[k];return o}
/* ---- месяц ---- */
function Mo(){var d=T(),m=mkey(),r=d.rd;
 if(!r||r.m!==m){
  var note="";
  if(r&&r.hp){var rw={sv:0,tl:0,junk:0,en:0},wa=0,cl=0,ok=r.dm>=need(r),fr=Math.min(1,(r.dm+botsNow(r,1))/r.hp);
   if(ok){MS.forEach(function(x,i){if(fr>=x[0]&&!r.c[i]){r.c[i]=1;cl++;["sv","tl","junk","en"].forEach(function(k){rw[k]+=x[1][k]||0})}});
    TIERS.forEach(function(t,i){if(r.dm>=t[0]*r.ref&&!r.pc[i]){r.pc[i]=1;cl++;["sv","tl","junk","en"].forEach(function(k){rw[k]+=t[2][k]||0});wa+=t[3]}})}
   var left=r.am||0;if(left>0)rw.sv+=left*20;
   if(cl||left){var wo={};if(wa)wo[r.w]=wa;P.addCarry(rw,wa?wo:null);note="Минулого місяця «"+boss(r.m)[0]+"»: "+(cl?"чекають у Літописі (Справи): "+cl+" нагород. ":"")+(left?"Залишок "+left+" зарядів обміняно на срібло. ":"")+P.rewTxt(rw)+(wa?" · +"+wa+" "+wBy(r.w).uk:"")}}
  var w=wid(m),W=wBy(w),u0=Math.round(unitFor(W,BASEMUL)),ref=u0*REFR;
  r=d.rd={m:m,w:w,hp:ref*HPK,ref:ref,dm:0,sh:0,am:0,kit:0,c:[0,0,0,0],pc:[0,0,0,0],snap:cur(),ea:{d:"",bk:0,hn:0,dw:0},ra:"",sd:{d:"",n:0},log:[],note:note};
  P.save()}
 return r}
function sdToday(r){if(r.sd.d!==P.day()){r.sd={d:P.day(),n:0}}return r.sd.n}
/* ---- заряды ---- */
function earn(){try{var r=Mo(),c=cur(),td=P.day(),tot=0,parts=[];
 if(r.ea.d!==td){r.ea={d:td,bk:0,hn:0,dw:0}}
 for(var k in SRC){var dl=c[k]-(r.snap[k]||0);if(dl>0){var room=SRC[k].cap-(r.ea[k]||0),n=Math.max(0,Math.min(dl,room));if(n>0){tot+=n*SRC[k].per;r.ea[k]=(r.ea[k]||0)+n}}r.snap[k]=c[k]}
 if(tot>0){r.am+=tot;P.save();P.toast("Рейд місяця: +"+tot+" "+(wBy(r.w).uk)+" (заряди)");if(ov&&ov.classList.contains("on"))render()}}catch(e){}}
function ration(){var r=Mo();if(r.ra===P.day()){P.say("Пайок на сьогодні вже забрано. Завтра — знову.");return}
 r.ra=P.day();r.am+=RATION;P.save();P.toast("Пайок рейду: +"+RATION+" зарядів");render()}
function buy(i){var r=Mo(),p=SHOP[i];if(!p)return;if((S.tl||0)<p[1]){P.say("Бракує талерів: треба "+p[1]+" 💰.");return}
 S.tl-=p[1];r.am+=p[0];try{draw()}catch(e){}P.save();P.toast("Куплено "+p[0]+" зарядів за "+p[1]+" 💰");render()}
function buyKit(){var r=Mo();if(r.kit){P.say("Набір рейду в цьому місяці вже куплено.");return}
 if((S.tl||0)<KIT.tl){P.say("Бракує талерів: треба "+KIT.tl+" 💰.");return}
 S.tl-=KIT.tl;r.kit=1;r.am+=KIT.am;try{draw()}catch(e){}P.save();P.toast("Набір рейду: шкода ×"+KITMUL+" і +"+KIT.am+" зарядів");render()}
/* ---- стрельба ---- */
function shoot(n){var r=Mo(),W=wBy(r.w),did=0,crit=false,dm0=r.dm;
 if(frac(r)>=1){P.say("Бос місяця зламаний. Дочекайся наступного місяця.");return}
 if((r.am||0)<1){P.say("Зарядів немає. Заробляй (пайок, боси, походи, кості) або купи за талери.");return}
 sdToday(r);
 while(did<n&&r.am>=1&&frac(r)<1){r.am--;var c=Math.random()<.1,d=Math.round(unitFor(W,mulNow(r))*(.9+Math.random()*.2)*(c?2:1));r.dm+=d;r.sh++;r.sd.n++;if(c)crit=true;did++;P.cnt("rds")}
 var add=r.dm-dm0;
 r.log.push((did>1?"⚔ Залп із "+did+" зарядів: −":(crit?"💥 Крит! −":"⚔ −"))+fs(add)+" · "+JOK[Math.floor(Math.random()*JOK.length)]);if(r.log.length>5)r.log=r.log.slice(-5);
 try{draw()}catch(e){}P.save();try{window.SFX&&SFX.play(crit||did>1?"boom":"slash")}catch(e){}
 var c0=ov&&ov.querySelector(".dzfort");if(c0){c0.classList.remove("dzshk");void c0.offsetWidth;c0.classList.add("dzshk")}
 if(frac(r)>=1)P.toast("Бос місяця «"+boss(r.m)[0]+"» зламаний! Забери нагороди.");
 render()}
/* ---- нагороды ---- */
function claimMs(i){var r=Mo();if(r.dm<need(r)){P.say("Щоб брати нагороди, наб'й особисто ≥"+fp(pctOf(r,need(r)))+"% міцності боса.");return}
 if(r.c[i]||frac(r)<MS[i][0])return;r.c[i]=1;P.give(MS[i][1]);P.toast("Рейд: "+P.rewTxt(MS[i][1]));render()}
function claimTier(i){var r=Mo(),t=TIERS[i];if(r.pc[i]||r.dm<t[0]*r.ref)return;r.pc[i]=1;P.give(t[2]);
 if(t[3]){S.wa=S.wa||{};S.wa[r.w]=(S.wa[r.w]||0)+t[3]}
 P.toast("Рейд · «"+t[1]+"»: "+P.rewTxt(t[2])+(t[3]?" · +"+t[3]+" "+wBy(r.w).uk:""));render()}
function claimable(){var r=Mo(),n=0;if(r.dm<need(r))return 0;var f=frac(r);MS.forEach(function(m,i){if(f>=m[0]&&!r.c[i])n++});TIERS.forEach(function(t,i){if(r.dm>=t[0]*r.ref&&!r.pc[i])n++});return n}
function rationReady(){var r=Mo();return r.ra!==P.day()}
function ready(){return claimable()+(rationReady()?1:0)}
P.reg.raid=ready;
function hint(){var r=Mo();
 if(claimable()>0)return ["🐉","Забери нагороду рейду","Бос місяця дав поживу"];
 if(rationReady())return ["🐉","Забери пайок рейду","+"+RATION+" зарядів — безкоштовно, раз на день"];
 return null}
/* ---- підрахунки для підказок ---- */
function shotsFor(r,part){var u=Math.max(1,unitFor(wBy(r.w),mulNow(r))*AVG);return Math.max(0,Math.ceil((part-r.dm)/u))}
function pctOf(r,x){return (x/r.hp*100)}
function fp(x){var v=Math.round(x*10)/10;return String(v).replace(".",",")}
function nextStep(r,f,mine){
 if(f>=1)return "Боса зламано! Забери нагороди, які ще не взяв, і чекай наступного місяця ("+P.fmtLeft(msLeft())+").";
 if(claimable()>0)return "Є нагорода! Натисни «Забрати» нижче.";
 if(rationReady())return "Забери безкоштовний пайок: +"+RATION+" зарядів (раз на день).";
 if(r.am<1)return "Зарядів немає. Заряди дають: пайок, перемоги над босами, походи, кості. Швидше — за талери (пачки або Набір рейду).";
 if(r.dm<need(r)){var k=shotsFor(r,need(r));return "Крок 1: наб'й особисто хоч "+fp(pctOf(r,need(r)))+"% — ще ≈"+k+" "+(k==1?"постріл":"пострілів")+" (маєш "+r.am+" зарядів). Без цього нагороди не видають."}
 for(var i=0;i<TIERS.length;i++){if(r.dm<TIERS[i][0]*r.ref){var k2=shotsFor(r,TIERS[i][0]*r.ref);return "Наступний особистий щабель — «"+TIERS[i][1]+"»: ще ≈"+k2+" пострілів."+(r.am<k2?" Зарядів не вистачає — фарми далі чи купи.":"")}}
 return "Особистий максимум досягнуто («Легенда»). Далі — лише допомога спільному прогресу."}
/* ---- путівник ---- */
var gp=-1,ov;
function msTable(){var h='<div class="dkh">';MS.forEach(function(m){h+='<div><b>'+Math.round(m[0]*100)+'% боса</b><small>'+P.rewTxt(m[1])+'</small></div>'});return h+'</div>'}
function tierTable(r){var h='<div class="dkh">';TIERS.forEach(function(t){h+='<div><b>«'+t[1]+'» · '+fp(pctOf(r,t[0]*r.ref))+'% боса</b><small>≈'+shotsFor({dm:0,w:r.w,kit:r.kit},t[0]*r.ref)+' пострілів · '+P.rewTxt(t[2])+(t[3]?' · +'+t[3]+' зарядів':'')+'</small></div>'});return h+'</div>'}
var GUIDE=[
 {t:"Що це",b:function(){var r=Mo(),b=boss(r.m);return ''+
  '<div class="dzhero"><div class="em">🐉</div><div style="flex:1"><b>«'+b[0]+'» '+b[1]+'</b><small>Один бос на <b>весь місяць</b>. Зламай його до кінця місяця.</small></div></div>'+
  '<p>Б’ють двоє: <b>🤖 боти</b> (до '+Math.round(BOTSHARE*100)+'%) і <b>ти</b>.</p>'+
  '<p>Рубежі <b>25 · 50 · 75 · 100%</b> — нагороди.</p>'}},
 {t:"Зброя і заряди",b:function(){var r=Mo(),W=wBy(r.w);return ''+
  '<p>Б’ємо лише <b>'+esc(W.uk)+'</b> '+WIC[r.w]+' — <b>×'+BASEMUL+'</b> шкоди (з Набором ×'+KITMUL+').</p>'+
  '<div class="dkh"><div><b>🆓 Заряди безкоштовно</b><small>Пайок +'+RATION+'/день · Бос +'+SRC.bk.per+' · Похід +'+SRC.hn.per+' · Кості +'+SRC.dw.per+'</small></div>'+
  '<div><b>💰 За талери</b><small>10 за '+SHOP[0][1]+' · 50 за '+SHOP[1][1]+' · 200 за '+SHOP[2][1]+' · Набір '+KIT.tl+' 💰: ×'+KITMUL+', +'+KIT.am+'</small></div></div>'+
  '<p>Залишок у кінці місяця → 🥈.</p>'}},
 {t:"Нагороди",b:function(){var r=Mo();return msTable()+
  '<p style="margin-top:9px">Щоб <b>брати</b>: свій внесок <b>≥'+fp(pctOf(r,need(r)))+'%</b> (≈'+shotsFor({dm:0,w:r.w,kit:r.kit},need(r))+' пострілів).</p>'+
  tierTable(r)+
  '<p>Не встиг — <b>видасться саме</b> в кінці місяця.</p>'}}];
function guideHtml(){var g=GUIDE[gp],n=GUIDE.length;
 var s='<div class="dzc"><div class="dzt"><b>📖 Путівник · '+(gp+1)+'/'+n+'</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 s+='<div class="dkg"><h3>'+g.t+'</h3>'+g.b()+'</div><div class="dkdots">';for(var i=0;i<n;i++)s+='<i class="'+(i==gp?'on':'')+'"></i>';s+='</div>';
 s+='<div style="display:flex;gap:8px;margin-top:10px">';
 s+=(gp>0?'<button class="dzb" style="flex:1;padding:11px" data-z="gp" data-k="'+(gp-1)+'">◀ Назад</button>':'<button class="dzb" style="flex:1;padding:11px" data-z="gp" data-k="-1">Пропустити</button>');
 s+=(gp<n-1?'<button class="dzb g" style="flex:1;padding:11px" data-z="gp" data-k="'+(gp+1)+'">Далі ▶</button>':'<button class="dzb g" style="flex:1;padding:11px" data-z="gp" data-k="-1">Зрозуміло</button>');
 return s+'</div></div>'}
/* ---- екран ---- */
function ic(id){try{if(window.ITEM_ICONS&&ITEM_ICONS["w_"+id]&&typeof ICO=="function")return '<span style="display:inline-block;width:22px;height:22px;vertical-align:middle">'+ICO("w_"+id)+'</span>'}catch(e){}return WIC[id]||"🔫"}
function render(){if(!ov)return;
 if(gp>=0){ov.innerHTML=guideHtml();var n0=ov.querySelector(".dzc");if(n0)n0.scrollTop=0;return}
 var r=Mo(),f=frac(r),mine=r.dm/r.hp,bf=Math.min(1,botsNow(r)/r.hp),b=boss(r.m),W=wBy(r.w),h="",mul=mulNow(r);
 var myw=Math.max(0,Math.min(f-bf,1-bf)),u=unitFor(W,mul);
 h+='<div class="dzc"><div class="dzt"><b>🐉 Рейд місяця</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 if(r.note)h+='<div class="dzrow cu"><div class="dzn">🎁</div><div class="dzx"><small>'+esc(r.note)+'</small></div></div>';
 h+='<div class="dzk">«Один у полі не воїн, а цілий місяць у полі — вже кампанія». Цього місяця — «'+b[0]+'».</div>';
 h+='<div class="dzhero"><div class="em dzfort">'+(f>=1?'💀':b[1])+'</div><div style="flex:1"><b>'+b[0]+'</b><small>'+(f>=1?'Зламаний! Слава козакам.':'Міцність: '+fs(Math.max(0,r.hp-total(r)))+' з '+fs(r.hp))+'</small>'+
  '<div class="dzbar sg2"><i class="b" style="width:'+(bf*100).toFixed(1)+'%"></i><i class="m" style="width:'+(myw*100).toFixed(1)+'%"></i><u style="left:25%"></u><u style="left:50%"></u><u style="left:75%"></u></div>'+
  '<small style="margin-top:3px">Зламано '+Math.round(f*100)+'% · до кінця місяця '+P.fmtLeft(msLeft())+'</small></div></div>';
 h+='<div class="dzchips"><span class="sgb">🤖 Боти: '+Math.round(bf*100)+'% <em>(самі, до '+Math.round(BOTSHARE*100)+'%)</em></span><span class="sgm">🎯 Ти: '+fp(mine*100)+'% <em>('+(r.dm>=need(r)?'✓ нагороди відкриті':'потрібно ≥'+fp(pctOf(r,need(r)))+'%')+')</em></span><span>Пострілів: '+r.sh+'</span></div>';
 h+='<div class="dzk" style="margin-top:8px;font-style:normal">👉 '+esc(nextStep(r,f,mine))+'</div>';
 h+='<div class="dzrow"><div class="dzn" style="flex-basis:34px;height:34px;line-height:32px;font-size:18px">'+ic(r.w)+'</div><div class="dzx"><b>Зброя місяця: '+esc(W.uk)+' · ×'+mul+(r.kit?' (Набір)':'')+'</b><small>Постріл ≈ '+fs(Math.round(u))+' шкоди · лише в рейді</small></div><span style="font:700 15px system-ui;color:#ffd978">'+fs(r.am)+'<small style="display:block;font-size:9.5px;color:#bfa77a;font-weight:600">зарядів</small></span></div>';
 var can1=r.am>=1&&f<1,can10=r.am>=10&&f<1;
 h+='<div style="display:flex;gap:8px"><button class="dzb g dzbig'+(can1?'':' off')+'" style="flex:2;margin-top:6px" data-z="s1">Постріл · −1 заряд</button><button class="dzb dzbig'+(can10?'':' off')+'" style="flex:1;margin-top:6px;font-size:13px" data-z="s10">×10</button></div>';
 h+='<button class="dzb dkhelp" style="width:100%;margin-top:7px" data-z="gp" data-k="0">📖 Як це працює? Путівник</button>';
 if(r.log.length){h+='<div class="dzlog" style="text-align:left">';r.log.slice().reverse().forEach(function(l){h+='<div>'+esc(l)+'</div>'});h+='</div>'}
 /* заряди */
 h+='<div class="dzs"><h4>Заряди: де взяти</h4>';
 h+='<div class="dzrow'+(rationReady()?' cu':' dn')+'"><div class="dzn">🍞</div><div class="dzx"><b>Щоденний пайок</b><small>+'+RATION+' зарядів, раз на день · безкоштовно</small></div>'+(rationReady()?'<button class="dzb g" data-z="ra">Забрати</button>':'<span style="color:#8fcf7a">✓</span>')+'</div>';
 var td=P.day(),ea=(r.ea.d===td)?r.ea:{bk:0,hn:0,dw:0},ln=[];
 for(var k in SRC)ln.push(SRC[k].n+': +'+SRC[k].per+' ('+(ea[k]||0)+'/'+SRC[k].cap+' сьогодні)');
 h+='<small style="display:block;color:#bfa77a;margin:2px 2px 8px;line-height:1.35">🆓 Безкоштовно, поки граєш: '+ln.join(' · ')+'.</small>';
 h+='<small style="display:block;color:#ffd978;margin:0 2px 5px">💰 За талери — швидше (у тебе '+(S.tl||0)+'):</small><div style="display:flex;gap:6px">';
 SHOP.forEach(function(p,i){h+='<button class="dzb'+((S.tl||0)>=p[1]?'':' off')+'" style="flex:1;padding:8px 2px;font-size:12px" data-z="by" data-k="'+i+'">'+p[0]+' зар.<br><b>'+p[1]+' 💰</b></button>'});h+='</div>';
 h+='<button class="dzb'+(r.kit?' off':((S.tl||0)>=KIT.tl?' g':' off'))+' dzbig" style="margin-top:8px;font-size:13px" data-z="kit">'+(r.kit?'✓ Набір рейду куплено (шкода ×'+KITMUL+')':'⚡ Набір рейду · '+KIT.tl+' 💰 → шкода ×'+KITMUL+' і +'+KIT.am+' зарядів')+'</button></div>';
 /* рубежі */
 h+='<div class="dzs"><h4>Рубежі боса (спільно)</h4>';
 MS.forEach(function(m,i){var ok=f>=m[0],got=r.c[i],can=ok&&!got&&r.dm>=need(r),sub;
  if(got)sub='Отримано';
  else if(ok&&r.dm<need(r))sub='Рубіж досягнуто, але ти вдарив мало: ще ≈'+shotsFor(r,need(r))+' пострілів, щоб брати';
  else if(ok)sub='Готово — можна забрати';
  else{sub=m[0]<=BOTSHARE?'Боти самі дійдуть: ~'+P.fmtLeft(Math.max(0,(m[0]/BOTSHARE-fracTime(r.m))*dim(r.m)*864e5)):'Боти самі не дійдуть — треба й твій внесок'}
  h+='<div class="dzrow'+(got?' dn':(can?' cu':''))+'"><div class="dzn">'+(got?'✓':Math.round(m[0]*100))+'</div><div class="dzx"><b>'+Math.round(m[0]*100)+'% боса</b><small>'+P.rewTxt(m[1])+'</small><small style="color:#bfa77a">'+esc(sub)+'</small></div>'+(got?'<span style="color:#8fcf7a">✓</span>':(can?'<button class="dzb g" data-z="cm" data-k="'+i+'">Забрати</button>':'<span style="opacity:.5">🔒</span>'))+'</div>'});
 h+='</div>';
 /* особисті щаблі */
 h+='<div class="dzs"><h4>Твій внесок (особисті щаблі)</h4>';
 TIERS.forEach(function(t,i){var goal=t[0]*r.ref,ok=r.dm>=goal,got=r.pc[i],can=ok&&!got,pr=Math.min(100,r.dm/goal*100);
  h+='<div class="dzrow'+(got?' dn':(can?' cu':''))+'"><div class="dzn">'+(got?'✓':(i+1))+'</div><div class="dzx"><b>«'+t[1]+'» · '+fp(pctOf(r,goal))+'% боса</b><small>'+P.rewTxt(t[2])+(t[3]?' · +'+t[3]+' зарядів':'')+'</small><div class="dzbar" style="height:5px"><i style="width:'+pr.toFixed(0)+'%"></i></div></div>'+(got?'<span style="color:#8fcf7a">✓</span>':(can?'<button class="dzb g" data-z="ct" data-k="'+i+'">Забрати</button>':'<span style="opacity:.5;font-size:11px">'+fs(Math.max(0,goal-r.dm))+'</span>'))+'</div>'});
 h+='</div>';
 h+='<div class="dzs"><small style="color:#9d8a62;display:block">🤖 Боти умовні — живі гравці з’являться з сервером.</small></div></div>';
 var sc=ov.querySelector(".dzc"),tp=sc?sc.scrollTop:0;ov.innerHTML=h;var n=ov.querySelector(".dzc");if(n)n.scrollTop=tp}
function open(){earn();var d=T(),r=Mo();if(!d.rdSeen){d.rdSeen=1;gp=0;P.save()}else gp=-1;render();ov.classList.add("on")}
function act(k,a){var kk=+a.getAttribute("data-k");
 if(k=="s1")shoot(1);else if(k=="s10")shoot(10);else if(k=="ra")ration();else if(k=="by")buy(kk);else if(k=="kit")buyKit();
 else if(k=="cm")claimMs(kk);else if(k=="ct")claimTier(kk);else if(k=="gp"){gp=kk;render()}}
function boot(){ov=P.ov("dzR",act);
 window.D9R={open:open,ready:ready,hint:hint,state:Mo,shoot:shoot,earn:earn,ration:ration,shotsToday:function(){var r=Mo();return sdToday(r)},frac:function(){return frac(Mo())},MS:MS,TIERS:TIERS};
 try{Mo()}catch(e){}earn();setInterval(earn,6000)}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
