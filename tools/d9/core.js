(function(){
/* v359: общее ядро новых механик (без сервера). Состояние: S.d9. ВСЕ числа — черновик (UNAPPROVED). */
if(window.D9)return;
var P=window.D9={};
function T(){var d=S.d9;if(!d||typeof d!="object")d=S.d9={};return d}
P.T=T;
P.day=function(t){try{return kyivDate(t)}catch(e){return new Date(t||Date.now()).toISOString().slice(0,10)}};
P.dn=function(ds){var p=(ds||P.day()).split("-");return Math.floor(Date.UTC(+p[0],+p[1]-1,+p[2])/864e5)};
P.week=function(){return Math.floor((P.dn()+3)/7)};
P.dow=function(){return (P.dn()+3)%7};
P.secOfDay=function(){try{var tz=(typeof CFG!="undefined"&&CFG.GAME_TIMEZONE)||"Europe/Kiev";var f=new Intl.DateTimeFormat("en-GB",{timeZone:tz,hour:"2-digit",minute:"2-digit",second:"2-digit",hour12:false}).formatToParts(new Date());var o={};f.forEach(function(x){o[x.type]=+x.value});return ((o.hour%24)*3600)+o.minute*60+o.second}catch(e){var d=new Date();return d.getUTCHours()*3600+d.getUTCMinutes()*60+d.getUTCSeconds()}};
P.msToWeekEnd=function(){return ((7-P.dow())*86400-P.secOfDay())*1000};
P.msToDayEnd=function(){return (86400-P.secOfDay())*1000};
P.fmtLeft=function(ms){ms=Math.max(0,ms);var s=Math.floor(ms/1000),d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return d?d+" дн "+h+" год":h?h+" год "+m+" хв":m+" хв"};
P.rng=function(str){var h=2166136261;for(var i=0;i<str.length;i++){h^=str.charCodeAt(i);h=Math.imul(h,16777619)}return function(){h+=0x6D2B79F5;var t=Math.imul(h^(h>>>15),1|h);t^=t+Math.imul(t^(t>>>7),61|t);return((t^(t>>>14))>>>0)/4294967296}};
P.esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})};
P.fs=function(n){return String(Math.floor(n||0)).replace(/\B(?=(\d{3})+(?!\d))/g," ")};
P.say=function(t){try{say(t)}catch(e){}};
P.toast=function(t){try{toast(t)}catch(e){P.say(t)}};
P.save=function(){try{window.gsave&&window.gsave()}catch(e){}};
P.give=function(r){
 if(r.sv){S.sv=(S.sv||0)+r.sv;if(S.sv>(S.svm||0))S.svm=S.sv}
 if(r.tl)S.tl=(S.tl||0)+r.tl;
 if(r.en)S.en=Math.min(MAXEN,(S.en||0)+r.en);
 if(r.pw)S.pw=(S.pw||0)+r.pw;
 if(r.junk){try{var j=S.junk;if(j){j.bal=(j.bal||0)+r.junk;j.tot=(j.tot||0)+r.junk}}catch(e){}}
 try{draw()}catch(e){}P.save()};
P.rewTxt=function(r){var a=[];if(r.sv)a.push(P.fs(r.sv)+" 🥈");if(r.tl)a.push(r.tl+" 💰");if(r.en)a.push(r.en+" ⚡");if(r.junk)a.push(r.junk+" 🔩");if(r.pw)a.push(r.pw+" 💪");return a.join(" · ")};
P.ov=function(id,onAct){var o=document.getElementById(id);if(o)return o;o=document.createElement("div");o.id=id;o.className="dzo";document.body.appendChild(o);
 o.addEventListener("click",function(e){if(e.target===o){P.shut(o);return}var a=e.target.closest("[data-z]");if(!a||!o.contains(a))return;var k=a.getAttribute("data-z");if(k=="x"){P.shut(o);return}if(o._act)o._act(k,a,e)});
 o._act=onAct;return o};
