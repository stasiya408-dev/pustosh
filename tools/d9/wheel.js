(function(){
/* v386: «Колесо фортуни» на весь экран. Только за талеры: 1 крутка = 8 💰, без лимита. Призы = иконка + число. Джекпот = скриня. Числа МОИ (UNAPPROVED). */
var P=window.D9;if(!P)return;
var T=P.T,fs=P.fs;
var PRICE=8,JP=7;
function base(){return 300+30*(S.lv||1)}
function BS(){try{return ["ostap","nahai","grom"]}catch(e){return ["ostap"]}}
var SEC=[
 {id:"silver",n:function(){return base()},w:24,c:"#6e4a22"},
 {id:"energy",n:function(){return 8},w:14,c:"#3f6b2a"},
 {id:"junk",n:function(){return 4},w:15,c:"#53402e"},
 {id:"silver",n:function(){return base()*4},w:12,c:"#8f3a1a"},
 {id:"pistol",n:function(){return 3},w:10,c:"#2f5470"},
 {id:"ring_shard",n:function(){return 25},w:10,c:"#5e2f66"},
 {id:"taler",n:function(){return 10},w:13,c:"#a07a10"},
 {id:"chest",n:function(){return 0},w:2,c:"#a81f1f",jp:1}];
function icon(id){try{return window.ICO(id)||""}catch(e){return""}}
function W(){var d=T();if(!d.wh||typeof d.wh.tot!=="number")d.wh={tot:0,my:[]};return d.wh}
function cost(){return PRICE}
function ready(){return 0}
P.reg.wheel=ready;
function pick(r){var sum=SEC.reduce(function(a,b){return a+b.w},0),x=r*sum,i=0;for(;i<SEC.length-1;i++){x-=SEC[i].w;if(x<0)break}return i}
/* список выданного: [[iconId,count],...] */
function jackpotItems(){return [["chest",1],["pistol",60],["w_dagger",50],["w_rifle",30],["w_volley",20],["w_cannon",12],["ring_shard",300],["gem_shard",150],["gem",3],["silver",base()*30],["taler",40]]}
function award(i){var s=SEC[i],b=base();
 if(s.jp){var p=window.PG?PG():null;
  S.fz=(S.fz||0)+60;S.wa=S.wa||{};S.wa.dagger=(S.wa.dagger||0)+50;S.wa.rifle=(S.wa.rifle||0)+30;S.wa.volley=(S.wa.volley||0)+20;S.wa.cannon=(S.wa.cannon||0)+12;
  if(p){BS().forEach(function(bid){p.ringShards[bid]=(p.ringShards[bid]||0)+100;p.gemShards[bid]=(p.gemShards[bid]||0)+50;p.gems.push({id:"wh"+Date.now()+bid,t:bid,src:"wheel"})});}
  P.give({sv:b*30,tl:40});try{draw()}catch(e){}P.save();return jackpotItems()}
 var n=s.n();
 if(s.id=="silver")P.give({sv:n});
 else if(s.id=="energy")P.give({en:n});
 else if(s.id=="junk")P.give({junk:n});
 else if(s.id=="pistol"){S.fz=(S.fz||0)+n;try{draw()}catch(e){}P.save()}
 else if(s.id=="ring_shard"){var p2=window.PG?PG():null;if(p2){var bid=BS()[Math.floor(Math.random()*3)];p2.ringShards[bid]=(p2.ringShards[bid]||0)+n}P.save()}
 else if(s.id=="taler")P.give({tl:n});
 return [[s.id,n]]}
/* ---- стили ---- */
var st=document.createElement("style");st.textContent=
"#dzW.dzo{padding:0;background:radial-gradient(ellipse at 50% 38%,#4a1030 0,#1a0714 55%,#08030a 100%);-webkit-backdrop-filter:none;backdrop-filter:none;align-items:stretch}"+
".wf{position:relative;width:100%;max-width:480px;margin:0 auto;display:flex;flex-direction:column;align-items:center;height:100%;box-sizing:border-box;padding:calc(env(safe-area-inset-top,0px) + 10px) 12px calc(env(safe-area-inset-bottom,0px) + 14px);overflow:hidden}"+
".wf .wx{position:absolute;right:12px;top:calc(env(safe-area-inset-top,0px) + 10px);width:42px;height:42px;border-radius:50%;border:1.5px solid rgba(255,214,120,.6);background:rgba(0,0,0,.45);color:#ffd678;font-size:20px;z-index:5}"+
".wf .wbal{align-self:flex-start;display:flex;align-items:center;gap:6px;height:42px;padding:0 14px;border-radius:21px;border:1.5px solid rgba(255,214,120,.55);background:rgba(0,0,0,.45);color:#ffe9a8;font:700 18px Cambria,Georgia,serif}"+
".wf .wbal .ic,.wf .wbtn .ic{width:1.2em;height:1.2em}"+
".wf .wjp{margin-top:10px;width:100%;display:flex;align-items:center;justify-content:center;gap:10px;padding:8px 10px;border-radius:14px;border:1.5px solid #ffcf4d;background:linear-gradient(180deg,rgba(255,200,60,.26),rgba(120,40,10,.35));animation:wjg 1.6s ease-in-out infinite;box-sizing:border-box}"+
".wf .wjp .big{width:46px;height:46px}.wf .wjp .it{display:flex;align-items:center;gap:2px;color:#fff;font:700 13px Cambria,serif}.wf .wjp .it .ic{width:22px;height:22px}"+
"@keyframes wjg{50%{box-shadow:0 0 22px 3px rgba(255,200,60,.55)}}"+
"html.gfx-low .wf .wjp,html.gfx-mid .wf .wjp{animation:none}"+
".wf .wst{flex:1;min-height:0;width:100%;display:flex;align-items:center;justify-content:center}"+
".wf .wrap{--ws:min(92vw,52vh,440px);position:relative;width:var(--ws);aspect-ratio:1}"+
".wf .wrim{position:absolute;inset:-3%;border-radius:50%;background:conic-gradient(#ffe08a,#b8821e,#ffe08a,#b8821e,#ffe08a,#b8821e,#ffe08a,#b8821e,#ffe08a);box-shadow:0 0 34px rgba(255,190,60,.45),inset 0 0 0 3px #3a1a06}"+
".wf .wdots{position:absolute;inset:-1.4%;border-radius:50%;background:radial-gradient(circle,#fff6c8 0 1.6px,transparent 2.4px) 0 0/0 0}"+
".wf .wh{position:absolute;inset:0;border-radius:50%;overflow:hidden;box-shadow:inset 0 0 0 4px #3a1a06}"+
".wf .wl{position:absolute;left:50%;top:50%;width:0;height:0}"+
".wf .wl>div{position:absolute;left:-26px;top:calc(var(--ws)*-.44);width:52px;display:flex;flex-direction:column;align-items:center;gap:0;color:#fff;font:700 15px Cambria,serif;text-shadow:0 1px 3px #000;transform:rotate(0)}"+
".wf .wl .ic{width:40px;height:40px;filter:drop-shadow(0 2px 3px rgba(0,0,0,.6))}"+
".wf .wp{position:absolute;left:50%;top:-6.5%;width:0;height:0;border-left:15px solid transparent;border-right:15px solid transparent;border-top:34px solid #ff3b3b;transform:translateX(-50%);z-index:3;filter:drop-shadow(0 3px 4px #000)}"+
".wf .wp.tk{animation:wtk .12s}@keyframes wtk{50%{transform:translateX(-50%) rotate(-14deg)}}"+
".wf .wc{position:absolute;left:50%;top:50%;width:19%;height:19%;transform:translate(-50%,-50%);border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffe9a8,#b8821e 70%);border:3px solid #3a1a06;z-index:2;display:flex;align-items:center;justify-content:center}"+
".wf .wc .ic{width:62%;height:62%}"+
".wf .wbtn{width:100%;max-width:380px;height:62px;border-radius:31px;border:2px solid #ffe08a;background:linear-gradient(180deg,#e0302b,#8f1511);color:#fff;font:800 22px Cambria,Georgia,serif;display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 0 22px rgba(255,70,50,.5);animation:wbp 1.4s ease-in-out infinite}"+
"@keyframes wbp{50%{transform:scale(1.03)}}html.gfx-low .wf .wbtn,html.gfx-mid .wf .wbtn{animation:none}"+
".wf .wbtn.off{opacity:.45;animation:none;filter:grayscale(.6)}"+
".wf .wr{height:54px;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;color:#fff;font:800 24px Cambria,serif;text-shadow:0 2px 6px #000}"+
".wf .wr .ic{width:40px;height:40px}.wf .wr.pop{animation:wpop .5s cubic-bezier(.2,1.6,.4,1)}@keyframes wpop{0%{transform:scale(.3);opacity:0}100%{transform:scale(1);opacity:1}}"+
"#wjk{position:absolute;inset:0;z-index:9;display:none;flex-direction:column;align-items:center;justify-content:center;gap:12px;background:radial-gradient(circle,rgba(255,190,60,.95) 0,rgba(120,30,10,.96) 60%,#1a0508 100%);padding:20px;box-sizing:border-box}"+
"#wjk.on{display:flex;animation:wfl .7s}@keyframes wfl{0%{filter:brightness(4)}100%{filter:none}}"+
"#wjk h2{margin:0;color:#fff;font:900 34px Cambria,serif;text-shadow:0 0 18px #ffcf4d,0 3px 6px #000;letter-spacing:3px}"+
"#wjk .gr{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;width:100%;max-width:380px}"+
"#wjk .gr div{display:flex;flex-direction:column;align-items:center;padding:8px 4px;border-radius:12px;background:rgba(0,0,0,.35);border:1px solid rgba(255,214,120,.5);color:#fff;font:800 17px Cambria,serif}"+
"#wjk .gr .ic{width:42px;height:42px}#wjk .gr div.c{grid-column:1/-1}#wjk .gr div.c .ic{width:70px;height:70px}"+
"#wjk button{margin-top:6px;height:52px;padding:0 34px;border-radius:26px;border:2px solid #ffe08a;background:linear-gradient(180deg,#e0302b,#8f1511);color:#fff;font:800 20px Cambria,serif}";
document.head.appendChild(st);
/* ---- экран ---- */
var ov,rot=0,spinning=0,lastHTML="&nbsp;",tick=0;
function chips(arr){return arr.map(function(a){return '<span style="display:inline-flex;align-items:center;gap:4px">'+icon(a[0])+(a[1]?'<span>'+(a[1]>=1e4?Math.round(a[1]/1e3)+"к":fs(a[1]))+'</span>':'')+'</span>'}).join("")}
function wheelHTML(){var seg=[],lab="",A=360/SEC.length;
 SEC.forEach(function(s,i){seg.push(s.c+" "+(i*A)+"deg "+((i+1)*A)+"deg");
  var n=s.n(),t=n?(n>=1e4?Math.round(n/1e3)+"к":fs(n)):"";
  lab+='<div class="wl" style="transform:rotate('+(i*A+A/2)+'deg)"><div>'+icon(s.id)+(t?'<span>'+t+'</span>':'')+'</div></div>'});
 return '<div class="wrim"></div><div class="wh" id="dzWh" style="background:conic-gradient('+seg.join(",")+');transform:rotate('+rot+'deg)">'+lab+'</div><div class="wp" id="dzWp"></div><div class="wc">'+icon("taler")+'</div>'}
function render(){if(!ov)return;var c=cost(),can=(S.tl||0)>=c;
 var h='<div class="wf"><button class="wx" data-z="x" aria-label="Закрити">✕</button>';
 h+='<div class="wbal">'+icon("taler")+'<span id="wBal">'+fs(S.tl||0)+'</span></div>';
 h+='<div class="wjp">'+icon("chest").replace('class="ic','class="ic big')+jackpotItems().slice(1,6).map(function(a){return '<span class="it">'+icon(a[0])+(a[1]>=1e4?Math.round(a[1]/1e3)+"к":a[1])+'</span>'}).join("")+'</div>';
 h+='<div class="wst"><div class="wrap">'+wheelHTML()+'</div></div>';
 h+='<div class="wr" id="dzWr">'+lastHTML+'</div>';
 h+='<button class="wbtn'+(spinning||!can?' off':'')+'" data-z="spin">'+(can?'Крутити · '+c+' '+icon("taler"):'Бракує талерів · '+c+' '+icon("taler"))+'</button>';
 h+='<div id="wjk"></div></div>';
 ov.innerHTML=h}
function jackpotShow(items){var j=ov.querySelector("#wjk");if(!j)return;
 var h='<h2>ДЖЕКПОТ!</h2><div class="gr">';
 items.forEach(function(a,k){h+='<div'+(k==0?' class="c"':'')+'>'+icon(a[0])+(a[1]>1?'<span>'+(a[1]>=1e4?Math.round(a[1]/1e3)+"к":fs(a[1]))+'</span>':'')+'</div>'});
 h+='</div><button data-z="jk">Забрати</button>';j.innerHTML=h;j.classList.add("on");
 try{window.SFX&&SFX.play("fanfare")}catch(e){}try{Telegram.WebApp.HapticFeedback.notificationOccurred("success")}catch(e){}}
function spin(){if(spinning)return;var c=cost();
 if((S.tl||0)<c){P.say("Бракує талерів: треба "+c+" 💰.");try{window.SFX&&SFX.play("err")}catch(e){}return}
 S.tl-=c;try{draw()}catch(e){}
 var i=window._whForce!=null?window._whForce:pick(Math.random()),items=award(i);var w=W();w.tot++;w.my.push({t:Date.now(),i:i});if(w.my.length>10)w.my=w.my.slice(-10);P.cnt("whl");P.save();
 spinning=1;var A=360/SEC.length,tgt=360-(i*A+A/2)+(Math.random()*A*.6-A*.3),cur=((rot%360)+360)%360,add=360*(6+Math.floor(Math.random()*3))+((tgt-cur+720)%360);rot+=add;
 var el=document.getElementById("dzWh"),bal=document.getElementById("wBal");if(bal)bal.textContent=fs(S.tl||0);
 var btn=ov.querySelector('[data-z="spin"]');if(btn)btn.classList.add("off");
 var r=document.getElementById("dzWr");if(r){r.className="wr";r.innerHTML="&nbsp;"}
 var dur=4.4,low=document.documentElement.classList.contains("gfx-low");
 if(el){el.style.transition="transform "+dur+"s cubic-bezier(.08,.6,.05,1)";void el.offsetWidth;el.style.transform="rotate("+rot+"deg)"}
 /* щелчки указателя по мере замедления */
 var t0=Date.now(),lastSeg=-1,pt=document.getElementById("dzWp"),iv=setInterval(function(){
  if(!el){clearInterval(iv);return}var m=new DOMMatrix(getComputedStyle(el).transform),ang=((Math.atan2(m.b,m.a)*180/Math.PI)+360)%360,seg=Math.floor(ang/A);
  if(seg!==lastSeg){lastSeg=seg;if(pt&&!low){pt.classList.remove("tk");void pt.offsetWidth;pt.classList.add("tk")}try{window.SFX&&SFX.play("tap")}catch(e){}try{Telegram.WebApp.HapticFeedback.impactOccurred("light")}catch(e){}}
  if(Date.now()-t0>dur*1000+200)clearInterval(iv)},60);
 setTimeout(function(){spinning=0;clearInterval(iv);lastHTML=chips(items.length>1?[items[0]]:items);
  if(!ov.classList.contains("on"))return;render();
  var rr=document.getElementById("dzWr");if(rr&&!(SEC[i].jp))rr.className="wr pop";
  if(SEC[i].jp)jackpotShow(items);else{try{window.SFX&&SFX.play(i>=5?"fanfare":"ok")}catch(e){}}
 },dur*1000+250)}
function open(){lastHTML="&nbsp;";render();ov.classList.add("on")}
function act(k){if(k=="spin")spin();else if(k=="jk"){var j=ov.querySelector("#wjk");if(j)j.classList.remove("on");lastHTML=chips([["chest",1]]);render()}}
function boot(){ov=P.ov("dzW",act);ov._onclose=function(){};
 window.D9W={open:open,ready:ready,spin:spin,state:W,cost:cost,SEC:SEC,pick:pick,award:award,busy:function(){return spinning}}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
