(function(){
/* v362: «Колода» — комбо в бою з босом (замість «Комбо дня»). Ставиш платну зброю в 3 місця, з них складається «рука»
   (Драбина, Трійця, Пара, Купа). Всі постріли летять у боса (шкода зараховується), а потім на склад повертається
   ТА САМА зброя: за гарну руку — трохи більше, ніж вклав; за «Купу» — трохи менше. Бонус +10%, якщо рука збіглася зі «слабиною дня» боса.
   Без сервера. Числа — чернетка, не затверджені. */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc,fs=P.fs;
var PAID=["dagger","samopal","rifle","volley","cannon"];
var NM={dagger:"Кинджал",samopal:"Самопал",rifle:"Рушниця",volley:"Залп стріл",cannon:"Гармата"};
var EM={dagger:"🗡",samopal:"🔫",rifle:"🔫",volley:"🏹",cannon:"💣"};
var PR={dagger:3,samopal:6,rifle:12,volley:24,cannon:48};
var STK=[["Мала",1],["Середня",3],["Велика",10]];
var HANDS={
 lad:{n:"Драбина",b:.25,d:"три різні, ціна зростає"},
 tri:{n:"Трійця",b:.15,d:"три однакові"},
 par:{n:"Пара",b:.10,d:"дві однакові"},
 kup:{n:"Купа",b:-.10,d:"три різні, без ладу"}};
var FAVB=.10,DAYLIM=3;
var ov,sl=[null,null,null],sk=1,running=false,btn;
function C(){var d=T();if(!d.bc)d.bc={d:"",n:{},carry:0,tot:0,p:0};var c=d.bc;if(c.d!==P.day()){c.d=P.day();c.n={};c.p=0}return c}
function WPo(){return window.WP||null}
function ammo(id){try{return Math.max(0,WP.ammo(WP.BY[id])||0)}catch(e){return 0}}
function ic(id){var u="";try{u=window.getItemIcon&&getItemIcon("w_"+id)}catch(x){}
 return u?'<img src="'+u+'" alt="" draggable="false">':'<span>'+EM[id]+'</span>'}
function act0(){try{return window.btActive&&btActive()}catch(e){return null}}
function bossBy(id){try{for(var i=0;i<BOSSES.length;i++)if(BOSSES[i].id==id)return BOSSES[i]}catch(e){}return null}
function fightVis(){var f=document.getElementById("nbF");return !!(f&&f.getClientRects().length)}
function bossLive(){var t=act0();if(!t)return false;try{var b=S.bd&&S.bd[t.mode];return !!(b&&b.hp>0)}catch(e){return false}}
function fav(bid){var r=P.rng(P.day()+"|dk|"+bid);return ["lad","tri","par"][Math.floor(r()*3)]}
function hand(a){if(a.indexOf(null)>=0)return null;var u={};a.forEach(function(x){u[x]=1});var k=Object.keys(u).length;
 if(k==1)return "tri";if(k==2)return "par";
 return (PR[a[0]]<PR[a[1]]&&PR[a[1]]<PR[a[2]])?"lad":"kup"}
function bonus(h,bid){return HANDS[h].b+(h==fav(bid)?FAVB:0)}
function used(){var c=C(),t=act0();return t?(c.n[t.bid]||0):0}
function playedToday(){return C().p||0}
function locked(){try{return WP.allowed(WP.BY.dagger)=="lock"}catch(e){return false}}
function need(){var n={};sl.forEach(function(x){if(x)n[x]=(n[x]||0)+STK[sk][1]});return n}
function enough(){var n=need(),ok=true;Object.keys(n).forEach(function(k){if(ammo(k)<n[k])ok=false});return ok}
var gp=-1; /* сторінка путівника: -1 = головний екран */
function chain(ids){return ids.map(function(i){return '<span class="dke">'+ic(i)+'</span>'}).join('<i class="dka">→</i>')}
function pct(x){return (x>=0?'+':'')+Math.round(x*100)+'%'}
function priceLine(){return PAID.map(function(i){return NM[i]+' '+PR[i]}).join(' · ')}
var GUIDE=[
 {t:"Що це таке",b:function(){return ''+
  '<p>Колода — це <b>обмін зброї просто під час бою</b> з босом.</p>'+
  '<p>1. Ти віддаєш у бій платну зброю (кинджал, самопал…).<br>2. <b>Усі ці постріли справді летять у боса</b> і б’ють його — як звичайні.<br>3. Потім на склад <b>повертається така сама зброя</b>, зазвичай <b>трохи більше</b>, ніж віддав.</p>'+
  '<div class="dzhero"><div class="em">🃏</div><div style="flex:1"><b>Приклад</b><small>Віддав 9 самопалів. Усі 9 вдарили боса. На склад повернулось 11 самопалів. І босові дісталось, і зброї побільшало.</small></div></div>'+
  '<p>Скільки повернеться, залежить від «руки» — тобто від того, яку зброю і в якому порядку ти поставив. Далі розкажу, як це працює.</p>'}},
 {t:"Ставка і три місця",b:function(){return ''+
  '<p>У Колоди <b>три місця</b>. У кожне місце ти кладеш <b>один вид</b> платної зброї.</p>'+
  '<p><b>Ставка</b> — скільки штук іде з кожного місця: <b>по 1</b> (мала), <b>по 3</b> (середня) або <b>по 10</b> (велика). Ставка однакова для всіх трьох місць.</p>'+
  '<div class="dzhero"><div class="em">🎯</div><div style="flex:1"><b>Приклад</b><small>Ставка «Середня» (по 3). Місця: '+chain(["dagger","samopal","cannon"])+' . Піде 3 кинджали + 3 самопали + 3 гармати = 9 пострілів по босу.</small></div></div>'+
  '<p>Платна зброя — це: кинджал, самопал, рушниця, залп стріл, гармата. <b>Безкоштовна зброя</b> (кулак, нога, шабля) у Колоді не бере участі.</p>'+
  '<p>Колода відкривається, коли в бою вже зроблено <b>3 безкоштовні удари</b> — так само, як і платна зброя.</p>'}},
 {t:"Рука і бонус",b:function(){return ''+
  '<p>З трьох місць складається <b>рука</b>. Від неї залежить, <b>скільки повернеться</b>.</p>'+
  '<div class="dkh"><div><b>Драбина '+pct(HANDS.lad.b)+'</b>'+chain(["dagger","samopal","cannon"])+'<small>три різні, і кожна наступна ДОРОЖЧА за попередню (зліва направо)</small></div>'+
  '<div><b>Трійця '+pct(HANDS.tri.b)+'</b>'+chain(["samopal","samopal","samopal"])+'<small>три однакові</small></div>'+
  '<div><b>Пара '+pct(HANDS.par.b)+'</b>'+chain(["samopal","samopal","dagger"])+'<small>дві однакові (порядок неважливий)</small></div>'+
  '<div class="bad"><b>Купа '+pct(HANDS.kup.b)+'</b>'+chain(["cannon","dagger","samopal"])+'<small>три різні, але не за зростанням ціни — повернеться менше, ніж віддав</small></div></div>'+
  '<p style="margin-top:9px"><b>Ціни зброї</b> (від цього залежить Драбина): '+priceLine()+'.</p>'+
  '<div class="dzhero"><div class="em">🧮</div><div style="flex:1"><b>Приклад</b><small>Драбина, ставка по 3: віддав 9, повернулось 9 × 1,25 ≈ 11. Купа: 9 × 0,9 ≈ 8.</small></div></div>'}},
 {t:"Слабина дня і ліміти",b:function(){return ''+
  '<p><b>Слабина дня.</b> Кожного дня в кожного боса є «улюблена рука» — Драбина, Трійця або Пара. Її написано зверху в Колоді. Якщо твоя рука збіглася з нею — ще <b>+'+Math.round(FAVB*100)+'%</b>.</p>'+
  '<div class="dzhero"><div class="em">⭐</div><div style="flex:1"><b>Приклад</b><small>Слабина боса — Драбина, і ти зібрав Драбину: +25% + 10% = +35%. Ставка по 3: 9 × 1,35 ≈ 12.</small></div></div>'+
  '<p><b>Ліміт.</b> На кожного боса — <b>'+DAYLIM+' колоди на добу</b>. Лічильник «n/'+DAYLIM+'» видно на кнопці Колоди в бою.</p>'+
  '<p><b>Якщо бос помер посеред ряду</b> — рахуються лише ті постріли, що встигли вилетіти. Повернення — тільки за них.</p>'+
  '<p><b>Дрібні залишки не пропадають:</b> якщо вийшло 11,25 — 11 повернулось зараз, а 0,25 запам’яталось і додасться до наступної Колоди.</p>'+
  '<p>Порада: найпростіше натиснути «✨ Підібрати за мене» — гра сама збере найкращу руку з того, що в тебе є.</p>'}}];
function guideHtml(){var g=GUIDE[gp],n=GUIDE.length;
 var s='<div class="dzc"><div class="dzt"><b>📖 Путівник · '+(gp+1)+'/'+n+'</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 s+='<div class="dkg"><h3>'+g.t+'</h3>'+g.b()+'</div>';
 s+='<div class="dkdots">';for(var i=0;i<n;i++)s+='<i class="'+(i==gp?'on':'')+'"></i>';s+='</div>';
 s+='<div style="display:flex;gap:8px;margin-top:10px">';
 s+=(gp>0?'<button class="dzb" style="flex:1;padding:11px" data-z="gp" data-k="'+(gp-1)+'">◀ Назад</button>':'<button class="dzb" style="flex:1;padding:11px" data-z="gp" data-k="-1">Пропустити</button>');
 s+=(gp<n-1?'<button class="dzb g" style="flex:1;padding:11px" data-z="gp" data-k="'+(gp+1)+'">Далі ▶</button>':'<button class="dzb g" style="flex:1;padding:11px" data-z="gp" data-k="-1">Зрозуміло, грати</button>');
 return s+'</div></div>'}
function autoPick(bid){var best=null,st=STK[sk][1];
 PAID.forEach(function(a){PAID.forEach(function(b){PAID.forEach(function(c){var arr=[a,b,c],n={},ok=true;
  arr.forEach(function(x){n[x]=(n[x]||0)+st});
  Object.keys(n).forEach(function(k){if(ammo(k)<n[k])ok=false});
  if(!ok)return;
  var bo=bonus(hand(arr),bid),cost=0;arr.forEach(function(x){cost+=PR[x]*st});
  if(!best||bo>best.bo+1e-9||(Math.abs(bo-best.bo)<1e-9&&cost<best.cost))best={a:arr,bo:bo,cost:cost}})})});
 return best}
function nextStep(t,left,h,n,tot){
 if(!t||!bossLive())return "Зараз бою з босом немає. Зайди в бій — і Колода відкриється.";
 if(locked())return "Спершу зроби 3 безкоштовні удари (кулак, нога, шабля) — тоді платна зброя і Колода відкриються.";
 if(left<=0)return "На сьогодні Колоди для цього боса вичерпано ("+DAYLIM+" з "+DAYLIM+"). Завтра — знову, або зайди до іншого боса.";
 var emp=sl.filter(function(x){return !x}).length;
 if(emp==3)return "Крок 2: постав зброю в три місця — тицяй на зброю внизу. Або просто натисни «✨ Підібрати за мене».";
 if(emp>0)return "Ще "+emp+" "+(emp==1?"порожнє місце":"порожні місця")+": тицяй на зброю внизу, щоб заповнити.";
 if(!enough())return "Не вистачає зброї на таку ставку. Зменш ставку (крок 1) або заміни зброю.";
 return "Усе готово! Натисни «🃏 Кинути в бій» — постріли полетять у боса, а зброя повернеться."}
function render(){if(!ov)return;
 if(gp>=0){var sc0=ov.querySelector(".dzc");ov.innerHTML=guideHtml();var n0=ov.querySelector(".dzc");if(n0)n0.scrollTop=0;return}
 var t=act0(),b=t?bossBy(t.bid):null,bid=t?t.bid:"",f=fav(bid),h=hand(sl),left=DAYLIM-used();
 var s='<div class="dzc"><div class="dzt"><b>🃏 Колода</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 s+='<div class="dzk">«'+(b?esc(b.n):"Бос")+' сьогодні любить <b>'+HANDS[f].n+'</b> ('+HANDS[f].d+'). Збереш її — повернеться ще +'+Math.round(FAVB*100)+'%.» — Кобзар</div>';
 s+='<button class="dzb dkhelp" data-z="gp" data-k="0">📖 Як це працює? Путівник</button>';
 var tot=STK[sk][1]*3,n=need();
 s+='<div class="dkhint" id="dkhint">'+esc(nextStep(t,left,h,n,tot))+'</div>';
 s+='<div class="dzs"><h4>1. Скільки на кожне місце</h4><div class="dkw">';
 STK.forEach(function(x,i){s+='<button class="dkt'+(i==sk?' on':'')+'" data-z="stk" data-k="'+i+'"><b>'+x[0]+'</b><small>по '+x[1]+'</small></button>'});
 s+='</div></div>';
 s+='<div class="dzs"><h4>2. Три місця колоди <small style="font-weight:400;color:#9d8a62">(тицьни — прибрати)</small></h4><div class="dkw">';
 for(var i=0;i<3;i++){var w=sl[i];s+='<button class="dkt dks'+(w?' fl':'')+'" data-z="clr" data-k="'+i+'">'+(w?ic(w)+'<small>'+NM[w]+' ×'+STK[sk][1]+'</small>':'<b>'+(i+1)+'</b><small>порожньо</small>')+'</button>'}
 s+='</div><button class="dzb dkauto" data-z="auto">✨ Підібрати за мене</button></div>';
 s+='<div class="dzs"><h4>3. Зброя (платна) <small style="font-weight:400;color:#9d8a62">(тицьни — покласти в місце)</small></h4><div class="dkw">';
 PAID.forEach(function(id){var a=ammo(id);s+='<button class="dkt dkw1'+(a<1?' off':'')+'" data-z="add" data-k="'+id+'">'+ic(id)+'<small>'+NM[id]+'</small><small class="dkc">'+a+' шт.</small></button>'});
 s+='</div></div>';
 if(h){var bo=bonus(h,bid),pv=Math.round(tot*(1+bo)),dl=pv-tot;
  var give=Object.keys(n).map(function(k){return NM[k]+' ×'+n[k]}).join(', ');
  var why=h=="lad"?'ціна зростає: '+sl.map(function(x){return PR[x]}).join(' → '):h=="kup"?'ціни: '+sl.map(function(x){return PR[x]}).join(', ')+' — не зростають':HANDS[h].d;
  s+='<div class="dzhero" style="margin-top:11px"><div class="em">🃏</div><div style="flex:1"><b>'+HANDS[h].n+' '+pct(HANDS[h].b)+(h==f?' · слабина боса +'+Math.round(FAVB*100)+'%!':'')+'</b>'+
   '<small>('+why+')</small>'+
   '<small style="font-style:normal;color:#f1dfae;margin-top:4px">Віддаєш: '+give+' — '+tot+' пострілів по босу.</small>'+
   '<small style="font-style:normal;color:#f1dfae">Повернеться: приблизно '+pv+' тієї самої зброї ('+(dl>=0?'+':'')+dl+', '+pct(bo)+').</small></div></div>'}
 else s+='<div class="dzx" style="margin-top:10px"><small style="color:#9d8a62">Заповни всі три місця — Кобзар назве руку і покаже, скільки повернеться.</small></div>';
 var why2="";
 if(!t||!bossLive())why2="Бій із босом зараз не йде.";
 else if(locked())why2="Спершу 3 безкоштовні удари (кулак, нога, шабля) — тоді платна зброя відкрита.";
 else if(left<=0)why2="Ліміт: "+DAYLIM+" колоди на кожного боса за добу.";
 else if(!h)why2="";
 else if(!enough())why2="Не вистачає зброї: "+Object.keys(n).filter(function(k){return ammo(k)<n[k]}).map(function(k){return NM[k]+" (треба "+n[k]+", є "+ammo(k)+")"}).join(", ");
 s+='<div style="margin-top:11px;display:flex;gap:8px;align-items:center"><button class="dzb g" style="flex:1;padding:11px" data-z="go"'+((why2||!h)?' disabled':'')+'>🃏 Кинути в бій</button></div>';
 s+='<small style="display:block;margin-top:6px;color:#d8996b">'+(why2||'')+'</small>';
 s+='<small style="display:block;margin-top:4px;color:#9d8a62">Колод на цього боса сьогодні: '+left+' з '+DAYLIM+'</small>';
 s+='<div class="dzs"><h4>Які бувають руки</h4><div class="dzx"><small>';
 s+='<b style="color:#ffd978">Драбина '+pct(HANDS.lad.b)+'</b> '+chain(["dagger","samopal","cannon"])+' — ціна зростає<br>';
 s+='<b style="color:#ffd978">Трійця '+pct(HANDS.tri.b)+'</b> '+chain(["samopal","samopal","samopal"])+' — три однакові<br>';
 s+='<b style="color:#ffd978">Пара '+pct(HANDS.par.b)+'</b> '+chain(["samopal","samopal","dagger"])+' — дві однакові<br>';
 s+='<b style="color:#e38a6b">Купа '+pct(HANDS.kup.b)+'</b> '+chain(["cannon","dagger","samopal"])+' — різні, без ладу<br>';
 s+='Ціни: '+priceLine()+'. Усі постріли летять у боса і завдають шкоди; після них на склад повертається та сама зброя — за руку.</small></div></div></div>';
 var sc=ov.querySelector(".dzc"),top=sc?sc.scrollTop:0;ov.innerHTML=s;var nn=ov.querySelector(".dzc");if(nn)nn.scrollTop=top}
function open(){if(running)return;var t=act0();if(!t||!bossLive()){P.toast("Колода грається в бою з босом: зайди в бій.");return}
 sl=[null,null,null];var c=C();if(!c.seen){c.seen=1;gp=0;P.save()}else gp=-1;render();ov.classList.add("on")}
function pay(fired,bid){
 var c=C(),h=hand(sl),bo=bonus(h,bid),got={},line=[],totIn=0,ids=Object.keys(fired),ex={},sum=0,base=0;
 ids.forEach(function(id){totIn+=fired[id];ex[id]=fired[id]*(1+bo);sum+=ex[id]});
 /* дробная часть общего возврата копится (c.carry) и достаётся при следующих колодах, поэтому малые ставки не «теряют» бонус */
 var tot=sum+(c.carry||0),W=Math.floor(tot+1e-9);c.carry=Math.round((tot-W)*1000)/1000;
 ids.forEach(function(id){got[id]=Math.floor(ex[id]+1e-9);base+=got[id]});
 var extra=Math.max(0,W-base),order=ids.slice().sort(function(p,q){return (ex[q]-Math.floor(ex[q]))-(ex[p]-Math.floor(ex[p]))}),g=0;
 while(extra>0&&g<50){got[order[g%order.length]]++;extra--;g++}
 var totOut=0;
 ids.forEach(function(id){var w=got[id];totOut+=w;
  if(w>0){if(id=="samopal")S.fz=(S.fz||0)+w;else{if(!S.wa)S.wa={};S.wa[id]=(S.wa[id]||0)+w}}
  line.push(NM[id]+" ×"+w)});
 c.p=(c.p||0)+1;c.n[bid]=(c.n[bid]||0)+1;c.tot=(c.tot||0)+1;P.cnt("dkp");if(bo>0)P.cnt("dkw");
 P.save();try{window.draw&&draw()}catch(e){}try{window.WP&&WP.ui&&WP.ui()}catch(e){}
 var d=totOut-totIn;
 P.toast("🃏 "+HANDS[h].n+(h==fav(bid)?" · слабина боса!":"")+": вклав "+totIn+", повернулось "+totOut+" ("+(d>=0?"+":"")+d+"): "+line.join(", "));
 try{window.SFX&&SFX.play(d>0?"ok":"err")}catch(e){}}
function go(){
 var t=act0();if(!t||!bossLive()||running)return;
 var h=hand(sl);if(!h||locked()||used()>=DAYLIM||!enough())return;
 var bid=t.bid,seq=[];sl.forEach(function(id){for(var i=0;i<STK[sk][1];i++)seq.push(id)});
 var fired={},k=0,step=STK[sk][1]>=10?170:STK[sk][1]>=3?260:340;
 running=true;P.shut(ov);upBtn();
 var snap=sl.slice();
 (function tick(){
  var tt=act0(),alive=tt&&bossLive();
  if(k>=seq.length||!alive||ammo(seq[k])<1){running=false;sl=snap;if(Object.keys(fired).length)pay(fired,bid);else P.toast("Колода не склалася: бій уже скінчився.");upBtn();return}
  var id=seq[k++];
  try{window._nbShoot(WP.BY[id]);fired[id]=(fired[id]||0)+1}catch(e){running=false;upBtn();return}
  setTimeout(tick,step)})()}
function act(k,a){var kk=a.getAttribute("data-k");
 if(k=="stk"){sk=+kk;render();return}
 if(k=="clr"){sl[+kk]=null;render();return}
 if(k=="add"){var i=sl.indexOf(null);if(i<0)i=2;if(ammo(kk)<1){P.toast("Цієї зброї немає. Купи на ринку або добудь у поході.");return}sl[i]=kk;render();return}
 if(k=="gp"){gp=+kk;render();return}
 if(k=="auto"){var t=act0(),r=autoPick(t?t.bid:"");
  if(!r){P.toast("На цю ставку зброї не вистачає навіть на одну руку. Спробуй меншу ставку або докупи зброї.");return}
  sl=r.a.slice();render();if(r.bo<0)P.toast("Зараз найкраще виходить лише «Купа» (мінус). Докупи різної зброї або зменш ставку.");return}
 if(k=="go"){go();return}}
function upBtn(){if(!btn)return;var show=!running&&fightVis()&&bossLive();
 if(!show){btn.style.display="none";return}
 var left=DAYLIM-used();btn.innerHTML='🃏 Колода <small>'+left+'/'+DAYLIM+'</small>';btn.style.display="block";
 var w=document.querySelector("#nbF .wpan"),r=w?w.getBoundingClientRect():null;
 if(r&&r.height){btn.style.left=Math.max(6,r.left+8)+"px";btn.style.top=Math.max(6,r.top-42)+"px";btn.style.right="auto";btn.style.bottom="auto"}
 else{btn.style.right="8px";btn.style.bottom="30%";btn.style.left="auto";btn.style.top="auto"}}
function boot(){ov=P.ov("dzB",act);
 btn=document.createElement("button");btn.id="bcb9";btn.type="button";btn.addEventListener("click",open);document.body.appendChild(btn);
 setInterval(upBtn,450);
 window.D9B={open:open,playedToday:playedToday,state:C,hand:hand,bonus:bonus,fav:fav,HANDS:HANDS,used:used,busy:function(){return running},
  dbg:function(a,s){sl=a;if(s!=null)sk=s;return {h:hand(sl),need:need()}}}}
if(document.readyState=="complete")setTimeout(boot,1000);else window.addEventListener("load",function(){setTimeout(boot,1000)});
})();
