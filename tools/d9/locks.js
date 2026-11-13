(function(){
/* v370: функції відкриваються поступово (видно одразу, але зі замком, поки не дорослий до рівня). Числа — чернетка. */
var P=window.D9;if(!P)return;
var esc=P.esc;
/* id, значок, назва, потрібний рівень, звідки брати досвід */
var ALL=[
 ["col","🧩","Колекції",3,"Ходи в походи"],
 ["junk","🧰","Торговець",4,"Бий босів і ходи в походи"],
 ["arena","🏟","Арена і хутори",5,"Грай у кості, бий босів"],
 ["wheel","🎡","Колесо фортуни",5,"Збирай срібло та рівні"],
 ["stable","🐎","Стійло",6,"Ходи в походи"],
 ["ring","💍","Перстні",6,"Бий босів — з них падають уламки"],
 ["trof","🏆","Трофеї",7,"Перемагай босів"],
 ["smith","🔨","Коваль",8,"Збери уламки перснів із босів"],
 ["nal","🛡","Наліт на обоз",9,"Ходи в походи"],
 ["siege","🏰","Облога фортеці",12,"Бий босів, грай щодня"],
 ["raid","🐉","Рейд місяця",15,"Бий босів, грай щодня"]];
var BY={};ALL.forEach(function(a){BY[a[0]]=a});
function T(){var d=S.d9;if(!d)return {};return d}
function C(){var d=T();if(!d.lk)d.lk={s:null};return d.lk}
function lv(){return S.lv||1}
function ok(id){var a=BY[id];if(!a)return true;if(T().lkAll)return true;return lv()>=a[3]}
function left(id){var a=BY[id];return a?Math.max(0,a[3]-lv()):0}
function deny(id){var a=BY[id];if(!a)return;var n=left(id);
 P.toast("🔒 «"+a[2]+"» відкриється на рівні "+a[3]+(n?" (ще "+n+")":"")+". "+a[4]+".")}
/* наступне закриті: найближча за рівнем */
function next(){var best=null;ALL.forEach(function(a){if(!ok(a[0])&&(!best||a[3]<best[3]))best=a});return best}
function prevTh(a){var p=1;ALL.forEach(function(b){if(b[3]<a[3]&&b[3]>p)p=b[3]});return p}
function strip(){var a=next();
 if(!a)return '<div class="lkstrip"><b>🔓 Усе відкрито</b><small>Скриня повністю твоя, козаче. Тепер — рекорди й рейтинг.</small></div>';
 var p=prevTh(a),t=a[3]-p,v=Math.max(0,Math.min(t,lv()-p)),pc=Math.round(v/Math.max(1,t)*100);
 var more=ALL.filter(function(b){return !ok(b[0])}).length;
 return '<div class="lkstrip"><b>🔓 Наступне: '+a[1]+' '+esc(a[2])+'</b><small>Рівень '+lv()+' з '+a[3]+' · ще '+(a[3]-lv())+'. '+esc(a[4])+'.'+(more>1?' Усього ще закрито: '+more+'.':'')+'</small><div class="dzbar"><i style="width:'+pc+'%"></i></div></div>'}
/* значок на плитці Скрині */
function cls(id){return ok(id)?'':' lkd'}
function tag(id){if(ok(id))return '';var a=BY[id];return '<em class="lkt">🔒 рів. '+a[3]+'</em>'}
/* для плиток: true = закрито, показали підказку */
function gate(id){if(ok(id))return false;deny(id);return true}
/* ---- замок на кнопках і виклики ---- */
var BTN=[['#stbtn','stable'],['#rdbtn','nal'],['#nav2 [data-a="arena"],#mnav2 [data-g="arena"],#mnav2 [data-a="arena"],#dnav2 [data-g="arena"],#dnav2 [data-a="arena"],#nav2 [data-g="arena"]','arena']];
function hit(t){if(!t||!t.closest)return null;for(var i=0;i<BTN.length;i++){try{if(t.closest(BTN[i][0]))return BTN[i][1]}catch(e){}}return null}
document.addEventListener("click",function(e){var id=hit(e.target);if(id&&!ok(id)){e.stopImmediatePropagation();e.stopPropagation();e.preventDefault();deny(id)}},true);
function paint(){BTN.forEach(function(b){var els=[];try{els=document.querySelectorAll(b[0])}catch(e){}
  for(var i=0;i<els.length;i++){var el=els[i],lk=!ok(b[1]);el.classList.toggle("lk9",lk);var bd=el.querySelector(":scope>.lkb");
   if(lk&&!bd){if(getComputedStyle(el).position=="static")el.style.position="relative";bd=document.createElement("s");bd.className="lkb";bd.textContent="🔒";el.appendChild(bd)}
   if(!lk&&bd)bd.remove()}})}
var WR=[["JUNK","open","junk"],["TROPHY","open","trof"],["D9W","open","wheel"],["D9G","open","siege"],["D9R","open","raid"],["D9A","open","arena"],["RAID","open","nal"],["RAID","start","nal"],["HORSE","open","stable"]],wrapped={};
function wrap(){var all=true;
 WR.forEach(function(w){var k=w[0]+"."+w[1],o=window[w[0]];if(wrapped[k])return;if(!o||typeof o[w[1]]!="function"){all=false;return}
  var f=o[w[1]];o[w[1]]=function(){if(!ok(w[2])){deny(w[2]);return}return f.apply(this,arguments)};wrapped[k]=1});
 if(!wrapped.jw&&typeof window.jwOpen=="function"){var jo=window.jwOpen;window.jwOpen=function(m){var id=(m=="forge")?"smith":"ring";if(!ok(id)){deny(id);return}return jo.apply(this,arguments)};wrapped.jw=1}else if(!wrapped.jw)all=false;
 return all}
/* ---- повідомлення «Відкрито!» ---- */
function news(){var c=C();
 if(c.s===null||c.s===undefined){c.s={};ALL.forEach(function(a){if(ok(a[0]))c.s[a[0]]=1});P.save();return}
 if(document.documentElement.classList.contains("gdon")||P.anyOpen())return;
 for(var i=0;i<ALL.length;i++){var a=ALL[i];if(ok(a[0])&&!c.s[a[0]]){c.s[a[0]]=1;P.save();
   P.toast("🔓 Відкрито: "+a[1]+" "+a[2]+"! Дивись у Скрині.");return}}}
function tick(){try{paint();news()}catch(e){}}
var tries=0;function boot(){if(!wrap()&&tries++<30)setTimeout(boot,1000);tick();setInterval(tick,1500)}
window.D9L={ok:ok,lv:lv,left:left,deny:deny,gate:gate,next:next,strip:strip,cls:cls,tag:tag,all:ALL,sync:tick,
 unlockAll:function(v){T().lkAll=v===false?0:1;P.save();tick()}};
P.lk=ok;
if(document.readyState=="complete")setTimeout(boot,1300);else window.addEventListener("load",function(){setTimeout(boot,1300)});
})();
