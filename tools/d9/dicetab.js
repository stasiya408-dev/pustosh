(function(){
if(window.D9DT)return;
function pip(n,x,y,s){var P={1:[[.5,.5]],2:[[.28,.28],[.72,.72]],3:[[.26,.26],[.5,.5],[.74,.74]],4:[[.28,.28],[.72,.28],[.28,.72],[.72,.72]],5:[[.26,.26],[.74,.26],[.5,.5],[.26,.74],[.74,.74]],6:[[.3,.25],[.7,.25],[.3,.5],[.7,.5],[.3,.75],[.7,.75]]}[n],h="";
P.forEach(function(p){h+='<circle cx="'+(x+p[0]*s).toFixed(1)+'" cy="'+(y+p[1]*s).toFixed(1)+'" r="'+(s*.09).toFixed(1)+'" fill="#2a1608"/>'});return h}
function dice(a,b){var s=26,g=6,h='<svg viewBox="0 0 '+(s*2+g)+' '+s+'" width="'+(s*2+g)*.9+'" height="'+s*.9+'" style="display:block">';
[[a,0],[b,s+g]].forEach(function(d){h+='<rect x="'+(d[1]+.8)+'" y=".8" width="'+(s-1.6)+'" height="'+(s-1.6)+'" rx="5" fill="#f3e6c4" stroke="#7a4a1c" stroke-width="1.6"/>'+pip(d[0],d[1],0,s)});return h+'</svg>'}
var CB=[
 {id:"six",n:"Дві шістки",a:6,b:6,p:25,m:function(a,b){return a==6&&b==6}},
 {id:"dbl",n:"Дубль",a:4,b:4,p:10,m:function(a,b){return a==b&&a!=6}},
 {id:"hi",n:"Старші кості",a:6,b:5,p:5,m:function(a,b){return a!=b&&a+b>=10}},
 {id:"sev",n:"Сімка",a:4,b:3,p:3,m:function(a,b){return a+b==7}}];
var st=document.createElement("style");st.id="d9dtcss";
st.textContent='#dc383{position:absolute;left:6px;right:6px;top:4px;z-index:6;pointer-events:none;display:flex;flex-direction:column;gap:3px}'
+'#dc383 .dch{display:flex;justify-content:space-between;align-items:center;font:700 10px Georgia,serif;letter-spacing:1.5px;color:#f6d27a;text-transform:uppercase;text-shadow:0 1px 3px #000;padding:0 4px}'
+'#dc383 .dch b{font-size:11px;color:#ffe9a8;letter-spacing:.5px;text-transform:none}'
+'#dc383 .dcr{display:grid;grid-template-columns:repeat(4,1fr);gap:4px}'
+'#dc383 .dcc{display:flex;flex-direction:column;align-items:center;gap:2px;padding:4px 2px 3px;border-radius:10px;background:rgba(24,12,5,.74);border:1px solid rgba(200,148,60,.45);transition:all .25s;opacity:.88}'
+'#dc383 .dcc small{font:600 9.5px Georgia,serif;color:#e8d3a4;line-height:1.1;text-align:center}'
+'#dc383 .dcc u{text-decoration:none;font:800 12px Georgia,serif;color:#f6d27a}'
+'#dc383 .dcc.on{opacity:1;background:linear-gradient(#7a4a12,#3d2108);border:1.5px solid #ffd870;box-shadow:0 0 14px rgba(255,200,80,.85),inset 0 0 8px rgba(255,210,120,.35);transform:scale(1.07);animation:dc383p 1s ease-in-out infinite}'
+'#dc383 .dcc.on small{color:#fff3cf}#dc383 .dcc.on u{color:#fff;font-size:13px}'
+'@keyframes dc383p{50%{box-shadow:0 0 22px rgba(255,220,110,1),inset 0 0 10px rgba(255,210,120,.5)}}'
+'html.gfx-low #dc383 .dcc.on{animation:none}';
document.head.appendChild(st);
var el=null,key="";
function build(){var dg=document.querySelector("#dice .dg");if(!dg)return null;
if(getComputedStyle(dg).position=="static")dg.style.position="relative";
if(!el||el.parentNode!==dg){el=document.createElement("div");el.id="dc383";
var h='<div class="dch"><span>Комбінації</span><b id="dc383t"></b></div><div class="dcr">';
CB.forEach(function(c){h+='<div class="dcc" data-c="'+c.id+'">'+dice(c.a,c.b)+'<small>'+c.n+'</small><u>+'+c.p+'</u></div>'});
el.innerHTML=h+'</div>';dg.appendChild(el);key=""}return el}
function tick(){try{var d=document.getElementById("dice");if(!d||d.style.display!="flex")return;var e=build();if(!e)return;
var a=0,b=0,tot=0,hold=false,kb=document.getElementById("keb"),r=document.getElementById("dr"),mt=r&&/Випало (\d) и (\d).*?(\d+) очок/.exec(r.textContent||"");
if(mt&&kb&&kb.style.display!="none"&&kb.offsetParent){hold=true;a=+mt[1];b=+mt[2];tot=+mt[3]}
var f=hold?CB.filter(function(c){return c.m(a,b)})[0]:null;var k=hold?(f?f.id:"none")+a+b+tot:"";
if(k===key)return;key=k;
[].forEach.call(e.querySelectorAll(".dcc"),function(c){c.classList.toggle("on",!!(f&&f.id==c.getAttribute("data-c")))});
var t=document.getElementById("dc383t");
if(hold){var bn=(a==6&&b==6)?25:a==b?10:(a+b==7)?3:(a+b>=10)?5:0;
t.textContent=a+" + "+b+(bn?" + бонус "+bn:"")+" = "+tot+" очок"}else t.textContent=""}catch(x){}}
setInterval(tick,200);
window.D9DT={tick:tick};
})();
