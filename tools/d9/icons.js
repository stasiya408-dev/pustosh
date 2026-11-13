/* d9ic v372: НИ ОДНОГО эмодзи в тексте. Все эмодзи в любом месте страницы заменяются на картинки:
   атлас игры (ICO) или свои линейные SVG-иконки в золотом стиле; неизвестные удаляются. */
(function(){
var G="#f0cf75";
/* SVG-иконки: имя -> [разметка внутри 24x24, цвет, заливка] */
var SV={
check:['<path d="M5 12.5l4.5 4.5L19 7"/>',"#7fd18a"],
cross:['<path d="M6 6l12 12M18 6L6 18"/>',"#e8806e"],
heart:['<path d="M12 20s-7.5-4.6-7.5-10.2A4.2 4.2 0 0 1 12 7.6a4.2 4.2 0 0 1 7.5 2.2C19.5 15.4 12 20 12 20z"/>',"#e8584a","#e8584a55"],
star:['<path d="M12 3l2.7 5.9 6.3.7-4.7 4.3 1.3 6.3L12 17l-5.6 3.2 1.3-6.3L3 9.6l6.3-.7z"/>',G,"#f0cf7555"],
spark:['<path d="M12 3l2 7 7 2-7 2-2 7-2-7-7-2 7-2z"/>',G,"#f0cf7555"],
flame:['<path d="M12 3c.8 4 5 6 5 11a5 5 0 0 1-10 0c0-2 1-3.2 2.2-4.2 0 2 .8 3 2 3C10.5 9 11 6 12 3z"/>',"#f2a444","#f2a44444"],
power:['<path d="M3 9.5v5M6 7v10M18 7v10M21 9.5v5M6 12h12"/>',G],
lock:['<rect x="6" y="11" width="12" height="9" rx="2"/><path d="M8.5 11V8a3.5 3.5 0 0 1 7 0v3"/>',G],
unlock:['<rect x="6" y="11" width="12" height="9" rx="2"/><path d="M8.5 11V8a3.5 3.5 0 0 1 6.8-1.2"/>',"#7fd18a"],
bow:['<path d="M5 3c9 2 15 8 16 16M5 3L21 19M4 20l6-6M4 20l1.5-4.5M4 20l4.5-1.5"/>',G],
run:['<circle cx="14.5" cy="5" r="2"/><path d="M6 20l4.5-5 3 2 2-6-4-2-3.5 3M12.5 11l5 1 2 3"/>',G],
burst:['<path d="M12 2l2 6 6-2-3.5 5 5.5 2-6 1.5 1.5 6.5-5.5-4L6.5 21 8 14.5 2 13l5.5-2L4 6l6 2z"/>',"#f2a444","#f2a44444"],
drop:['<path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11z"/>',"#6ab8f0","#6ab8f044"],
wheat:['<path d="M12 21V8M12 8c-3 0-3-3-3-5 3 0 3 3 3 5zM12 8c3 0 3-3 3-5-3 0-3 3-3 5zM12 14c-3 0-4-2-4-4 3 0 4 2 4 4zM12 14c3 0 4-2 4-4-3 0-4 2-4 4z"/>',"#e0c068"],
skull:['<path d="M12 3a7 7 0 0 0-7 7c0 2.5 1.2 4 3 5v3h8v-3c1.8-1 3-2.5 3-5a7 7 0 0 0-7-7z"/><circle cx="9" cy="10.5" r="1.3"/><circle cx="15" cy="10.5" r="1.3"/><path d="M10.5 18v-2M13.5 18v-2"/>',G],
castle:['<path d="M4 20V9h3v2h2V9h6v2h2V9h3v11zM10 20v-4h4v4"/>',G],
link:['<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3A4 4 0 0 0 11 18.7l1-1"/>',G],
people:['<circle cx="9" cy="8" r="3"/><path d="M3 20c0-4 3-6 6-6s6 2 6 6M16 5.5a3 3 0 0 1 0 5.5M17 14.2c2.5.6 4 2.5 4 5.8"/>',G],
person:['<circle cx="12" cy="8" r="4"/><path d="M4 21c0-5 4-7 8-7s8 2 8 7"/>',G],
paw:['<circle cx="6.5" cy="10" r="1.8"/><circle cx="10" cy="6" r="1.8"/><circle cx="14" cy="6" r="1.8"/><circle cx="17.5" cy="10" r="1.8"/><path d="M12 12c-3 0-5 3-5 5.5 0 1.6 1.5 2 3 1.5 1.2-.4 1.8-.4 4 0 1.5.3 3-.1 3-1.5C17 15 15 12 12 12z"/>',G],
cat:['<path d="M5 4l4 3h6l4-3v9a7 7 0 0 1-14 0z"/><path d="M9.5 12v.5M14.5 12v.5M10.5 16c.9.6 2.1.6 3 0"/>',G],
demon:['<path d="M5 3l3 5M19 3l-3 5"/><path d="M7 8h10a3 3 0 0 1 3 3v2a8 8 0 0 1-16 0v-2a3 3 0 0 1 3-3z"/><path d="M9 12.5v.5M15 12.5v.5M9.5 17h5"/>',G],
eye:['<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',G],
sound:['<path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/>',G],
mute:['<path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16.5 9.5l5 5M21.5 9.5l-5 5"/>',"#e8806e"],
gear:['<circle cx="12" cy="12" r="3.4"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M18.7 5.3l-2.1 2.1M7.4 16.6l-2.1 2.1"/>',G],
hammer:['<path d="M4 20l9-9M11 5l4-2 6 6-2 4-3-1-2 2-4-4 2-2z"/>',G],
bell:['<path d="M6 16v-5a6 6 0 0 1 12 0v5l2 2H4zM10 20.5a2 2 0 0 0 4 0"/>',G],
chart:['<path d="M5 20V10M12 20V4M19 20v-7"/>',G],
wheel:['<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="2"/><path d="M12 3.5v17M3.5 12h17M6 6l12 12M18 6L6 18"/>',G],
temple:['<path d="M3 10l9-6 9 6zM5 10v9M9.5 10v9M14.5 10v9M19 10v9M3 19.5h18"/>',G],
house:['<path d="M4 11l8-7 8 7M6 10v10h12V10M10 20v-5h4v5"/>',G],
flag:['<path d="M6 21V4M6 5h12l-2.5 4L18 13H6"/>',G],
crown:['<path d="M3 8l4 4 5-7 5 7 4-4-2 11H5z"/>',G,"#f0cf7555"],
medal:['<circle cx="12" cy="15" r="5"/><path d="M8 3l4 6 4-6M12 12.5v5"/>',G],
refresh:['<path d="M20 11a8 8 0 0 0-14-4L4 9M4 4v5h5M4 13a8 8 0 0 0 14 4l2-2M20 20v-5h-5"/>',G],
warn:['<path d="M12 3l10 18H2zM12 10v5M12 18v.4"/>',"#f2a444"],
bulb:['<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 11c.7.6 1 1.3 1 2h5c0-.7.3-1.4 1-2A6 6 0 0 0 12 3z"/>',G],
book:['<path d="M4 5h6a2 2 0 0 1 2 2v12a2 2 0 0 0-2-2H4zM20 5h-6a2 2 0 0 0-2 2v12a2 2 0 0 1 2-2h6z"/>',G],
save:['<path d="M5 4h11l3 3v13H5zM8 4v5h7V4M8 20v-6h8v6"/>',G],
note:['<path d="M9 18V6l10-2v12M9 18a2.5 2.5 0 1 1-2.5-2.5M19 16a2.5 2.5 0 1 1-2.5-2.5"/>',G],
palette:['<path d="M12 3a9 9 0 1 0 0 18c1.5 0 2-1 1.5-2.2S13.5 17 15 17h2a4 4 0 0 0 4-4c0-5-4-10-9-10z"/><circle cx="8" cy="11" r="1"/><circle cx="12" cy="7.5" r="1"/><circle cx="16" cy="10" r="1"/>',G],
moon:['<path d="M20 14A8 8 0 1 1 10 4a6.5 6.5 0 0 0 10 10z"/>',G],
sun:['<circle cx="12" cy="12" r="4"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2 2M16.7 16.7l2 2M18.7 5.3l-2 2M7.3 16.7l-2 2"/>',G],
cloud:['<path d="M7 18a4 4 0 0 1 0-8 5 5 0 0 1 9.5-1A4 4 0 0 1 17 18z"/>',G],
snow:['<path d="M12 2v20M3.3 7l17.4 10M3.3 17L20.7 7"/>',"#8fd0f0"],
leaf:['<path d="M5 19c0-9 5-14 15-14 0 10-5 15-14 15zM5 19l8-8"/>',"#8cc86a"],
wave:['<path d="M3 9c3-3 6 3 9 0s6 3 9 0M3 15c3-3 6 3 9 0s6 3 9 0"/>',"#6ab8f0"],
hole:['<ellipse cx="12" cy="13" rx="8" ry="4"/><path d="M5 13v3c0 2 3.5 3.5 7 3.5s7-1.5 7-3.5v-3"/>',G],
fist:['<path d="M7 11V8a1.5 1.5 0 0 1 3 0v-1a1.5 1.5 0 0 1 3 0v1a1.5 1.5 0 0 1 3 0v2a1.5 1.5 0 0 1 3 0v4a6 6 0 0 1-6 6h-2a6 6 0 0 1-6-6z"/>',G],
shield:['<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',G],
target:['<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.3"/>',G],
cart:['<path d="M3 6h12v9H3zM15 9.5h3.5L21 13v2h-6"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',G],
door:['<path d="M6 21V4h12v17M3 21h18M14 12v.5"/>',G],
bed:['<path d="M3 18V7M3 15h18v3M21 15v-3a3 3 0 0 0-3-3h-8v6"/>',G],
pin:['<path d="M12 21s7-6 7-12a7 7 0 0 0-14 0c0 6 7 12 7 12z"/><circle cx="12" cy="9" r="2"/>',G],
scale:['<path d="M12 4v16M5 8h14M5 8l-3 7a3 3 0 0 0 6 0zM19 8l-3 7a3 3 0 0 0 6 0zM8 20h8"/>',G],
wind:['<path d="M3 9h11a3 3 0 1 0-3-3M3 14h15a3 3 0 1 1-3 3M3 19h7"/>',G],
swirl:['<path d="M12 12a2 2 0 1 1 2 2 4 4 0 1 1-4-4 6 6 0 1 1 6 6"/>',G],
bot:['<path d="M7 8h10v9H7zM12 8V4M9.5 12v.5M14.5 12v.5M5 12v3M19 12v3"/>',G],
play:['<path d="M7 4l13 8-13 8z"/>',G,"#f0cf7555"],
gem2:['<path d="M12 3l7 8-7 10-7-10z"/>',G,"#f0cf7555"],
dotG:['<circle cx="12" cy="12" r="6"/>',"#5ccf7a","#5ccf7a"],
dotB:['<circle cx="12" cy="12" r="6"/>',"#5a9cf0","#5a9cf0"],
dotP:['<circle cx="12" cy="12" r="6"/>',"#a878e8","#a878e8"],
dotR:['<circle cx="12" cy="12" r="6"/>',"#e8584a","#e8584a"],
dotN:['<circle cx="12" cy="12" r="5.5"/>',G,"#f0cf7544"],
diamond:['<path d="M12 5l6 7-6 7-6-7z"/>',G,"#f0cf7555"]
};
/* эмодзи -> "@id атласа" | "имя SVG" | "=текст" */
var MAP={};
function m(list,v){list.split(" ").forEach(function(e){if(e)MAP[e]=v})}
m("💰 🪙","@taler");m("🥈","@silver");m("🔑 🗝","@key");m("⚡ 🔋","@energy");m("🏆","@trophy");
m("🐎 🏇 🐴","@horse");m("🎒","@backpack");m("🍖 🍽 🍞 🥖 🌭 🥣 🥚 🧅 🍴","@food");m("🛒","@nav_market");
m("⚔ 🤺","@w_sabre");m("🗡 🔪 🪓","@w_dagger");m("🍺 🍻 🥃 🍷 🍵 🥛 🍯","@beer");m("🧭","@compass");
m("🌿 🍀 🪻 🌻","@herbs");m("🗺 🛤","@map");m("🔫","@pistol");m("🎁 📦 🏺 ⚱","@chest");
m("💎","@gem");m("🔩 🧰","@junk");m("🧩","@ring_shard");m("🔷 💠","@gem_shard");m("💍","@ring");
m("🖼","@boss_background");m("👘","@boss_outfit");m("🧍","@boss_stance");m("🏕 ⛺ 🛖","@tent");
m("🎲","@dice");m("📜","@knowledge_scroll");m("🔍 🔎","@spyglass");m("🧥 👕 👖","@coat");
m("🎩 🪖","@hat");m("👢 🦵","@boots");m("🧣 🧵","@cloth");m("👛","@bag_red");m("🪣","@bucket");
m("🪵","@wood");m("🪶 🦅","@eagle_feather");m("💣","@cannonballs");m("🕯","@candle");m("📣 🎺","@horn");
m("🎗","@banner");m("✝ ⚜ 🔱","@cossack_cross");m("⏳ ⌛","@hourglass");m("🐟 🎣","@fish");
m("🚚","cart");m("🎯","target");m("🛡","shield");m("🏹 ➶","bow");m("🔥 ☄","flame");m("💪 🦾","power");
m("🔒","lock");m("🔓","unlock");m("🏃 🚶","run");m("💥 💢","burst");m("💧 🩸","drop");m("🌾","wheat");
m("💀 ☠ 👻","skull");m("🏰 ♜","castle");m("🔗 ⛓","link");m("👥 👯 🤝","people");
m("👤 🧑 🧙 🧝 💂 🕵 🥋 ♙ 🦹","person");m("🐺 🐕 🐾 🐗 🐽 🐂 🦌 🐇 🦇 🦉 🐓 🐸 🦷 🦴 🐿 🐀","paw");
m("🐈","cat");m("🐉 👹 👿","demon");m("👁 👀","eye");m("🔊 🔈 🔉","sound");m("🔇","mute");
m("⚙","gear");m("🛠 ⚒ 🔨 🔧 ⛏","hammer");m("🔔","bell");m("📊 📈 📉","chart");m("🎡 🎰","wheel");
m("🏟 🏛 🏦 🏪","temple");m("🏠 🏡 🏚 🏯 🗼 ⛩ 🕌","house");m("🏁 🚩 ⚑ 🏴","flag");m("👑","crown");
m("🎖 🏅 🥇 🥉","medal");m("🔁 🔄","refresh");m("⚠ 🚨","warn");m("💡","bulb");m("📖 📘 📋 📅 📓","book");
m("💾","save");m("🎵 🎶 ♬ 🎧 🥁 🪕","note");m("🎨","palette");m("🌙 🌑","moon");m("☀ 🌅","sun");
m("☁ 🌫","cloud");m("❄ 🥶","snow");m("🌲 🌳 🍄 🌰","leaf");m("🌊","wave");m("🕳","hole");
m("👊 🥊 ✊ ✋ 🤚 🖐","fist");m("🚪","door");m("🛏 🛌","bed");m("📍","pin");m("⚖","scale");
m("💨","wind");m("🌀","swirl");m("🤖","bot");m("▶","play");m("⭐ 🌟 ✪ ☆","star");m("✨ ✦ ✹ 🎉","spark");
m("✔ ✅","check");m("✖ ❌","cross");m("❤ ♥ 💔","heart");m("🔘","dotN");m("🟢","dotG");m("🔵","dotB");
m("🟣","dotP");m("🔴","dotR");m("⬆ 👆","=↑");m("⬇ 👇","=↓");m("⬅ 👈","=←");m("➡ 👉","=→");m("↔","=↔");
m("❓ ❔","=?");m("❗ ❕","=!");m("📤","=↑");m("🏴‍☠","skull");
var KEEP_BELOW=0x2190;
function atlas(id){var h=window.ICO&&window.ICO(id);if(!h)return null;var t=document.createElement("template");t.innerHTML=h;return t.content.firstChild}
function svg(name){var d=SV[name];if(!d)return null;var s=document.createElementNS("http://www.w3.org/2000/svg","svg");
  s.setAttribute("viewBox","0 0 24 24");s.setAttribute("class","ig");s.setAttribute("aria-hidden","true");
  s.setAttribute("fill",d[2]||"none");s.setAttribute("stroke",d[1]);s.setAttribute("stroke-width","1.8");
  s.setAttribute("stroke-linecap","round");s.setAttribute("stroke-linejoin","round");s.innerHTML=d[0];return s}
var RX=/(?:\p{Extended_Pictographic}|▶)[️︎\u{1F3FB}-\u{1F3FF}]?(?:‍(?:\p{Extended_Pictographic})️?)*/gu;
var PRE=/[←-⯿\u{1F000}-\u{1FAFF}‍️]/u;
function node(e,solo){
  var base=String.fromCodePoint(e.codePointAt(0)),v=MAP[e.replace(/[️︎]/g,"")]||MAP[base];
  if(base.codePointAt(0)<KEEP_BELOW)return document.createTextNode(e);
  if(v){
    if(v.charAt(0)==="="){return document.createTextNode(v.slice(1))}
    if(v.charAt(0)==="@"){var a=atlas(v.slice(1));if(a)return a}
    else{var s=svg(v);if(s)return s}
  }
  return solo?svg("diamond"):null;
}
function conv(t){
  var s=t.nodeValue;if(!PRE.test(s))return;
  var p=t.parentNode;if(!p)return;
  var tag=p.nodeName;
  if(/^(OPTION|TEXTAREA|TITLE)$/.test(tag)){t.nodeValue=s.replace(RX,"").replace(/️/g,"");return}
  var solo=s.replace(RX,"").trim()==="",frag=document.createDocumentFragment(),last=0,hit=0,r;
  RX.lastIndex=0;
  while((r=RX.exec(s))){
    var n=node(r[0],solo);
    if(r.index>last)frag.appendChild(document.createTextNode(s.slice(last,r.index)));
    if(n)frag.appendChild(n);
    last=r.index+r[0].length;hit=1}
  if(!hit){var c=s.replace(/️/g,"");if(c!==s)t.nodeValue=c;return}
  if(last<s.length)frag.appendChild(document.createTextNode(s.slice(last)));
  p.replaceChild(frag,t)}
var SKIP=/^(SCRIPT|STYLE|NOSCRIPT|INPUT|SELECT|SVG|CANVAS|IFRAME)$/i;
function walk(root){
  if(root.nodeType===3){if(!(root.parentNode&&root.parentNode.closest&&root.parentNode.closest("[data-noic]")))conv(root);return}
  if(root.nodeType!==1||SKIP.test(root.nodeName))return;
  if(root.closest&&root.closest("[data-noic]"))return;
  var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:function(n){var p=n.parentNode;
    return p&&!SKIP.test(p.nodeName)&&PRE.test(n.nodeValue)?1:2}}),a=[],n;
  while((n=w.nextNode()))a.push(n);
  a.forEach(function(t){if(!(t.parentNode&&t.parentNode.closest&&t.parentNode.closest("[data-noic]")))conv(t)})}
