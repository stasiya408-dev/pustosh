(function(){
var busy=0,el=null;
var TXT={fire:"Розпалюєш вогнище…",watch:"Виставляєш дозор…",eat:"Готуєш їжу…",horse:"Дбаєш про коня…",sleep:"Спиш… 😴"};
function vis(){var h=document.getElementById("hike");return !!(h&&h.getClientRects().length&&getComputedStyle(h).visibility!="hidden")}
function mk(){
  if(!document.getElementById("cpcss")){var s=document.createElement("style");s.id="cpcss";
  s.textContent="#cpw{position:fixed;left:0;right:0;top:0;bottom:0;z-index:99993;display:flex;align-items:center;justify-content:center;background:rgba(6,4,2,.55);opacity:0;pointer-events:none;transition:opacity .25s}#cpw.on{opacity:1;pointer-events:auto}#cpw.sl{background:rgba(2,2,10,.86);transition:opacity 1s}#cpw .cpb{width:min(300px,80vw);text-align:center;color:#f2dfae;font:700 17px/1.3 system-ui,sans-serif;text-shadow:0 2px 6px #000}#cpw .cpt{margin-bottom:12px}#cpw .cpp{height:12px;border-radius:7px;background:rgba(0,0,0,.55);border:1px solid rgba(240,200,110,.5);overflow:hidden}#cpw .cpp i{display:block;height:100%;width:0;background:linear-gradient(90deg,#c8821c,#f5cf6a)}";
  document.head.appendChild(s)}
  el=document.createElement("div");el.id="cpw";el.innerHTML='<div class="cpb"><div class="cpt"></div><div class="cpp"><i></i></div></div>';document.body.appendChild(el);
}
function run(k,ms,fn){
  busy=1;if(!el||!el.isConnected)mk();
  el.className=k=="sleep"?"sl":"";el.querySelector(".cpt").textContent=TXT[k];
  var bar=el.querySelector("i");bar.style.transition="none";bar.style.width="0";
  void el.offsetWidth;el.classList.add("on");bar.style.transition="width "+ms+"ms linear";bar.style.width="100%";
  setTimeout(function(){el.classList.remove("on");busy=0;try{fn()}catch(e){console.error(e)}},ms);
}
function wrap(){
  var a=window.hCampAct,s=window.hSleep;
  if(typeof a!="function"||typeof s!="function"||a._cp)return setTimeout(wrap,400);
  window.hCampAct=function(k){
    if(!vis())return a.apply(this,arguments);
    if(busy)return;var c=window.HK&&HK.cp;if(!c)return;
    if(k=="eat"&&c.eat||k=="horse"&&c.horse)return;
    if(k=="eat"&&HK.food<1)return a.call(this,k);
    run(k,3000,function(){a.call(window,k)});
  };window.hCampAct._cp=1;
  window.hSleep=function(){
    if(!vis())return s.apply(this,arguments);
    if(busy)return;if(!(window.HK&&HK.cp))return;
    run("sleep",5000,function(){s.call(window)});
  };
}
wrap();

/* ---- раптове напад: з події одразу в бій ---- */
function surprise(txt){
  if(!document.getElementById("hsxcss")){var st=document.createElement("style");st.id="hsxcss";
  st.textContent="#hsx{position:fixed;left:0;right:0;top:0;bottom:0;z-index:99992;pointer-events:none;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:18%;background:radial-gradient(ellipse at center,rgba(180,0,0,0) 35%,rgba(190,10,10,.6) 100%);animation:hsxa 1.6s ease-out forwards}#hsx b{font:900 26px/1.1 system-ui,sans-serif;color:#ffe9b0;text-shadow:0 0 12px #e00,0 3px 6px #000;letter-spacing:1px;animation:hsxb .5s ease-out}#hsx span{margin-top:8px;max-width:80vw;text-align:center;font:700 14px/1.3 system-ui,sans-serif;color:#fff;text-shadow:0 2px 5px #000}@keyframes hsxa{0%{opacity:1;background-color:rgba(255,255,255,.55)}12%{background-color:rgba(255,255,255,0)}70%{opacity:1}100%{opacity:0}}@keyframes hsxb{0%{transform:scale(2.2)}100%{transform:scale(1)}}@keyframes hsxs{0%,100%{transform:none}20%{transform:translate(-6px,3px)}40%{transform:translate(5px,-4px)}60%{transform:translate(-4px,-2px)}80%{transform:translate(3px,3px)}}#hike.hsk{animation:hsxs .4s}";
  document.head.appendChild(st)}
  var o=document.getElementById("hsx");if(o)o.remove();
  o=document.createElement("div");o.id="hsx";o.innerHTML="<b>⚠ НАПАД!</b><span></span>";o.querySelector("span").textContent=txt||"";document.body.appendChild(o);
  var h=document.getElementById("hike");if(h){h.classList.remove("hsk");void h.offsetWidth;h.classList.add("hsk")}
  try{navigator.vibrate&&navigator.vibrate(60)}catch(e){}
  setTimeout(function(){if(o.isConnected)o.remove()},1700);
}
function wrap2(){
  var c=window.hChoice;
  if(typeof c!="function"||c._sp)return setTimeout(wrap2,400);
  window.hChoice=function(){
    var r=c.apply(this,arguments),H=window.HK;
    if(H&&H.ph=="out"&&H.out&&H.out.fight&&vis()){
      var t=H.out.t;
      try{hNext()}catch(e){console.error(e)}
      surprise(t);
    }
    return r;
  };window.hChoice._sp=1;
}
wrap2();
window.D9CP={busy:function(){return busy}};
})();
