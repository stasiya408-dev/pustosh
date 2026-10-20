/* v174 alpha: single unified account-wide talent tree; all boss weapons benefit. */
(function(){
"use strict";
var N=[
{id:"powder",n:"Порохова сила",ic:"✹",d:"+1% шкоди зброєю за рівень",t:0},
{id:"eagle",n:"Орлине око",ic:"◎",d:"+0,5 в.п. шансу криту",t:0},
{id:"finish",n:"Останній удар",ic:"⚔",d:"+1% при HP боса ≤30%",t:0},
{id:"steady",n:"Тверда рука",ic:"✦",d:"+0,5% шкоди зброєю",t:1},
{id:"marksman",n:"Влучний стрілець",ic:"🎯",d:"+2 в.п. до множника криту",t:1},
{id:"opening",n:"Перший залп",ic:"➶",d:"+1% при HP боса ≥70%",t:1},
{id:"barrage",n:"Пороховий натиск",ic:"✹",d:"+1% п’ятому пострілу",t:2},
{id:"precision",n:"Зіркий сокіл",ic:"◈",d:"+0,5 в.п. криту при HP ≤50%",t:2},
{id:"fury",n:"Без пощади",ic:"⚡",d:"+0,5% при HP боса ≤30%",t:2},
{id:"ataman",n:"Сила одинака",ic:"♜",d:"+1% шкоди у соло",t:3},
{id:"comrade",n:"Побратим",ic:"♙",d:"+1% шкоди у відряді",t:3},
{id:"legend",n:"Легенда степу",ic:"★",d:"+0,5% урону будь-якої зброї",t:3}
];
var TH=[50000,120000,300000,650000,1200000,2000000,3200000,5000000,7000000,10000000,14000000,19000000,25000000,33000000,44000000,58000000,75000000,96000000,122000000,155000000];
var REQ=[0,3,8,14];
function root(){var p=PG();return p.talents||(p.talents={version:1,spent:{}})}
function spent(){var t=root();if(!t.spent||typeof t.spent!=="object")t.spent={};return t.spent}
function damage(){return Math.max(0,Math.floor(Number(PG().bossStats.totalPersonalDamage)||0))}
function lvl(){var d=damage(),n=0;for(var i=0;i<TH.length;i++)if(d>=TH[i])n++;return n}
function r(k){return Math.min(5,Math.max(0,Math.floor(Number(spent()[k])||0)))}
function used(){return N.reduce(function(a,n){return a+r(n.id)},0)}
function free(){return Math.max(0,lvl()-used())}
function inc(k){var n=N.find(function(x){return x.id===k});if(!n||!free()||r(k)>=5||used()<REQ[n.t])return false;spent()[k]=r(k)+1;try{save()}catch(e){}render();return true}
function shot(base,hp,mx,shotNo){
var p=mx>0?hp/mx:1,add=r("powder")*.01+r("steady")*.005+r("legend")*.005;
if(p<=.30)add+=r("finish")*.01+r("fury")*.005;
if(p>=.70)add+=r("opening")*.01;
if(shotNo>0&&shotNo%5===0)add+=r("barrage")*.01;
add+=(S.mode==="grp"?r("comrade"):r("ataman"))*.01;
var chance=Math.min(.125,.05+r("eagle")*.005+(p<=.5?r("precision")*.005:0));
var crit=Math.random()<chance;
return {damage:Math.max(1,Math.round(base*(1+Math.min(add,.25))*(crit?1.5+r("marksman")*.02:1))),critical:crit};
}
function fmt(n){return Math.floor(n).toLocaleString("uk-UA")}
function render(){
var el=document.getElementById("talentModal");if(!el)return;
var l=lvl(),d=damage(),prev=l?TH[l-1]:0,next=TH[l],pct=next===undefined?100:Math.max(0,Math.min(100,(d-prev)/(next-prev)*100));
var h='<div class="tal-shell" role="dialog" aria-modal="true" aria-label="Козацька майстерність"><div class="tal-head"><b>⚔ КОЗАЦЬКА МАЙСТЕРНІСТЬ</b><button type="button" id="talClose">✕</button></div>'
+'<p class="tal-sub">Одне дерево на весь акаунт · бонуси для всіх видів зброї проти босів</p><div class="tal-meta">Рівень <b>'+l+'/20</b> · Вільні очки <b>'+free()+'</b></div>'
+'<div class="tal-bar"><span style="width:'+pct+'%"></span></div><div class="tal-note">Всього особистої шкоди: '+fmt(d)+' · '+(next===undefined?'всі очки зібрані':'до наступного очка: '+fmt(next-d))+'</div><div class="tal-tree">';
N.forEach(function(n,i){
if(i%3===0){if(i)h+='</div>';h+='<div class="tal-tier"><div class="tal-ttl">'+["I · ОСНОВА","II · МАЙСТЕРНІСТЬ","III · ВЕТЕРАН","IV · ОТАМАН"][n.t]+(REQ[n.t]?' · від '+REQ[n.t]+' вкладених очок':'')+'</div><div class="tal-row">'}
var a=r(n.id),locked=used()<REQ[n.t];
h+='<button class="tal-node'+(locked?' locked':'')+'" data-talent="'+n.id+'" '+(locked||a===5||!free()?'disabled':'')+'><span class="tal-icon">'+n.ic+'</span><b>'+n.n+'</b><small>'+n.d+'</small><em>'+a+'/5</em></button>';
});
h+='</div></div></div><p class="tal-note">Бонуси постійні та не залежать від одягу. Урон друзів-ботів не враховується.</p></div>';
el.innerHTML=h;el.querySelector("#talClose").onclick=close;
Array.from(el.querySelectorAll("[data-talent]")).forEach(function(b){b.onclick=function(){inc(b.getAttribute("data-talent"))}});
}
function open(){var e=document.getElementById("talentModal");if(e){render();e.style.display="flex"}}
function close(){var e=document.getElementById("talentModal");if(e)e.style.display="none"}
function install(){
if(document.getElementById("talentModal"))return;
var e=document.createElement("div");e.id="talentModal";e.style.display="none";document.body.appendChild(e);
e.addEventListener("click",function(ev){if(ev.target===e)close()});
var b=document.createElement("button");b.type="button";b.id="talentOpen";b.textContent="⚔ Таланти";b.onclick=open;document.body.appendChild(b);
var my=document.getElementById("nbmy");if(my){my.style.cursor="pointer";my.title="Відкрити дерево талантів";my.addEventListener("click",open)}
}
window.TALENTS={open:open,close:close,shot:shot,upgrade:inc,rank:r,level:lvl,free:free,damage:damage,allocated:used,nodes:N,thresholds:TH};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",install);else install();
})();