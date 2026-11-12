(function(){
/* v359: Літопис героя, Справи дня, Тиждень (рейтинг с ботами), турнір кісток, звання, майстерність коваля, «Що далі?», правая панель 10 -> 5 */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc,fs=P.fs;
var BOT=["Грицько Мотика","Оксана Сіркова","Тарас Кривий","Мирон Ворон","Явтух Бузько","Горпина Остапівна","Левко Шаблюка","Ганна Нестримна","Охрім-молодший","Мотря Гопак","Панас Чуб","Дмитро Бульбенко","Софія Кобза","Ігнат Макогін","Богдан Шабельський","Катря Вишиванка","Семен Півень","Кіндрат Макітра","Зіня Чорнобрива","Прокіп Вус","Тихін Гармаш","Марко Курінь","Варка Шабельна","Юрко Лиман","Оксен Пилипюк","Данило Дубовий","Устим Козуб","Карпо Півторак","Явдоха Бойко","Назар Кучма","Лукаш Верховод","Мар'яна Хорунжа","Остап Чорновіл","Федір Хвилюн","Орися Сокира","Гнат Горішній","Улита Козацька","Роман Зарічний","Пилип Кобиляка","Тетяна Сіромаха"];
var WEEK_RW=function(place,pts){if(pts<40)return null;if(place==1)return {sv:6000,tl:10,junk:20};if(place==2)return {sv:4000,tl:6,junk:12};if(place==3)return {sv:3000,tl:4,junk:8};if(place<=10)return {sv:1800,tl:2,junk:4};return {sv:700,junk:1}};
function hits(){return (S.dst&&S.dst.hits)||0}
function cnt(k){return (T().cnt&&T().cnt[k])||0}
P.cnt=function(k,n){var d=T();if(!d.cnt)d.cnt={};d.cnt[k]=(d.cnt[k]||0)+(n||1)};
var TASKS=[
 {id:"tav",ic:"🎲",t:"Зіграй партію в кості",d:"Шинкарка Мотрона вже налила — сідай за стіл.",rw:{sv:40},go:"tav",need:1,cur:function(b){return ((S.ds&&S.ds.g)||0)-b.g}},
 {id:"hit",ic:"🎯",t:"Влуч по босу 15 разів",d:"Бос сам себе не переможе.",rw:{sv:60},go:"boss",need:15,cur:function(b){return hits()-b.h}},
 {id:"hike",ic:"🐎",t:"Сходи в похід",d:"Степ сам себе не обшукає.",rw:{sv:80},go:"hike",need:1,cur:function(b){return (S.hn||0)-b.hn}},
 {id:"cmb",ic:"🧩",t:"Розгадай Комбо дня",d:"Писар переплутав послідовність ударів — розплутай.",rw:{sv:40,en:2},go:"combo",need:1,cur:function(){return window.D9K?D9K.playedToday():0}},
 {id:"ar",ic:"🏟",t:"Виграй дуель за хутір",d:"Хутір сам не візьметься, хоч як просить.",rw:{sv:70},go:"arena",need:1,cur:function(){return window.D9A?D9A.winsToday():0}}];
var CHEST={sv:250,tl:2,junk:5,en:5};
var TOUR=[[3,{sv:150}],[6,{sv:400,junk:2}],[10,{sv:900,tl:2,junk:5}]];
function base(){return {g:(S.ds&&S.ds.g)||0,h:hits(),hn:S.hn||0,w:(S.ds&&S.ds.w)||0,k:S.bossKills||0}}
function dd(){var d=T(),td=P.day();if(!d.dd||d.dd.d!==td){d.dd={d:td,b:base(),p:{},chest:0,t:[0,0,0]};P.save()}return d.dd}
/* ---- майстерність коваля ---- */
var MT=[0,3,8,15,25,40,60,85,115,150,200];
function mastUses(){try{var j=PG().jewel||{};return (j.crafted||0)+(j.sharpAttempts||0)+(j.broken||0)}catch(e){return 0}}
function mastLv(){var u=mastUses(),l=0;MT.forEach(function(t,i){if(u>=t)l=i});return l}
function applyMast(){var l=mastLv();try{var F=GAME_CONFIG.BOSSCFG.FORGE;if(F&&F.silver){if(!P._f0){P._f0={};Object.keys(F.silver).forEach(function(k){P._f0[k]=F.silver[k]})}Object.keys(P._f0).forEach(function(k){F.silver[k]=Math.round(P._f0[k]*(1-l*.03))})}}catch(e){}return l}
P.mast=function(){var l=mastLv(),u=mastUses();return {l:l,u:u,disc:l*3,next:MT[l+1]||null,from:MT[l]}};
/* ---- неделя ---- */
function botFinal(n,w){var r=P.rng(n+"|"+w),z=(r()+r()+r()+r()-2)/.577;return Math.min(2600,Math.round(420*Math.exp(.75*z)))}
function weekFrac(){return 1-P.msToWeekEnd()/(7*864e5)}
function standings(w,fin){var d=T(),f=fin?1:weekFrac(),pp=fin?fin.p:((d.wk&&d.wk.p)||0),a=BOT.map(function(n){return {n:n,p:Math.round(botFinal(n,w)*f)}});a.push({n:"Ти",p:pp,me:1});a.sort(function(x,y){return y.p-x.p||(x.me?-1:1)});a.forEach(function(x,i){x.pl=i+1});return a}
function wkSources(){return [[S.bossKills||0,20],[S.hn||0,15],[(S.ds&&S.ds.w)||0,3],[Math.floor(hits()/25),1],[cnt("tasks"),8],[cnt("cmbw"),25],[cnt("arw"),10],[cnt("cx"),20]]}
function wkTick(){var d=T(),w=P.week(),src=wkSources();
 if(!d.wk){d.wk={w:w,p:0,l:src.map(function(x){return x[0]})};P.save();return}
 if(d.wk.w!==w){var old=standings(d.wk.w,{p:d.wk.p}),me=old.filter(function(x){return x.me})[0];
  d.prev={w:d.wk.w,p:d.wk.p,place:me.pl,top:old.slice(0,10).map(function(x){return {n:x.n,p:x.p,me:x.me?1:0,pl:x.pl}}),rw:WEEK_RW(me.pl,d.wk.p),claimed:0};
  d.wk={w:w,p:0,l:src.map(function(x){return x[0]})};P.save();return}
 var add=0;src.forEach(function(x,i){var l=d.wk.l[i];if(l==null){d.wk.l[i]=x[0];return}var dl=x[0]-l;if(dl>0)add+=dl*x[1];d.wk.l[i]=x[0]});
 if(add>0){d.wk.p+=add;P.save()}}
/* ---- главный тик ---- */
function tick(){try{
 if(!window.S||!window.kyivDate)return;
 var d=T(),k=dd();
 TASKS.forEach(function(t){if(!k.p[t.id]&&t.cur(k.b)>=t.need){k.p[t.id]=1;P.cnt("tasks");P.give(t.rw);P.toast("Справа дня виконана: "+t.t+" · "+P.rewTxt(t.rw))}});
 var wins=((S.ds&&S.ds.w)||0)-k.b.w;TOUR.forEach(function(x,i){if(!k.t[i]&&wins>=x[0]){k.t[i]=1;P.give(x[1]);P.toast("Турнір кісток: "+x[0]+" перемог за день · "+P.rewTxt(x[1]))}});
 var rk=P.rank();if(typeof d.rk!="number"){d.rk=rk.i;P.save()}else if(rk.i>d.rk){d.rk=rk.i;var rw={sv:300*rk.i,tl:rk.i*2};P.give(rw);P.toast("Нове звання: "+rk.ic+" "+rk.n+"! "+rk.d+" · "+P.rewTxt(rw))}
 var ml=applyMast();if(typeof d.ml!="number")d.ml=ml;else if(ml>d.ml){d.ml=ml;P.toast("Коваль Омелько: майстерність "+ml+"/10. Ковка дешевшає на "+(ml*3)+"%.")}
 wkTick();badges();
}catch(e){window._d9err=e}}
function chestReady(){var k=dd();return Object.keys(k.p).length>=TASKS.length&&!k.chest}
function prevReady(){var p=T().prev;return !!(p&&p.rw&&!p.claimed)}
function badges(){var n=(chestReady()?1:0)+(prevReady()?1:0);var e=document.querySelector("#l9btn .d9n");if(e)e.textContent=n?String(n):"";
 var s=document.querySelector("#sk9btn .d9n");if(s){var m=window.D9S?D9S.ready():0;s.textContent=m?String(m):""}}
/* ---- Літопис ---- */
var ov,tab="sum";
function bar(a,b){var p=Math.max(0,Math.min(100,Math.round(a/b*100)));return '<div class="dzbar"><i style="width:'+p+'%"></i></div>'}
function tSum(){var r=P.rank(),h="";
 h+='<div class="dzhero"><div class="em">'+r.ic+'</div><div style="flex:1"><b>'+r.n+'</b><small>'+r.d+'</small>';
 if(r.next)h+=bar(r.lv-r.from,r.next[0]-r.from)+'<small style="margin-top:3px">до звання «'+r.next[1]+'»: рівень '+r.lv+' з '+r.next[0]+'</small>';else h+='<small style="margin-top:3px">Вище — тільки небо.</small>';
 h+='</div></div><div class="dzchips"><span>⭐ Рівень '+(S.lv||1)+'</span><span>💪 Сила '+fs(S.pw||0)+'</span><span>🐎 Походів '+(S.hn||0)+'</span><span>💀 Босів '+(S.bossKills||0)+'</span></div>';
 var near=P.near(3);h+='<div class="dzs"><h4>Найближчі досягнення</h4>';
 if(!near.length)h+='<div class="dzx"><small>Усе, що можна було, вже зроблено. Чи ти просто ще не заходив у походи.</small></div>';
 near.forEach(function(x){h+='<div class="dzrow"><div class="dzn">'+x.a[1]+'</div><div class="dzx"><b>'+esc(x.a[2])+'</b><small>'+esc(x.a[3])+'</small>'+bar(x.v,x.t)+'<small style="text-align:right">'+fs(x.v)+' / '+fs(x.t)+'</small></div></div>'});
 h+='</div>';
 var m=P.mast();h+='<div class="dzs"><h4>Коваль Омелько</h4><div class="dzrow"><div class="dzn">🔨</div><div class="dzx"><b>Майстерність '+m.l+' / 10 · знижка '+m.disc+'%</b><small>'+(m.next?'Ще '+(m.next-m.u)+' кувань/заточок до наступного рівня. «Буде добре, якщо не лопне».':'Омелько майстер. Лопає тільки молот.')+'</small>'+(m.next?bar(m.u-m.from,m.next-m.from):'')+'</div></div></div>';
 h+='<div class="dzs"><h4>Куди ще</h4><div class="dzgrid"><div class="dztile" data-z="gach"><span>🏆</span>Усі досягнення</div><div class="dztile" data-z="ach"><span>🍺</span>Кості: досягнення</div><div class="dztile" data-z="rt"><span>📊</span>Рейтинг</div><div class="dztile" data-z="tut"><span>🎯</span>Перші кроки</div><div class="dztile" data-z="ntf"><span>🔔</span>Події</div><div class="dztile" data-z="skr"><span>📦</span>Скриня</div></div></div>';
 return h}
function tDay(){var k=dd(),h="",done=Object.keys(k.p).length;
 h+='<div class="dzs" style="border:0;margin:0;padding:0"><h4>Справи дня · '+done+' / '+TASKS.length+'</h4>';
 TASKS.forEach(function(t,i){var c=Math.max(0,Math.min(t.need,t.cur(k.b))),dn=!!k.p[t.id];
  h+='<div class="dzrow'+(dn?' dn':'')+'"><div class="dzn">'+(dn?'✓':t.ic)+'</div><div class="dzx"><b>'+t.t+'</b><small>'+t.d+'</small>'+(t.need>1?bar(c,t.need)+'<small style="text-align:right">'+c+' / '+t.need+'</small>':'')+'<small>Нагорода: '+P.rewTxt(t.rw)+'</small></div>'+(dn?'':'<button class="dzb" data-z="go" data-k="'+t.go+'">Піти</button>')+'</div>'});
 h+='<div class="dzrow'+(k.chest?' dn':(done>=TASKS.length?' cu':''))+'"><div class="dzn">🎁</div><div class="dzx"><b>Скриня писаря</b><small>Усі п\'ять справ: '+P.rewTxt(CHEST)+'</small></div>'+(k.chest?'<span style="color:#8fcf7a">✓</span>':(done>=TASKS.length?'<button class="dzb g" data-z="chest">Забрати</button>':''))+'</div>';
 h+='<small style="color:#9d8a62">Нові справи через '+P.fmtLeft(P.msToDayEnd())+'</small></div>';
 var wins=((S.ds&&S.ds.w)||0)-k.b.w;
 h+='<div class="dzs"><h4>Турнір кісток · перемог сьогодні: '+wins+'</h4>';
 TOUR.forEach(function(x,i){h+='<div class="dzrow'+(k.t[i]?' dn':'')+'"><div class="dzn">'+(k.t[i]?'✓':x[0])+'</div><div class="dzx"><b>'+x[0]+' перемог за день</b><small>'+P.rewTxt(x[1])+'</small></div></div>'});
 h+='</div>';
 h+='<div class="dzs"><h4>Комбо дня</h4>';
 var st=window.D9K?D9K.status():[0,0,0],nm=["Джура","Козак","Отаман"];
 h+='<div class="dzgrid">';st.forEach(function(s,i){h+='<div class="dztile" data-z="cmb" data-k="'+i+'"><span>'+(s==1?'✅':s==2?'❌':'🧩')+'</span>'+nm[i]+'</div>'});
 h+='</div></div>';
 return h}
function tWeek(){var d=T(),w=P.week(),st=standings(w),me=st.filter(function(x){return x.me})[0],h="";
 h+='<div class="dzhero"><div class="em">🏅</div><div style="flex:1"><b>Ти на '+me.pl+' місці · '+fs(me.p)+' очок</b><small>Тиждень скінчиться через '+P.fmtLeft(P.msToWeekEnd())+'. Суперники — козаки-боти (живі люди будуть після сервера).</small></div></div>';
 var p=d.prev;
 if(p){h+='<div class="dzrow'+(p.rw&&!p.claimed?' cu':'')+'" style="margin-top:9px"><div class="dzn">🎁</div><div class="dzx"><b>Минулий тиждень: '+p.place+' місце, '+fs(p.p)+' очок</b><small>'+(p.rw?(p.claimed?'Скриню забрано':'Скриня: '+P.rewTxt(p.rw)):'Менше 40 очок — скрині не буде. Козак, ти де був?')+'</small></div>'+(p.rw&&!p.claimed?'<button class="dzb g" data-z="wchest">Забрати</button>':'')+'</div>'}
 h+='<div class="dzs"><h4>Топ-10 тижня</h4>';
 st.slice(0,10).forEach(function(x){h+='<div class="dzrow'+(x.me?' me':'')+'"><div class="dzn">'+x.pl+'</div><div class="dzx"><b>'+esc(x.n)+'</b></div><b style="color:#ffd978">'+fs(x.p)+'</b></div>'});
 if(me.pl>10)h+='<div class="dzrow me"><div class="dzn">'+me.pl+'</div><div class="dzx"><b>Ти</b></div><b style="color:#ffd978">'+fs(me.p)+'</b></div>';
 h+='</div>';
 h+='<div class="dzs"><h4>Як набрати очки</h4><div class="dzx"><small>Бос переможений +20 · похід +15 · перемога в кістках +3 · 25 влучань по босу +1 · справа дня +8 · Комбо дня +25 · дуель за хутір +10 · колекція +20.<br>Скриня за місце: 1 — '+P.rewTxt(WEEK_RW(1,99))+'; 2 — '+P.rewTxt(WEEK_RW(2,99))+'; 3 — '+P.rewTxt(WEEK_RW(3,99))+'; Топ-10 — '+P.rewTxt(WEEK_RW(10,99))+'; решта (від 40 очок) — '+P.rewTxt(WEEK_RW(30,99))+'.</small></div></div>';
 return h}
function render(){if(!ov)return;var k=dd(),dn=Object.keys(k.p).length,nb=(chestReady()?1:0);
 var h='<div class="dzc"><div class="dzt"><b>📜 Літопис героя</b><button data-z="x" aria-label="Закрити">✕</button></div><div class="dzk">'+P.kob(1)+'</div>';
 h+='<div class="dztabs"><button data-z="tab" data-k="sum" class="'+(tab=="sum"?'on':'')+'">Зведення</button><button data-z="tab" data-k="day" class="'+(tab=="day"?'on':'')+'">Справи'+(nb?'<i>1</i>':'')+'</button><button data-z="tab" data-k="wk" class="'+(tab=="wk"?'on':'')+'">Тиждень'+(prevReady()?'<i>1</i>':'')+'</button></div>';
 h+=tab=="sum"?tSum():tab=="day"?tDay():tWeek();
 h+='</div>';var sc=ov.querySelector(".dzc"),top=sc?sc.scrollTop:0;ov.innerHTML=h;var n=ov.querySelector(".dzc");if(n)n.scrollTop=top}
function open(t){if(t)tab=t;tick();render();ov.classList.add("on")}
function go(k){P.shut(ov);var m={tav:"tavOpen",boss:"bossOpen",hike:"hikeOpen",market:"marketOpen"};
 setTimeout(function(){if(m[k]&&window[m[k]])window[m[k]]();else if(k=="combo"&&window.D9K)D9K.open();else if(k=="arena"&&window.D9A)D9A.open()},60)}
function act(k,a){var kk=a.getAttribute("data-k");
 if(k=="tab"){tab=kk;render();return}
 if(k=="go"){go(kk);return}
 if(k=="cmb"){P.shut(ov);setTimeout(function(){window.D9K&&D9K.open(+kk)},60);return}
 if(k=="chest"){var d=dd();if(!chestReady())return;d.chest=1;P.give(CHEST);P.toast("Скриня писаря: "+P.rewTxt(CHEST));render();return}
 if(k=="wchest"){var p=T().prev;if(!p||!p.rw||p.claimed)return;p.claimed=1;P.give(p.rw);P.toast("Скриня тижня: "+P.rewTxt(p.rw));render();return}
 if(k=="gach"){P.shut(ov);window.gachOpen&&gachOpen();return}
 if(k=="ach"){P.shut(ov);window.achOpen&&achOpen();return}
 if(k=="rt"){P.shut(ov);window.rtOpen&&rtOpen("hike_score");return}
 if(k=="tut"){P.shut(ov);window.TUT&&TUT.open();return}
 if(k=="ntf"){P.shut(ov);window.NTF&&NTF.open();return}
 if(k=="skr"){P.shut(ov);window.D9S&&D9S.open();return}}
/* ---- «Що далі?» ---- */
var nx;
function R(e,t,s,f){return {e:e,t:t,s:s,go:f}}
function sk(b){return function(){var el=document.querySelector('#nav2 .nb[data-a="'+b+'"]');if(el)el.click()}}
function rec(){
 try{if(window.TUT){var u=TUT.state();if(u&&u.last!==P.day())return R("🎁","Забери нагороду за вхід","Серія днів росте — не губи її",function(){TUT.open()})}}catch(e){}
 try{var rs=window.RAID&&RAID.status&&RAID.status();if(rs&&(rs.k=="open"||rs.k=="claim"||rs.k=="run"))return R("🛡",rs.k=="claim"?"Забери здобич з обозу":"Налетіти на обоз","Вікно відкрите лише декілька годин",function(){var b=document.getElementById("rdbtn");if(b)b.click()})}catch(e){}
 try{var its=window.NTF&&NTF.items;if(typeof its=="function")its=its();if(its){for(var i=0;i<its.length;i++){if(its[i].id=="boss"&&its[i].st=="warn")return R("⏳","Бос скоро втече","Устигни добити його",function(){bossOpen()})}}}catch(e){}
 if(prevReady())return R("🏅","Забери скриню тижня","Минулий тиждень закінчився",function(){open("wk")});
 if(chestReady())return R("🎁","Забери скриню писаря","Усі справи дня виконано",function(){open("day")});
 var cb=window.D9K?D9K.status():[1,1,1];if(cb.indexOf(0)>=0&&cb[0]==0)return R("🧩","Розгадай Комбо дня","Три складності, одна спроба на день",function(){D9K.open()});
 if(window.D9A&&D9A.ready()>0)return R("🏟","Збери дохід з хуторів","Хутори сами себе не збирають",function(){D9A.open()});
 if(window.D9S&&D9S.ready()>0)return R("📦","Обміняй колекцію","Один набір зібрано повністю",function(){D9S.open("col")});
 if((S.en||0)>=MAXEN)return R("⚡","Енергія повна — у похід","Так вона не пропаде",function(){hikeOpen()});
 var k=dd(),nxt=TASKS.filter(function(t){return !k.p[t.id]})[0];
 if(nxt)return R(nxt.ic,nxt.t,nxt.d,function(){go(nxt.go)});
 return R("🍺","Усе зроблено, козаче","Йди випий узвару — завтра нові справи",function(){open("day")})}
function nxPos(){if(!nx)return;
 var nav=document.getElementById("nav2");if(!nav||!nav.offsetParent){nx.style.display="none";return}
 var r=nav.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,e=document.elementFromPoint(cx,cy);
 if(!e||!e.closest("#nav2")||document.documentElement.classList.contains("gdon")||P.anyOpen()){nx.style.display="none";return}
 var x=rec();nx._g=x.go;nx.querySelector(".e").textContent=x.e;nx.querySelector("b").textContent=x.t;nx.querySelector("small").textContent=x.s;
 nx.style.display="flex";nx.style.bottom=Math.round(window.innerHeight-r.top+8)+"px"}
function iconRule(from,to){try{var el=document.getElementById(from),bg=el&&getComputedStyle(el,"::after").backgroundImage;return bg&&bg!="none"?"#app #rpan>#"+to+"::after{background-image:"+bg+"}":""}catch(e){return ""}}
function boot(){
 ov=P.ov("dzL",act);ov._onclose=function(){badges()};
 var rp=document.getElementById("rpan");
 if(rp&&!document.getElementById("l9btn")){
  var css=iconRule("abtn","l9btn")+iconRule("jkbtn","sk9btn");if(css){var st=document.createElement("style");st.id="d9icons";st.textContent=css;document.head.appendChild(st)}
  var a=document.createElement("button");a.id="l9btn";a.setAttribute("aria-label","Літопис");a.innerHTML='<span class="d9n"></span>';a.onclick=function(){open()};rp.insertBefore(a,rp.firstChild);
  var b=document.createElement("button");b.id="sk9btn";b.setAttribute("aria-label","Скриня");b.innerHTML='<span class="d9n"></span>';b.onclick=function(){window.D9S&&D9S.open()};rp.insertBefore(b,a.nextSibling)}
 nx=document.createElement("div");nx.id="nx9";nx.innerHTML='<span class="e">👉</span><div><b>Що далі?</b><small></small></div>';
 nx.addEventListener("click",function(e){e.stopPropagation();if(nx._g)nx._g()});document.body.appendChild(nx);
 setInterval(tick,1500);setInterval(nxPos,800);tick();nxPos();
 window.D9H={open:open,tick:tick,tasks:TASKS,state:function(){return T()},standings:standings,rec:rec,mast:P.mast}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
