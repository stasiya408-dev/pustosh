(function(){
/* v361: «Колесо фортуни» (как у «Братвы и кольца»): первая крутка в день бесплатная, дальше цена растёт; лента чужих выигрышей (боты). Без сервера. Числа — черновик. */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc,fs=P.fs;
var COST=[0,300,700,1500,3000,6000];
var SEC=[
 {ic:"🥈",t:"Жменя шелягів",w:26,c:"#7a5a2a"},
 {ic:"👛",t:"Мішок срібла",w:14,c:"#a2481e"},
 {ic:"🍵",t:"Бочка узвару",w:16,c:"#4f6f2c"},
 {ic:"🔩",t:"Хлам із воза",w:16,c:"#5d4a38"},
 {ic:"🔫",t:"Два самопали",w:10,c:"#3d5a73"},
 {ic:"🧩",t:"Знахідка для колекції",w:10,c:"#6d3d6f"},
 {ic:"💰",t:"Талер",w:6,c:"#b08a1c"},
 {ic:"🎁",t:"Скриня гетьмана",w:2,c:"#b02a2a"}];
var BOTS=["Грицько Мотика","Оксана Сіркова","Тарас Кривий","Мирон Ворон","Явтух Бузько","Горпина Остапівна","Левко Шаблюка","Ганна Нестримна","Панас Чуб","Мотря Гопак","Семен Півень","Катря Вишиванка","Прокіп Вус","Зіня Чорнобрива"];
function base(){return 300+30*(S.lv||1)}
function W(){var d=T(),td=P.day();if(!d.wh||d.wh.d!==td){var old=d.wh;d.wh={d:td,n:0,tot:(old&&old.tot)||0,my:(old&&old.my)||[]}}return d.wh}
function cost(){var n=W().n;return n>=COST.length?null:COST[n]}
function ready(){var w=W();return w.n===0?1:0}
P.reg.wheel=ready;
function pick(r){var sum=SEC.reduce(function(a,b){return a+b.w},0),x=r*sum,i=0;for(;i<SEC.length-1;i++){x-=SEC[i].w;if(x<0)break}return i}
function prizeText(i,v){return SEC[i].ic+" "+SEC[i].t+(v?" · "+v:"")}
/* выдать приз, вернуть текст */
function award(i){var b=base(),t="";
 if(i==0){P.give({sv:b});t=fs(b)+" 🥈"}
 else if(i==1){P.give({sv:b*3});t=fs(b*3)+" 🥈"}
 else if(i==2){P.give({en:8});t="8 ⚡"}
 else if(i==3){P.give({junk:3});t="3 🔩"}
 else if(i==4){S.fz=(S.fz||0)+2;try{draw()}catch(e){}P.save();t="2 🔫"}
 else if(i==5){var o=window.D9S,k=null;
  if(o){var h=o.state().h,ks=Object.keys(h).filter(function(q){return h[q].some(function(x){return !x})});if(!ks.length)ks=Object.keys(h);k=ks[Math.floor(Math.random()*ks.length)];t=o.drop(k,1)||""}
  if(!t){P.give({sv:b});t=fs(b)+" 🥈 (колекції порожні)"}}
 else if(i==6){P.give({tl:1});t="1 💰"}
 else{P.give({tl:10,sv:b*8,junk:5});t="10 💰 · "+fs(b*8)+" 🥈 · 5 🔩"}
 return t}
/* лента: боты + я */
function feed(){var now=Date.now(),SL=9*60e3,t0=Math.floor(now/SL),out=[];
 for(var k=0;k<6;k++){var t=t0-k,r=P.rng("wh|"+t),nm=BOTS[Math.floor(r()*BOTS.length)],i=pick(r());out.push({t:t*SL+Math.floor(r()*SL*.9),n:nm,i:i,bot:1})}
 W().my.slice(-3).forEach(function(m){out.push({t:m.t,n:"Ти",i:m.i,me:1})});
 out.sort(function(a,b){return b.t-a.t});return out.slice(0,6)}
function ago(t){var m=Math.max(1,Math.round((Date.now()-t)/60000));return m<60?m+" хв тому":Math.floor(m/60)+" год тому"}
/* ---- экран ---- */
var ov,rot=0,spinning=0,lastTxt="";
function wheelHTML(){var seg=[],lab="";
 SEC.forEach(function(s,i){seg.push(s.c+" "+(i*45)+"deg "+((i+1)*45)+"deg");lab+='<span class="dzwl" style="transform:rotate('+(i*45+22.5)+'deg) translateY(-88px)">'+s.ic+'</span>'});
 return '<div class="dzwp">▼</div><div class="dzwh" id="dzWh" style="background:conic-gradient('+seg.join(",")+');transform:rotate('+rot+'deg)">'+lab+'<div class="dzwc">🎡</div></div>'}
function render(){if(!ov)return;var w=W(),c=cost(),h="";
 h+='<div class="dzc"><div class="dzt"><b>🎡 Колесо фортуни</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 h+='<div class="dzk">'+(w.n===0?'Перша крутка — <b>безкоштовно</b>':'Далі дорожче')+'</div>';
 h+='<div class="dzwrap">'+wheelHTML()+'</div>';
 h+='<div class="dzwr" id="dzWr">'+(lastTxt||'&nbsp;')+'</div>';
 h+='<button class="dzb g dzbig'+(c===null||spinning?' off':'')+'" data-z="spin">'+(c===null?'Колесо зламалось на сьогодні':(c===0?'Крутити — безкоштовно':'Крутити · '+fs(c)+' 🥈'))+' <small style="font-weight:400">(крутка '+Math.min(w.n+1,COST.length)+' з '+COST.length+')</small></button>';
 h+='<div class="dzs"><h4>Призи (шанс)</h4><div class="dzchips">';
 var sum=SEC.reduce(function(a,b){return a+b.w},0);
 SEC.forEach(function(s,i){var v=i==0?fs(base())+' 🥈':i==1?fs(base()*3)+' 🥈':i==2?'8 ⚡':i==3?'3 🔩':i==4?'2 🔫':i==5?'1 предмет':i==6?'1 💰':'10 💰 + срібло';h+='<span>'+s.ic+' '+v+' · '+Math.round(s.w/sum*100)+'%</span>'});
 h+='</div></div>';
 h+='<div class="dzs"><h4>Останні виграші <span style="text-transform:none;letter-spacing:0;font-weight:400;color:#9d8a62">(козаки-боти, живі люди будуть із сервером)</span></h4>';
 feed().forEach(function(f){h+='<div class="dzrow'+(f.me?' me':'')+'" style="padding:5px 9px;margin-bottom:4px"><div class="dzx"><small style="color:#e8d6ab"><b style="display:inline;font-size:12px">'+esc(f.n)+'</b> виграв '+SEC[f.i].ic+' '+SEC[f.i].t+'</small></div><small style="color:#9d8a62;white-space:nowrap">'+ago(f.t)+'</small></div>'});
 h+='</div></div>';
 var sc=ov.querySelector(".dzc"),top=sc?sc.scrollTop:0;ov.innerHTML=h;var n=ov.querySelector(".dzc");if(n)n.scrollTop=top}
function spin(){if(spinning)return;var w=W(),c=cost();if(c===null){P.say("Колесо на сьогодні зламалось.");return}
 if((S.sv||0)<c){P.say("Бракує срібла на кручення: треба "+fs(c)+" 🥈. Колесо в борг не крутить.");return}
 if(c){S.sv-=c;try{draw()}catch(e){}}
 var i=pick(Math.random()),txt=award(i);w.n++;w.tot++;w.my.push({t:Date.now(),i:i});if(w.my.length>10)w.my=w.my.slice(-10);P.cnt("whl");P.save();
 spinning=1;var tgt=360-(i*45+22.5)+(Math.random()*30-15),cur=((rot%360)+360)%360,add=360*5+((tgt-cur+720)%360);rot+=add;
 var el=document.getElementById("dzWh");
 if(el){el.style.transition="transform 3.8s cubic-bezier(.12,.62,.08,1)";void el.offsetWidth;el.style.transform="rotate("+rot+"deg)"}
 var lowfx=document.documentElement.classList.contains("gfx-low");
 var btn=ov.querySelector('[data-z="spin"]');if(btn)btn.classList.add("off");
 setTimeout(function(){spinning=0;lastTxt="Випало: "+prizeText(i,txt);if(i>=6)P.toast("Колесо: "+prizeText(i,txt));try{window.SFX&&SFX.play(i>=6?"fanfare":"ok")}catch(e){}if(ov.classList.contains("on"))render()},lowfx?600:3900)}
function open(){render();ov.classList.add("on")}
function act(k){if(k=="spin")spin()}
function boot(){ov=P.ov("dzW",act);ov._onclose=function(){};
 window.D9W={open:open,ready:ready,spin:spin,state:W,cost:cost,SEC:SEC,pick:pick,award:award,busy:function(){return spinning}}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