var q=[],pend=0;
function flush(){pend=0;var a=q;q=[];a.forEach(function(n){try{if(n.isConnected!==false)walk(n)}catch(e){}})}
function sched(){if(pend)return;pend=1;(window.requestAnimationFrame||setTimeout)(flush)}
function start(){
  if(!document.body)return;
  new MutationObserver(function(ms){
    for(var i=0;i<ms.length;i++){var x=ms[i];
      if(x.type==="characterData"){if(PRE.test(x.target.nodeValue))q.push(x.target)}
      else for(var j=0;j<x.addedNodes.length;j++){var a=x.addedNodes[j];if(a.nodeType===3?PRE.test(a.nodeValue):a.nodeType===1)q.push(a)}}
    if(q.length)sched()}).observe(document.body,{childList:true,subtree:true,characterData:true});
  q.push(document.body);sched();
  /* страховка: полный проход раз в 3 с (на случай атласа, загрузившегося позже) */
  setInterval(function(){q.push(document.body);sched()},3000)}
window.D9I={walk:function(r){walk(r||document.body)},svg:svg,names:Object.keys(SV),map:MAP,rx:RX};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start);else start();
var css=document.createElement("style");
css.textContent=".ig{width:1.1em;height:1.1em;vertical-align:-.2em;display:inline-block;overflow:visible;filter:drop-shadow(0 1px 1px rgba(0,0,0,.55));flex:none}"
 +"img.ic{width:1.15em;height:1.15em;vertical-align:-.22em;display:inline-block}";
document.head.appendChild(css);
})();
