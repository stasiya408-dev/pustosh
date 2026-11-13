(function(){
/* v366: ПІДКАЗКИ НА КОЖНОМУ ЕКРАНІ. Кнопка «?» (#tp9) з'являється, коли відкрито екран зі списку SC; при ПЕРШОМУ заході на екран
   підказка показується сама (один раз, S.d9.tp[id]); поки йде Дід Охрім (html.gdon) — сама не лізе, але «?» працює.
   Кубики не пояснюємо (за побажанням власника). Екрани з власним путівником (Облога, Рейд місяця) «?» не мають.
   Щоб додати екран: запис у SC (id, як перевірити «відкрито», заголовок, пункти). Тексти ВСІ мої (UNAPPROVED). */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc;
function shown(el,minW,minH){if(!el)return false;try{var cs=getComputedStyle(el);if(cs.display=="none"||cs.visibility=="hidden"||parseFloat(cs.opacity)<.05)return false;var r=el.getBoundingClientRect();return r.width>=(minW||200)&&r.height>=(minH||120)}catch(e){return false}}
function on(id){return function(){var e=document.getElementById(id);return !!e&&e.classList.contains("on")}}
function sh(id,w,h){return function(){return shown(document.getElementById(id),w,h)}}
/* pos: br (низ-право, за замовчуванням) | tr (право-вгорі, нижче шапки) */
var SC=[
 {id:"dzS",ok:on("dzS"),t:"Скриня",i:[["🧩","**Колекції** — збирай у походах, обмінюй на нагороду"],["🔒","Сіра плитка — відкриється на вказаному **рівні**"],["🔴","Кружечок — є що забрати"]]},
 {id:"dzL",ok:on("dzL"),t:"Літопис",i:[["✅","**Справи** — 5 на день, за всі — скриня"],["🏆","**Тиждень** — рейтинг, нагорода за місце"],["🔴","**Забрати** — натисни кнопку"]]},
 {id:"dzA",ok:on("dzA"),t:"Арена",i:[["🏚️","**Хутір** дає 🥈, поки ти далеко — «Зібрати все»"],["⚔️","Захопи двобоєм (−2 ⚡)"],["🛡️","Замах зверху — **блок**, широкий — **ухил**"]]},
 {id:"dzP",ok:on("dzP"),t:"Кіт",i:[["🐈","**Годуй** — ситий кіт дає навички"],["🤚","**Погладити** раз на день — ⚡"],["🔓","Звільни перемогою над **Мареною**"]]},
 {id:"dzW",ok:on("dzW"),t:"Колесо",i:[["🎡","**Крутити** — перша крутка безкоштовна"],["🥈","Далі дорожче, **6** на добу"]]},
 {id:"jkx",ok:sh("jkx"),t:"Торговець",i:[["🔩","**Хлам** — з босів, походів, налітів"],["👆","Натисни **ціну** — купиш закуп"],["🎁","**Комод** — випадкова нагорода"]]},
 {id:"ward",ok:sh("ward",200,60),t:"Одяг",i:[["👆","Угорі — **частина тіла**"],["👕","**Одягти** / **Зняти**"],["🔒","Закрите — здобудеш пізніше"]]},
 {id:"jwx",ok:sh("jwx"),t:"Коваль",i:[["🔨","**Ковка** — перстень з уламків"],["✨","**Заточка** — до +10, більше шкоди"],["💥","**Розламати** — назад в уламки"]]},
 {id:"stx",ok:sh("stx"),t:"Стійло",i:[["🐎","Швидший кінь — менше втоми, легше втекти"],["🌾","**Годуй** — кінь росте"],["🔁","**Осідлати** — обрати коня"]]},
 {id:"trx",ok:sh("trx"),t:"Трофеї",i:[["🏆","Дає **перша перемога** над босом"],["🏠","**Повісити** в хаті"]]},
 {id:"gach",ok:sh("gach"),t:"Досягнення",i:[["🏅","Виконав — **Забрати** 💰"],["📈","Смужка — скільки лишилось"]]},
 {id:"rtx",ok:sh("rtx"),t:"Рейтинг",i:[["📊","Вкладки: походи, шкода, боси"],["📅","**Сезон** — 4 тижні"],["👤","Тисни на гравця — профіль"]]},
 {id:"talentModal",ok:sh("talentModal"),t:"Таланти",i:[["⭐","Очки — за **власну** шкоду по босах"],["👆","Тисни талант — **вклади очко**"],["🔓","Нижні ступені відкривають вищі"]]},
 {id:"mkt2",ok:sh("mkt2"),t:"Ринок",i:[["👆","Тисни **лавку**"],["👈","Свайп — далі по ринку"]]},
 {id:"nbx",ok:sh("nbx",200,300),t:"Боси",i:[["🔑","Бій = **1 ключ**"],["👥","**Соло** або **Відряд** з друзями"],["🎯","Обери зброю, **тапай по босу**"],["🔒","Платна зброя — після **3** безкоштовних ударів"]]},
 {id:"hike",ok:sh("hike"),t:"Похід",i:[["🎒","Візьми **їжу**, **воду**, трави"],["🗺️","Тисни точку на карті"],["⚡","Вхід — енергія, вихід — **живим**"]]}
];
var MAIN={id:"main",t:"Головний екран",i:[["👆","**Козак** — одяг і персні"],["🧭","Внизу: **Похід · Ринок · Боси · Таверна · Арена**"],["➡️","Стрічка справа — **Скриня, Літопис**"],["🔴","Кружечок — є що **забрати**"]]};
var cur=null,since=0,btn=null,ov=null;
function seenOf(id){var d=T();return !!(d.tp&&d.tp[id])}
function mark(id){var d=T();d.tp=d.tp||{};d.tp[id]=1;P.save()}
function find(){
 for(var i=0;i<SC.length;i++){var s=SC[i];try{if(s.ok())return s}catch(e){}}
 return null}
function mainOpen(){
 if(P.anyOpen())return false;
 var nav=document.getElementById("nav2");if(!nav)return false;var r=nav.getBoundingClientRect();if(r.width<50||r.height<20)return false;
 var e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return !!(e&&e.closest("#nav2"))}
function hl(t){return esc(t).replace(/\*\*(.+?)\*\*/g,'<b class="hlt">$1</b>')}
function card(s){
 var h='<div class="dzc"><div class="dzt"><b>💡 '+esc(s.t)+'</b><button data-z="x" aria-label="Закрити">✕</button></div><div class="dkh">';
 s.i.forEach(function(x){h+='<div><b>'+x[0]+'</b><span class="tpt">'+hl(x[1])+'</span></div>'});
 return h+'</div><button class="dzb g dzbig" style="margin-top:8px" data-z="x">Зрозуміло</button></div>'}
function show(s){
 if(!ov){ov=P.ov("dzT",function(){});ov.style.zIndex=99998}
 P.show(ov,card(s));mark(s.id)}
function busyGuide(){var h=document.documentElement;if(h.classList.contains("gdon"))return true;var g=document.getElementById("gdc");if(g&&g.classList.contains("on"))return true;var w=document.getElementById("tqw");if(w&&w.offsetParent!==null)return true;return false}
function ensureBtn(){
 if(btn)return;btn=document.createElement("button");btn.id="tp9";btn.type="button";btn.setAttribute("aria-label","Підказка");btn.textContent="?";
 btn.addEventListener("click",function(e){e.stopPropagation();var s=cur;if(!s)return;if(ov&&ov.classList.contains("on")){P.shut(ov);return}show(s)});
 document.body.appendChild(btn)}
function tick(){
 ensureBtn();
 var tipOpen=ov&&ov.classList.contains("on");
 var s=find();
 if(!s&&!tipOpen&&mainOpen())s=MAIN;
 if(tipOpen&&cur)s=cur;
 if(!s){cur=null;btn.className="";since=0;return}
 if(s.id==="main"){btn.className="";/* на головному «?» не показуємо: мінімалізм */}
 else{btn.className="on"+(s.pos==="tr"?" up":"")+(seenOf(s.id)?"":" nw")}
 if(!cur||cur.id!==s.id){cur=s;since=Date.now();return}
 if(!seenOf(s.id)&&!tipOpen&&Date.now()-since>900&&!busyGuide())show(s)}
setInterval(tick,450);
window.TIPS={open:function(id){var s=id=="main"?MAIN:SC.filter(function(x){return x.id==id})[0];if(s)show(s)},list:function(){return SC.map(function(x){return x.id})},reset:function(){var d=T();d.tp={};P.save()},cur:function(){return cur&&cur.id}};
/* ---- торговець: зрозуміла кнопка закупу ---- */
var jo=null,busyJ=false;
function fixJ(){
 if(busyJ)return;var root=document.getElementById("jkx");if(!root)return;busyJ=true;
 try{
  var b=root.querySelector('[data-j="lv"]');
  var cap=[].slice.call(root.querySelectorAll(".q.cr")).filter(function(e){return /^(Купиш цей закуп|👆|Не вистачає хламу)/.test((e.textContent||"").trim())})[0];
  if(b){var can=!b.querySelector(".qd");b.classList.toggle("can",can);
   if(cap){var t=can?"👆 Тисни на ціну праворуч — купиш закуп":"Не вистачає хламу — збирай з босів і походів";if(cap.textContent!==t)cap.textContent=t}}
 }catch(e){}
 busyJ=false}
function watchJ(){var root=document.getElementById("jkx");if(!root){setTimeout(watchJ,1500);return}
 jo=new MutationObserver(function(){fixJ()});jo.observe(root,{childList:true,subtree:true});fixJ()}
setTimeout(watchJ,1200);
})();
