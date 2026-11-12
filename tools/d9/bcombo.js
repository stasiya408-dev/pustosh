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
function render(){if(!ov)return;var t=act0(),b=t?bossBy(t.bid):null,bid=t?t.bid:"",f=fav(bid),h=hand(sl),left=DAYLIM-used();
 var s='<div class="dzc"><div class="dzt"><b>🃏 Колода</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 s+='<div class="dzk">«'+(b?esc(b.n):"Бос")+' сьогодні любить <b>'+HANDS[f].n+'</b> ('+HANDS[f].d+'). Збереш її — повернеться ще +'+Math.round(FAVB*100)+'%.» — Кобзар</div>';
 s+='<div class="dzs"><h4>1. Скільки на кожне місце</h4><div class="dkw">';
 STK.forEach(function(x,i){s+='<button class="dkt'+(i==sk?' on':'')+'" data-z="stk" data-k="'+i+'"><b>'+x[0]+'</b><small>по '+x[1]+'</small></button>'});
 s+='</div></div>';
 s+='<div class="dzs"><h4>2. Три місця колоди</h4><div class="dkw">';
 for(var i=0;i<3;i++){var w=sl[i];s+='<button class="dkt dks'+(w?' fl':'')+'" data-z="clr" data-k="'+i+'">'+(w?ic(w)+'<small>'+NM[w]+' ×'+STK[sk][1]+'</small>':'<b>'+(i+1)+'</b><small>порожньо</small>')+'</button>'}
 s+='</div></div>';
 s+='<div class="dzs"><h4>3. Зброя (платна)</h4><div class="dkw">';
 PAID.forEach(function(id){var a=ammo(id);s+='<button class="dkt dkw1'+(a<1?' off':'')+'" data-z="add" data-k="'+id+'">'+ic(id)+'<small>'+NM[id]+'</small><small class="dkc">'+a+' шт.</small></button>'});
 s+='</div></div>';
 var tot=STK[sk][1]*3,n=need();
 if(h){var bo=bonus(h,bid),pv=Math.round(tot*(1+bo)),dl=pv-tot;
  s+='<div class="dzhero" style="margin-top:11px"><div class="em">🃏</div><div style="flex:1"><b>'+HANDS[h].n+(h==f?' · слабина боса!':'')+'</b><small>У бій піде '+tot+' пострілів. Повернеться приблизно '+pv+' ('+(dl>=0?'+':'')+dl+', '+(bo>=0?'+':'')+Math.round(bo*100)+'%) тієї самої зброї.</small></div></div>'}
 else s+='<div class="dzx" style="margin-top:10px"><small style="color:#9d8a62">Заповни всі три місця — Кобзар назве руку.</small></div>';
 var why="";
 if(!t||!bossLive())why="Бій із босом зараз не йде.";
 else if(locked())why="Спершу 3 безкоштовні удари (кулак, нога, шабля) — тоді платна зброя відкрита.";
 else if(left<=0)why="Ліміт: "+DAYLIM+" колоди на кожного боса за добу.";
 else if(!h)why="";
 else if(!enough())why="Не вистачає зброї: "+Object.keys(n).filter(function(k){return ammo(k)<n[k]}).map(function(k){return NM[k]+" (треба "+n[k]+", є "+ammo(k)+")"}).join(", ");
 s+='<div style="margin-top:11px;display:flex;gap:8px;align-items:center"><button class="dzb g" style="flex:1;padding:11px" data-z="go"'+((why||!h)?' disabled':'')+'>🃏 Кинути в бій</button></div>';
 s+='<small style="display:block;margin-top:6px;color:#d8996b">'+(why||'')+'</small>';
 s+='<small style="display:block;margin-top:4px;color:#9d8a62">Колод на цього боса сьогодні: '+left+' з '+DAYLIM+'</small>';
 s+='<div class="dzs"><h4>Які бувають руки</h4><div class="dzx"><small>';
 Object.keys(HANDS).forEach(function(k){s+='<b style="color:#ffd978">'+HANDS[k].n+'</b> — '+HANDS[k].d+': '+(HANDS[k].b>=0?'+':'')+Math.round(HANDS[k].b*100)+'%<br>'});
 s+='Усі постріли летять у боса і завдають йому шкоди. Після них на склад повертається та сама зброя — за руку.</small></div></div></div>';
 var sc=ov.querySelector(".dzc"),top=sc?sc.scrollTop:0;ov.innerHTML=s;var nn=ov.querySelector(".dzc");if(nn)nn.scrollTop=top}
function open(){if(running)return;var t=act0();if(!t||!bossLive()){P.toast("Колода грається в бою з босом: зайди в бій.");return}
 sl=[null,null,null];render();ov.classList.add("on")}
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
