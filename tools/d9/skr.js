(function(){
/* v359: «Скриня» (все добро в одном месте) и «Колекції» по локациям похода: 7 предметов, обмен на награду, «Збирач» добивает половину */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc;
var SETS={
 field:{n:"Дике поле",ic:"🌾",rw:{sv:700,en:10},it:[["🪶","Орлине перо"],["🏺","Глечик без дна"],["🦴","Кістка-невдаха"],["🧣","Чумацька хустка"],["🔔","Дзвоник від отари"],["🪙","Старий шеляг"],["🥚","Яйце нічийне"]]},
 oak:{n:"Дубрава",ic:"🌲",rw:{sv:1600,junk:5},it:[["🍄","Мухомор-красень"],["🪵","Гілка-макогін"],["🐗","Ікло кабана"],["🕸","Павутина з росою"],["🦉","Перо сови-філософа"],["🌰","Золотий жолудь"],["🪓","Іржава сокира"]]},
 farm:{n:"Хутір",ic:"🏡",rw:{sv:3200,tl:1,junk:6},it:[["🥛","Глечик сметани"],["🧅","Цибулина-мислитель"],["🐓","Гребінь півня"],["🧵","Рушник з вишивкою"],["🥖","Паляниця"],["🪣","Відро з-під борщу"],["🍯","Бджолиний мед"]]},
 kurgan:{n:"Курган",ic:"⛰",rw:{sv:6500,tl:3,junk:10},it:[["⚱️","Урна давніх"],["🏹","Скіфська стріла"],["💍","Каблучка без імені"],["📜","Грамота без печатки"],["🛡","Бронзовий щиток"],["🦷","Зуб велетня"],["🔱","Тризуб у пилюці"]]}};
var ORDER=["field","oak","farm","kurgan"],HELP_CD=20*3600*1000;
function C(){var d=T();if(!d.co)d.co={h:{},help:0};ORDER.forEach(function(k){if(!d.co.h[k])d.co.h[k]=[0,0,0,0,0,0,0]});return d.co}
function distinct(k){return C().h[k].filter(function(x){return x>0}).length}
function full(k){return C().h[k].every(function(x){return x>0})}
function drop(loc,n,fin){if(!SETS[loc])return;var c=C().h[loc],got=[];
 for(var q=0;q<n;q++){var w=c.map(function(x){return x>0?1:3}),sum=w.reduce(function(a,b){return a+b},0),r=Math.random()*sum,i=0;for(;i<w.length-1;i++){r-=w[i];if(r<=0)break}c[i]++;got.push(i)}
 P.save();var s=SETS[loc];
 return got.map(function(i){return s.it[i][0]+" "+s.it[i][1]}).join(", ")+" ("+s.n+" "+distinct(loc)+"/7)"}
function ready(){return ORDER.filter(full).length}
P.reg.col=ready;
function exch(k){if(!full(k))return;var c=C().h[k];for(var i=0;i<7;i++)c[i]--;P.cnt("cx");P.give(SETS[k].rw);P.toast("Колекція «"+SETS[k].n+"» обміняна: "+P.rewTxt(SETS[k].rw))}
function help(k){var co=C();if(Date.now()<co.help){P.say("Збирач ще відпочиває: "+P.fmtLeft(co.help-Date.now()));return}
 if(distinct(k)<4||full(k)){P.say("Збирач допомагає, коли в наборі 4–6 з 7 предметів.");return}
 var c=co.h[k],miss=[];c.forEach(function(x,i){if(!x)miss.push(i)});var i=miss[Math.floor(Math.random()*miss.length)];c[i]++;co.help=Date.now()+HELP_CD;P.save();
 P.toast("Збирач Бульбаш витяг із кишені: "+SETS[k].it[i][0]+" "+SETS[k].it[i][1]+". «Тільки нікому, козаче».")}
/* ---- хуки в похід ---- */
function sn(){return .07+.015*(P.petSk?P.petSk(0):0)}
function hook(){
 var hf=window.hFinish;if(typeof hf=="function"&&!hf._d9){var n=function(ok){var loc=window.HK&&HK.loc,r=hf.apply(this,arguments);try{if(loc){var t=drop(loc,(ok?2:1)+(Math.random()<.12*(P.petSk?P.petSk(0):0)?1:0),true);if(t&&window.HK&&HK.res&&HK.res.items)HK.res.items.push("🧩 Знахідка для колекції: "+t)}}catch(e){}return r};n._d9=1;window.hFinish=hFinish=n}
 var hs=window.hStep;if(typeof hs=="function"&&!hs._d9){var m=function(){var loc=window.HK&&HK.loc,s0=window.HK&&HK.step,r=hs.apply(this,arguments);try{if(loc&&window.HK&&HK.step>s0&&Math.random()<sn()){var t=drop(loc,1,false);if(t)P.toast("Знахідка: "+t)}}catch(e){}return r};m._d9=1;window.hStep=hStep=m}}
 var H=window.HMAP;if(H&&typeof H.go=="function"&&!H.go._d9){var g=H.go,q=function(id){var loc=window.HK&&HK.loc,s0=window.HK&&HK.step,r=g.apply(this,arguments);try{if(loc&&window.HK&&HK.step>s0&&Math.random()<sn()){var t=drop(loc,1,false);if(t)P.toast("Знахідка: "+t)}}catch(e){}return r};q._d9=1;H.go=q}
/* ---- экраны ---- */
var ov,view="skr";
function colHTML(){var h="";
 ORDER.forEach(function(k){var s=SETS[k],c=C().h[k],d=distinct(k);
  h+='<div class="dzs" style="'+(k=="field"?'border:0;margin:0;padding:0':'')+'"><h4>'+s.ic+' '+s.n+' · '+d+' / 7</h4><div>';
  s.it.forEach(function(it,i){h+='<div class="dzcell'+(c[i]?' h':'')+'"><span>'+it[0]+'</span><small>'+esc(it[1])+'</small>'+(c[i]>1?'<em>×'+c[i]+'</em>':'')+'</div>'});
  h+='</div><div class="dzrow'+(full(k)?' cu':'')+'" style="margin-top:6px"><div class="dzx"><small>Набір → '+P.rewTxt(s.rw)+'</small></div>';
  if(d>=4&&!full(k))h+='<button class="dzb" data-z="help" data-k="'+k+'">Збирач</button>';
  h+='<button class="dzb g'+(full(k)?'':' off')+'" data-z="exch" data-k="'+k+'">Обміняти</button></div></div>'});
 h+='<small style="color:#9d8a62;display:block;margin-top:6px">Предмети знаходяться в походах цієї локації: по дорозі й коли повертаєшся. «Збирач» раз на 20 годин добиває набір, якщо в ньому вже 4+ предмети.</small>';
 return h}
function bd(o){var n=0;try{n=o&&o.ready?o.ready():0}catch(e){}return n?' <i style="font-style:normal;background:#c8261c;color:#fff;border-radius:8px;padding:0 5px;font:700 10px system-ui">'+n+'</i>':''}
function skrHTML(){var h='<div class="dzgrid">'+
 '<div class="dztile" data-z="col"><span>🧩</span>Колекції'+(ready()?' ('+ready()+')':'')+'</div>'+
 '<div class="dztile" data-z="junk"><span>🧰</span>Торговець</div>'+
 '<div class="dztile" data-z="trof"><span>🏆</span>Трофеї</div>'+
 '<div class="dztile" data-z="ring"><span>💍</span>Перстні</div>'+
 '<div class="dztile" data-z="smith"><span>🔨</span>Коваль</div>'+
 '<div class="dztile" data-z="lit"><span>📜</span>Літопис</div>'+
 '<div class="dztile" data-z="pet"><span>🐈</span>Кіт'+(window.D9P&&!D9P.own()?' 🔒':bd(window.D9P))+'</div>'+
 '<div class="dztile" data-z="wheel"><span>🎡</span>Колесо'+bd(window.D9W)+'</div>'+
 '<div class="dztile" data-z="siege"><span>🏰</span>Облога'+bd(window.D9G)+'</div></div>';
 var j=S.junk||{};h+='<div class="dzchips" style="margin-top:10px"><span>🥈 '+P.fs(S.sv||0)+'</span><span>💰 '+P.fs(S.tl||0)+'</span><span>🔩 Хлам '+(j.bal||0)+'</span><span>🔫 Самопалів '+(S.fz||0)+'</span></div>';
 return h}
function render(){if(!ov)return;var h='<div class="dzc"><div class="dzt"><b>'+(view=="col"?'🧩 Колекції':'📦 Скриня')+'</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 if(view=="col")h+=colHTML()+'<button class="dzb dzbig" data-z="back">← До скрині</button>';else h+=skrHTML();
 h+='</div>';var sc=ov.querySelector(".dzc"),top=sc?sc.scrollTop:0;ov.innerHTML=h;var n=ov.querySelector(".dzc");if(n)n.scrollTop=top}
function open(v){view=v||"skr";render();ov.classList.add("on")}
function act(k,a){var kk=a.getAttribute("data-k");
 if(k=="col"){view="col";render();return}
 if(k=="back"){view="skr";render();return}
 if(k=="exch"){exch(kk);render();return}
 if(k=="help"){help(kk);render();return}
 P.shut(ov);
 setTimeout(function(){
  if(k=="junk"&&window.JUNK&&JUNK.open)JUNK.open();
  else if(k=="trof"&&window.TROPHY&&TROPHY.open)TROPHY.open();
  else if(k=="ring"&&window.jwOpen)jwOpen("rings");
  else if(k=="smith"&&window.jwOpen)jwOpen("forge");
  else if(k=="lit"&&window.D9H)D9H.open()
  else if(k=="pet"&&window.D9P)D9P.open()
  else if(k=="wheel"&&window.D9W)D9W.open()
  else if(k=="siege"&&window.D9G)D9G.open()},60)}
function boot(){ov=P.ov("dzS",act);hook();window.D9S={open:open,ready:ready,drop:drop,state:C,sets:SETS,exch:exch}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
