(function(){
if(window.D9DU)return;
var C="#f3e6c4";
function svg(k,sz,col){col=col||C;var p={
left:'<path d="M40 8 12 32l28 24v-15h18V23H40z" fill="'+col+'"/>',
right:'<path d="M24 8l28 24-28 24V41H6V23h18z" fill="'+col+'"/>',
block:'<path d="M32 5 10 13v17c0 14 9 24 22 29 13-5 22-15 22-29V13z" fill="'+col+'" stroke="#2a1608" stroke-width="3"/><path d="M32 12v40c-9-4-15-12-15-22V18z" fill="rgba(0,0,0,.25)"/>',
atk:'<path d="M50 6 56 12 26 42l-6-6zM18 38l8 8-6 4-6 6-6-6 6-6zM10 54l6-6 4 4-6 6z" fill="'+col+'" stroke="#2a1608" stroke-width="2"/>'}[k];
return '<svg viewBox="0 0 64 64" width="'+sz+'" height="'+sz+'" style="display:block">'+p+'</svg>'}
var st=document.createElement("style");st.id="dducss";
st.textContent='.hdw .hdbt{gap:8px}.hdw .hdbt button{height:clamp(120px,21vh,190px);font-size:15px;padding:6px 2px;justify-content:center;gap:6px;border-radius:14px;border-width:2px}.hdw .hdbt button small{font-size:13px;opacity:1}.hdw .hda{min-height:110px}.hdw .hdr{width:150px;height:150px;margin:-75px 0 0 -75px;background:rgba(10,5,2,.55)}.hdw .hdr.on{display:flex}.hdw .hda:has(.hdr.on) .hdem{opacity:.22}.hdw .hdbt button.atk svg path{fill:#fff}';
document.head.appendChild(st);
var side="left";
function fix(){try{fix0()}catch(e){}}
function fix0(){var h=document.getElementById("hc");if(!h)return;
var b=h.querySelectorAll(".hdbt button");
if(b.length==4&&!b[0].getAttribute("data-d9")){var k=["left","block","right","atk"],t=["ухил","блок","ухил","удар"];
for(var i=0;i<4;i++){b[i].innerHTML=svg(k[i],64)+"<small>"+t[i]+"</small>";b[i].setAttribute("data-d9","1")}}
var r=document.getElementById("hdr");
if(r&&r.classList.contains("on")){var kind=r.classList.contains("sw")?"sw":"hi";var key=kind+(kind=="sw"?side:"");
if(r.getAttribute("data-k")!=key){r.setAttribute("data-k",key);r.innerHTML=svg(kind=="hi"?"block":side,92,kind=="hi"?"#ffd9a0":"#ffe27a")}}
else if(r&&r.innerHTML&&!r.classList.contains("on")){r.innerHTML="";r.removeAttribute("data-k");side=Math.random()<.5?"left":"right"}}
var mo=new MutationObserver(function(){fix();mo.takeRecords()});
function go(){var h=document.getElementById("hc");if(!h){setTimeout(go,500);return}mo.observe(h,{childList:true,subtree:true,attributes:true,attributeFilter:["class"]});fix()}
go();setInterval(fix,300);
window.D9DU={fix:fix};
})();