P.shut=function(o){o.classList.remove("on");if(o._onclose)o._onclose()};
P.show=function(o,html){o.innerHTML=html;o.classList.add("on")};
P.anyOpen=function(){return !!document.querySelector(".dzo.on")};
/* кобзар: короткая присказка дня */
var KOB=["Кобзар: «Хто рано встає — тому Бог дає, а хто пізно — тому шинкарка наливає».","Кобзар: «Козак без шаблі — як борщ без сала: їсти можна, та сумно».","Кобзар: «Не той козак, що в битві перший, а той, хто з обозу цілим вернувся».","Кобзар: «Сила є — розуму не треба. Розум є — сила знайдеться».","Кобзар: «Лінивому й самопал не стріляє».","Кобзар: «Де козак — там і слава. Де слава — там і кум із чаркою».","Кобзар: «Бий боса — не питай, чи гарно. Питай — чи довго».","Кобзар: «Сорок разів перевір, один раз бахни».","Кобзар: «Серед степу бачиш далі, а все одно не бачиш, куди йдеш».","Кобзар: «Кому хутір, кому курган, а кому — гарна байка біля вогню».","Кобзар: «Гетьман без булави — просто дядько з вусами».","Кобзар: «Енергія закінчилась? Козак теж людина. Іди перекуси».","Кобзар: «У кого шаблі нема, у того язик гострий».","Кобзар: «Сьогодні шеляг, завтра — гетьманська шуба».","Кобзар: «Не поспішай, козаче: татарин теж не бігає без діла»."];
P.kob=function(salt){var n=(P.dn()*7+(salt||0))%KOB.length;return KOB[n]};
/* звания по уровню */
var RANKS=[[1,"Джура","носить чужу зброю та мовчить","🪖"],[5,"Козак","вже має власну шаблю й чуб","⚔️"],[12,"Осавул","усе бачить, обідає першим","👁"],[25,"Курінний","у нього курінь і претензії","🏕"],[50,"Отаман","слово його — закон, жінка його — виняток","🪶"],[100,"Кошовий","Сірко на пенсії спить спокійно","👑"]];
P.RANKS=RANKS;
P.rank=function(){var lv=S.lv||1,i=0;RANKS.forEach(function(r,k){if(lv>=r[0])i=k});var n=RANKS[i+1]||null;return {i:i,n:RANKS[i][1],d:RANKS[i][2],ic:RANKS[i][3],from:RANKS[i][0],next:n,lv:lv}};
/* смешные добавки к отказам */
var _say=window.say;
if(typeof _say=="function"){
 var J1=[" Піди до шинкарки — вона знає, де його немає."," Гроші, як вареники: були — і нема."," Козак без срібла — це просто чоловік із шаблею."];
 var J2=[" Козак теж людина: перекуси й відпочинь."," Енергія закінчилась разом із запалом."," Навіть Сірко іноді спав."];
 window.say=say=function(t){try{if(typeof t=="string"&&t.length<140&&!/[.!?]\s.*[.!?]$/.test(t)&&Math.random()<.45){
  if(/(Бракує|Не вистачає|Не хватает|Недостаточно)[^.]{0,30}(срібл|серебр|🥈)/i.test(t))t+=J1[Math.floor(Math.random()*J1.length)];
  else if(/(Бракує|Не вистачає|Не хватает|Нет сил|Недостаточно)[^.]{0,30}(⚡|енерг|энерг)/i.test(t))t+=J2[Math.floor(Math.random()*J2.length)]}}catch(e){}
  return _say(t)}}
/* смешные названия оружия (только подписи) */
try{var L=GAME_CONFIG.BOSSCFG.WEAPONS.LIST;L.forEach(function(w){if(w.id=="fist")w.uk="Дуля";if(w.id=="foot")w.uk="Копняк"})}catch(e){}
/* прогресс ближайших достижений */
P.near=function(n){var out=[];try{var pr=window.GPROG||{},g=S.gach||{},A={};(window.GACH||[]).forEach(function(a){A[a[0]]=a});var fam={};Object.keys(pr).forEach(function(id){if(g[id]||!A[id])return;var v=0;try{v=pr[id][0]()}catch(e){return}var t=pr[id][1];if(v>=t)return;var f=id.replace(/\d+$/,"");if(!fam[f]||t<fam[f].t)fam[f]={id:id,a:A[id],v:v,t:t,r:v/t}});out=Object.keys(fam).map(function(k){return fam[k]});out.sort(function(a,b){return b.r-a.r||a.t-b.t})}catch(e){}return out.slice(0,n||3)};
})();
