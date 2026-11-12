(function(){
/* v359: «Арена» = «Хутори»: 4 хутора, на каждом хозяин-бот. Выиграл дуэль — хутор твой, раз в 5 ч капает серебро («Зібрати все»), боты иногда отбивают хутор назад. Без сервера. Числа — черновик. */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc;
var KH=[{n:"Вовчий Яр",ic:"🐺",inc:60,hpm:7,dm:.10},{n:"Три Дуби",ic:"🌳",inc:140,hpm:10,dm:.14},{n:"Сліпий Колодязь",ic:"🕳",inc:300,hpm:14,dm:.19},{n:"Чортова Круча",ic:"👹",inc:650,hpm:20,dm:.25}];
var BN=["Грицько Бульба","Тарас Кривий","Мирон Ворон","Оксана Сіркова","Явтух Мотика","Горпина Грізна","Левко Шаблюка","Ганна Нестримна","Панас Чуб","Мотря Гопак","Семен Півень","Катря Вишиванка"];
var INTV=5*3600e3,CAP=3,BLK=6*3600e3,RETAKE=.28,COST=2;
function A(){var d=T();if(!d.ar)d.ar={h:[],pl:{d:"",w:0},note:[]};var a=d.ar;if(!a.wt)a.wt={n:0,at:Date.now()};for(var i=0;i<4;i++){if(!a.h[i])a.h[i]={o:0,last:0,pend:0,chk:0,b:BN[i*3%12]}}return a}
/* Розшук: перемоги на арені привертають увагу; від 3 зірок на тебе полюють — бій тяжчий, нагорода +50% */
function heat(){var a=A(),w=a.wt,now=Date.now(),dec=Math.floor((now-w.at)/(12*3600e3));if(dec>0){w.n=Math.max(0,w.n-dec);w.at=w.n>0?w.at+dec*12*3600e3:now}return w.n}
function wanted(){return heat()>=3}
function bribeCost(){return Math.round(200+(S.lv||1)*60)}
function bribe(){var a=A(),n=heat();if(!n){P.say("Писар тебе не знає. Розшуку нема.");return}
 var c=bribeCost();if((S.sv||0)<c){P.say("Бракує срібла писареві: треба "+P.fs(c)+" 🥈. «Совість у нього дешева, та не безкоштовна».");return}
 S.sv-=c;a.wt={n:0,at:Date.now()};try{draw()}catch(e){}P.save();P.cnt("brb");P.toast("Писар «загубив» твою справу за "+P.fs(c)+" 🥈. Розшук знято.")}
function ret(){var r=RETAKE+.03*heat();try{r*=1-.17*(P.petSk?P.petSk(1):0)}catch(e){}return Math.max(.03,r)}
function bl(i){return Math.max(1,Math.round((S.lv||1)*[.7,.9,1.1,1.4][i]))}
function inc(h,i,t){return Math.min(CAP,Math.floor((t-h.last)/INTV))*KH[i].inc}
function sync(){var a=A(),now=Date.now(),ch=0;
 a.h.forEach(function(h,i){if(!h.o)return;var t=h.chk||now;
  while(t+BLK<=now){t+=BLK;var r=P.rng("kh"+i+"|"+h.last+"|"+t);if(r()<ret()){h.pend+=inc(h,i,t);h.o=0;var q=P.rng("b"+i+"|"+t);h.b=BN[Math.floor(q()*BN.length)];a.note.push("Козак "+h.b+" відбив хутір «"+KH[i].n+"». Забери своє й відіграйся.");ch=1;break}}
  if(h.o)h.chk=Math.min(t,now);else h.chk=now});
 if(ch)P.save()}
function total(){sync();var a=A(),now=Date.now(),s=0;a.h.forEach(function(h,i){s+=h.pend||0;if(h.o)s+=inc(h,i,now)});return s}
function ready(){return total()>0?1:0}
function collect(){var a=A(),now=Date.now(),s=total();if(!s){P.say("Хутори поки порожні: дохід капає раз на 5 годин.");return}
 a.h.forEach(function(h,i){h.pend=0;if(h.o){var n=Math.floor((now-h.last)/INTV);if(n>=CAP)h.last=now;else h.last+=n*INTV}});
 P.cnt("arcol");P.give({sv:s});P.toast("Зібрано з хуторів: "+P.fs(s)+" 🥈. «Не ми такі — життя таке».")}
function winsToday(){var p=A().pl;return p.d===P.day()?p.w:0}
/* ---- дуэль ---- */
var D=null,tm=0,ov,view="list";
function stop(){if(tm){clearInterval(tm);tm=0}}
function start(i){sync();var a=A(),h=a.h[i];if(h.o)return;if((S.en||0)<COST){P.say("Бракує енергії для дуелі: треба "+COST+" ⚡.");return}
 S.en-=COST;try{draw()}catch(e){}
 var wn=wanted(),k=KH[i],pw=12+(S.pw||0)*.035+(S.lv||1)*1.5,hpm=Math.round(90+(S.lv||1)*4+(S.pw||0)*.02),n=Date.now();
 D={i:i,pw:pw,php:hpm,phm:hpm,ehp:Math.round(pw*k.hpm*(wn?1.25:1)),ehm:Math.round(pw*k.hpm*(wn?1.25:1)),ed:Math.max(3,Math.round(hpm*k.dm*(wn?1.2:1))),wn:wn,ph:"wait",nextAt:n+1200,teleEnd:0,type:"",par:0,wr:0,ctr:0,scd:0,stun:0,over:0,log:"Дуель почалась! Дивись на значок і тисни потрібну кнопку."};
 view="duel";render();stop();tm=setInterval(loop,50)}
function loop(){if(!D||D.over){stop();return}var n=Date.now(),k=KH[D.i];
 if(D.ph=="wait"&&n>=D.nextAt&&n>=D.stun){D.ph="tele";D.type=Math.random()<.5?"H":"W";D.dur=Math.max(640,1180-D.i*120);D.teleEnd=n+D.dur;D.par=0;D.wr=0;tele(1)}
 else if(D.ph=="tele"&&n>=D.teleEnd){
  if(D.par){D.ctr=1;D.stun=n+800;D.log="Парирував! Наступний удар — подвійний.";D.ph="wait";D.nextAt=n+800+700+Math.random()*700}
  else{var dm=Math.round(D.ed*(D.wr?.7:1)*(.85+Math.random()*.3));D.php-=dm;D.log="Влучили! −"+dm+" здоров'я.";D.ph="wait";D.nextAt=n+1000+Math.random()*(1000-D.i*120);var c=ov&&ov.querySelector(".dzc");if(c){c.classList.remove("dzshk");void c.offsetWidth;c.classList.add("dzshk")}
   if(D.php<=0){D.php=0;finish(false);return}}
  tele(0)}
 paint()}
function tele(on){var r=ov&&ov.querySelector(".dzring"),b=ov&&ov.querySelector(".dztele .big"),t=ov&&ov.querySelector(".dztele .tx");if(!r)return;
 if(on){b.textContent=D.type=="H"?"⬆️":"↔️";t.textContent=D.type=="H"?"ВИСОКИЙ УДАР — тисни БЛОК":"ШИРОКИЙ ЗАМАХ — тисни УХИЛ";r.style.setProperty("--dur",D.dur+"ms");r.classList.remove("go");void r.offsetWidth;r.classList.add("go")}
 else{b.textContent="🗡";t.textContent="";r.classList.remove("go")}}
function paint(){if(!D||!ov)return;var e=ov.querySelector("#dzAe"),p=ov.querySelector("#dzAp"),l=ov.querySelector(".dzlog");
 if(e){e.firstChild.style.width=Math.max(0,D.ehp/D.ehm*100)+"%";e.lastChild.textContent=Math.max(0,Math.round(D.ehp))+" / "+D.ehm}
 if(p){p.firstChild.style.width=Math.max(0,D.php/D.phm*100)+"%";p.lastChild.textContent=Math.max(0,Math.round(D.php))+" / "+D.phm}
 if(l)l.textContent=D.log;
 var s=ov.querySelector('[data-z="hit"]');if(s)s.style.opacity=(Date.now()<D.scd)?".55":""}
function press(w){if(!D||D.over)return;var n=Date.now();
 if(w=="B"||w=="W2"){var need=(w=="B")?"H":"W";if(D.ph=="tele"){if(D.type==need)D.par=1;else D.wr=1}return}
 if(w=="S"){if(n<D.scd)return;var dm=D.pw*(D.ctr?2.4:1)*(.85+Math.random()*.3),cr=Math.random()<.1;if(cr)dm*=1.6;D.ehp-=dm;D.scd=n+520;D.log=(D.ctr?"Контрудар! ":cr?"Критичний! ":"")+"−"+Math.round(dm)+" ворогові.";D.ctr=0;paint();if(D.ehp<=0){D.ehp=0;finish(true)}}}
function finish(win){if(!D)return;D.over=1;stop();var i=D.i,k=KH[i],a=A(),h=a.h[i],now=Date.now();
 if(win){h.o=1;h.last=now;h.chk=now;var rw={sv:Math.round(k.inc*.6*(D.wn?1.5:1))};P.cnt("arw");a.pl={d:P.day(),w:winsToday()+1};a.wt={n:Math.min(5,heat()+1),at:Date.now()};P.give(rw);P.toast("Хутір «"+k.n+"» твій! +"+P.rewTxt(rw)+". Дохід капає раз на 5 годин.")}
 else{P.say("Тебе вигнали з хутора «"+k.n+"». Козак, який втік, воює вдруге.");P.save()}
 D=null;view="list";render()}
/* ---- экран ---- */
function listHTML(){sync();var a=A(),now=Date.now(),s=total(),h="",ht=heat(),pips="";
 h+='<div class="dzk">'+P.kob(3)+'</div>';
 for(var q=0;q<5;q++)pips+=q<ht?'★':'☆';
 h+='<div class="dzrow'+(ht>=3?' cu':'')+'"><div class="dzn">'+(ht>=3?'🚨':'🕵')+'</div><div class="dzx"><b>Розшук <span style="color:#ffd978;letter-spacing:2px">'+pips+'</span></b><small>'+(ht>=3?'На тебе полюють: господарі лютіші (+25% здоров\'я, +20% шкоди), але нагорода за перемогу +50%. Хутори відбивають частіше.':ht?'Про тебе вже шепочуться. З 3 зірок на тебе почнуть полювати.':'Тебе ніхто не знає. Поки що.')+(ht?' Зірка тане раз на 12 год.':'')+'</small></div>'+(ht?'<button class="dzb" data-z="brb">Підкупити · '+P.fs(bribeCost())+' 🥈</button>':'')+'</div>';
 (a.note||[]).forEach(function(n){h+='<div class="dzrow cu"><div class="dzn">⚔️</div><div class="dzx"><small>'+esc(n)+'</small></div></div>'});a.note=[];
 h+='<div class="dzrow'+(s?' cu':'')+'"><div class="dzn">🥈</div><div class="dzx"><b>Дохід з хуторів: '+P.fs(s)+'</b><small>Капає раз на '+(INTV/3600e3)+' год, накопичується до '+CAP+' разів</small></div><button class="dzb g'+(s?'':' off')+'" data-z="col">Зібрати все</button></div>';
 var mine=a.h.filter(function(x){return x.o}).length;
 h+='<div class="dzs"><h4>Хутори · твоїх: '+mine+' / 4 · дуель −'+COST+' ⚡</h4>';
 KH.forEach(function(k,i){var x=a.h[i],pw=inc(x,i,now);
  h+='<div class="dzrow'+(x.o?' dn':'')+'"><div class="dzn" style="font-size:16px">'+k.ic+'</div><div class="dzx"><b>'+k.n+'</b><small>'+(x.o?'Твій · '+k.inc+' 🥈 за '+(INTV/3600e3)+' год'+(pw?' · зараз '+P.fs(pw):''):'Господар: '+esc(x.b)+' (рівень '+bl(i)+') · '+k.inc+' 🥈 за '+(INTV/3600e3)+' год')+'</small></div>'+(x.o?'<span style="color:#8fcf7a">✓</span>':'<button class="dzb r" data-z="duel" data-k="'+i+'">Бій</button>')+'</div>'});
 h+='</div><small style="color:#9d8a62;display:block;margin-top:8px">Бот може відбити хутір: приблизно раз на кілька діб. Сильніші хутори — сильніші господарі. Живих суперників додамо разом із сервером.</small>';
 return h}
function duelHTML(){var k=KH[D.i];return '<div class="dzk">Дивись на значок посередині: високий удар — БЛОК, широкий замах — УХИЛ. Вдале парирування дає подвійний контрудар.</div>'+
 '<div class="dzs" style="border:0;margin:0;padding:0"><h4>'+k.ic+' '+k.n+' · господар '+esc(A().h[D.i].b)+'</h4></div>'+
 '<div class="dzhp e" id="dzAe"><i style="width:100%"></i><span></span></div>'+
 '<div class="dztele"><div class="dzring"></div><div class="big">🗡</div><div class="tx"></div></div>'+
 '<div class="dzhp p" id="dzAp"><i style="width:100%"></i><span></span></div>'+
 '<div class="dzlog"></div>'+
 '<div class="dzbtns" style="margin-top:8px"><button class="dzb" data-z="blk">🛡 Блок</button><button class="dzb" data-z="dg">💨 Ухил</button><button class="dzb g" data-z="hit">⚔ Удар</button></div>'+
 '<button class="dzb dzbig" data-z="flee">Втекти (енергію не повернуть)</button>'}
function render(){if(!ov)return;
 var h='<div class="dzc"><div class="dzt"><b>🏟 Арена · Хутори</b><button data-z="x" aria-label="Закрити">✕</button></div>'+(view=="duel"&&D?duelHTML():listHTML())+'</div>';
 ov.innerHTML=h;if(view=="duel"&&D){paint();if(D.ph=="tele")tele(1)}}
function open(){if(D)return;view="list";render();ov.classList.add("on")}
function act(k,a){var kk=a.getAttribute("data-k");
 if(k=="col"){collect();render();return}
 if(k=="brb"){bribe();render();return}
 if(k=="duel"){start(+kk);return}
 if(k=="blk"){press("B");return}
 if(k=="dg"){press("W2");return}
 if(k=="hit"){press("S");return}
 if(k=="flee"){if(D){D.over=1;stop();D=null;P.say("Втік. Хутір почекає.")}view="list";render();return}}
function boot(){ov=P.ov("dzA",act);ov._onclose=function(){if(D){D.over=1;stop();D=null}view="list"};
 var fn=function(e){var el=e.target.closest&&e.target.closest('[data-a="arena"],[data-g="arena"]');if(!el)return;if(!el.closest("#nav2,#mnav2,#dnav2"))return;e.stopPropagation();e.preventDefault();open()};
 document.addEventListener("click",fn,true);
 window.D9A={heat:heat,bribe:bribe,open:open,ready:ready,winsToday:winsToday,collect:collect,total:total,KH:KH,start:start,press:press,state:A,sync:sync,dbg:function(){return D}}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
