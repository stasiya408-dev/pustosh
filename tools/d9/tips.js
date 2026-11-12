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
 {id:"dzS",ok:on("dzS"),t:"Скриня",i:[["🧩","Колекції — предмети набору збираються в походах. Збереш усі — обміняєш на нагороду."],["🧰","Торговець, Трофеї, Перстні, Коваль — це швидкі входи в ті самі екрани."],["🔔","Червоний кружечок на плитці — там є що забрати."]]},
 {id:"dzL",ok:on("dzL"),t:"Літопис",i:[["📜","Зведення — твоє звання, найближчі досягнення, майстерність коваля."],["✅","Справи — 5 завдань на день. Нагорода за кожне йде сама, а за всі п'ять — ще скриня."],["🏆","Тиждень — рейтинг з іншими. Місце в кінці тижня дає скриню."]]},
 {id:"dzA",ok:on("dzA"),t:"Арена · хутори",i:[["🏚️","Хутір приносить срібло, поки ти далеко. Натисни «Зібрати все», коли накопичиться."],["⚔️","Щоб захопити хутір, переможи господаря в двобої (−2 ⚡)."],["🛡️","Ворог замахується — дивись на підказку: «високий удар» → БЛОК, «широкий замах» → УХИЛ. Вчасно відбив — контрудар ×2,4."]]},
 {id:"dzP",ok:on("dzP"),t:"Кіт",i:[["🐈","Годуй кота (корм за срібло): ситий кіт дає навички. Голодний — навички вимкнені."],["🤚","«Погладити» раз на день дає ⚡."],["🔓","Кіт спочатку в клітці — його звільняє перемога над Мареною."]]},
 {id:"dzW",ok:on("dzW"),t:"Колесо фортуни",i:[["🎡","Натисни «Крутити» — випаде приз. Перша крутка на день безкоштовна."],["🥈","Далі кожна крутка дорожча, усього 6 на добу."]]},
 {id:"jkx",ok:sh("jkx"),t:"Заїжджий торговець",i:[["🔩","Хлам — валюта торговця. Його дають боси, походи й наліт на обоз."],["👆","Закупи йдуть ПО ПОРЯДКУ (усього 1000). Натисни кнопку з ціною праворуч від нагороди — купиш закуп, одразу з'явиться наступний."],["📊","Смужка зверху — скільки закупів вже куплено."],["⚡","«Купити скільки вистачить» бере кілька закупів підряд."],["🧰","Комод — 10 хламу за випадкову нагороду."]]},
 {id:"ward",ok:sh("ward",200,60),t:"Одяг казака",i:[["👆","Угорі — значки частин тіла: взуття, руки, штани, тулуб, голова. Обери частину."],["👕","У списку натисни «Одягти» під потрібною річчю. «Зняти» — прибрати."],["🔒","Закрита річ ще не здобута: її дають за досягнення в таверні."],["💍","Персні теж тут — у вкладці «Руки»."]]},
 {id:"jwx",ok:sh("jwx"),t:"Коваль і ювелір",i:[["🔨","Ковка: з уламків перстня виковуєш перстень. Шанс успіху показано на кнопці."],["✨","Заточка: підвищує перстень до +10 — сильніший бонус до шкоди по босах."],["💥","Розламати: перстень → уламки, якщо він вже не потрібен."],["❓","Тисни на «Як це працює» всередині — там цифри."]]},
 {id:"stx",ok:sh("stx"),t:"Стійло",i:[["🐎","Кінь дає швидкість: у поході менше втоми, у нальоті — легше втекти."],["🌾","Годуй сіном чи вівсом: ситий кінь швидший і росте в рівні."],["🔁","Обери коня зі стійла й натисни «Осідлати». Нових коней дають боси."]]},
 {id:"trx",ok:sh("trx"),t:"Трофеї",i:[["🏆","Трофей дають за першу перемогу над босом."],["🏠","«Повісити в хаті» — він з'явиться на головному екрані, «Прибрати» — забрати."]]},
 {id:"gach",ok:sh("gach"),t:"Досягнення",i:[["🏅","Кожне виконане досягнення дає талери 💰 — вони з'являються самі."],["📈","Смужка під назвою — скільки ще лишилось."]]},
 {id:"rtx",ok:sh("rtx"),t:"Рейтинг",i:[["📊","Вгорі вкладки: Походи, Шкода, Боси, Загальний."],["📅","«Сезон» — змагання на 4 тижні, «За весь час» — загальне."],["👤","Натисни на гравця — відкриється його профіль."]]},
 {id:"talentModal",ok:sh("talentModal"),t:"Козацька майстерність",i:[["⭐","Очки талантів дає ТВІЙ власний урон по босах (не відряду)."],["👆","Натисни талант, щоб вкласти очко. Нижчі ступені відкривають вищі."],["🔄","Невитрачений досвід не пропадає."]],pos:"tr"},
 {id:"mkt2",ok:sh("mkt2"),t:"Ринок",i:[["👆","Торкнись лавки: зброяр (самопал за талери), коваль, ювелір."],["👈","Ринок гортається вбік — свайп по картинці."],["🚪","Внизу ті самі розділи, що й на головному."]]},
 {id:"nbx",ok:sh("nbx",200,300),t:"Боси",i:[["🔑","Бій з босом коштує ключ. Ключі дають перемоги та походи."],["👥","Режим: Соло — сам (боса менше), Відряд — з друзями (друзі теж б'ють)."],["🎯","У бою обери зброю внизу й тапай по босу. Перші 3 безкоштовні удари (кулак, нога, шабля) відкривають платну зброю."],["🏆","Переможеш — на екрані нагород заберуть усе випадене."]],pos:"tr"},
 {id:"hike",ok:sh("hike"),t:"Похід",i:[["🎒","Перед походом візьми припаси (їжа, вода, трави) і обери маршрут."],["🗺️","На карті тисни точку: ❓ подія, ⚔️ засідка, 🏹 полювання, 🏕️ привал, 👹 бос."],["⚡","Вхід коштує енергію, а повертатися живим — вигідніше. Хлам і ключі даються за успішне повернення."],["🏴","Налітом на обоз керує червона стрічка на цьому екрані."]],pos:"tr"}
];
var MAIN={id:"main",t:"Головний екран",i:[["👆","Торкнись козака — відкриється одяг: шапка, жилет, шаровари, чоботи, персні."],["🧭","Внизу п'ять розділів: Похід, Ринок, Боси, Таверна, Арена."],["➡️","Справа червона стрічка зі стрілкою — з неї виїжджає панель: скриня, літопис, кінь, торговець."],["🔴","Червоний кружечок — там щось готове."]]};
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
function card(s){
 var h='<div class="dzc"><div class="dzt"><b>💡 '+esc(s.t)+'</b><button data-z="x" aria-label="Закрити">✕</button></div><div class="dkh">';
 s.i.forEach(function(x){h+='<div><b>'+x[0]+'</b><span class="tpt">'+esc(x[1])+'</span></div>'});
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
