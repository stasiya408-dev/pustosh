(function(){
/* v365: путівник, дві частини смужки (боти/ти), підказки «скільки штурмів ще», штурм ×5, чесний рядок про ботів. v361: «Облога» — недельная фортеця. Козаки-боти (честно подписаны) бьють її самі до ~60%, решту маєш добити ти. Штурм −3 ⚡. Нагороди на 25/50/75/100%. Без сервера. Числа — чернетка. */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc,fs=P.fs;
var COST=3,BOTSHARE=.6,NEEDME=.03,FORTS=[["Чорна вежа","🏰"],["Лядський замок","🏯"],["Татарський острог","🛖"],["Фортеця Круків","🗼"],["Брама Пекла","⛩"],["Цитадель Хмеля","🏛"]];
var MS=[[.25,{sv:1500,junk:3}],[.5,{sv:3000,tl:1,junk:6}],[.75,{sv:5000,tl:2,junk:8}],[1,{sv:9000,tl:5,junk:15,en:10}]];
var BN=["Грицько Мотика","Оксана Сіркова","Тарас Кривий","Мирон Ворон","Явтух Бузько","Горпина Остапівна","Левко Шаблюка","Ганна Нестримна","Панас Чуб","Мотря Гопак","Катря Вишиванка","Семен Півень"];
function unit(){return 30+(S.pw||0)*.04+(S.lv||1)*2}
function Wk(){var d=T(),w=P.week();
 if(!d.sg||d.sg.w!==w){
  var old=d.sg,note="";
  if(old&&old.dm>=old.hp*NEEDME){var tot=0,rw={sv:0,tl:0,junk:0,en:0},fr=(old.dm+botDone(old,1))/old.hp;
   MS.forEach(function(m,i){if(fr>=m[0]&&!old.c[i]){old.c[i]=1;["sv","tl","junk","en"].forEach(function(k){rw[k]+=m[1][k]||0});tot++}});
   if(tot){P.addCarry(rw);note="Минулого тижня «"+FORTS[old.f%FORTS.length][0]+"»: "+tot+" нагород чекають у Літописі (Справи): "+P.rewTxt(rw)}}
  var u=unit();d.sg={w:w,f:w%FORTS.length,hp:Math.round(u*150),u:u,dm:0,c:[0,0,0,0],n:0,log:[],note:note};P.save()}
 return d.sg}
function botDone(s,fin){var f=fin?1:1-P.msToWeekEnd()/(7*864e5);return Math.round(s.hp*BOTSHARE*Math.max(0,Math.min(1,f)))}
function total(s){return Math.min(s.hp,s.dm+botDone(s))}
function frac(s){return total(s)/s.hp}
function claimable(){var s=Wk();if(s.dm<s.hp*NEEDME)return 0;var f=frac(s),n=0;MS.forEach(function(m,i){if(f>=m[0]&&!s.c[i])n++});return n}
function ready(){return claimable()}
P.reg.siege=ready;
/* ---- действия ---- */
var JOK=["Ядро влучило в браму. Брама образилась.","Влучно! Хтось із ворогів прикинувся мертвим.","Бах! Комендант сховався під столом.","Вежа затремтіла, як тесть на весіллі.","Козацький лист доставлено: «Відчиняй, гади»."];
var AVG=1.12;/* середня шкода штурму з урахуванням критів (12% × 2) */
function avgHit(s){return Math.max(1,s.u*AVG)}
function needMe(s,m){return Math.max(NEEDME,m-BOTSHARE)}/* яка частка фортеці має бути від тебе до кінця тижня */
function strikesFor(s,part){return Math.max(0,Math.ceil((part*s.hp-s.dm)/avgHit(s)))}
function weekElapsed(){return 7*864e5-P.msToWeekEnd()}
function botsAt(m){return Math.max(0,m/BOTSHARE*7*864e5-weekElapsed())}/* через скільки боти самі дійдуть до m */
var gp=-1;
/* ---- действия ---- */
function hit(s){var crit=Math.random()<.12,dm=Math.round(s.u*(.8+Math.random()*.4)*(crit?2:1));
 s.dm+=dm;s.n++;s.log.push((crit?"💥 Крит! ":"⚔ ")+"−"+fs(dm)+" · "+JOK[Math.floor(Math.random()*JOK.length)]);if(s.log.length>5)s.log=s.log.slice(-5);
 P.cnt("sgn");return crit}
function assault(times){var s=Wk(),n=times||1;
 if(frac(s)>=1){P.say("Фортеця вже взята. Дочекайся наступного тижня.");return}
 if((S.en||0)<COST){P.say("Бракує енергії на штурм: треба "+COST+" ⚡.");return}
 var did=0,crit=false,before=s.dm;
 while(did<n&&(S.en||0)>=COST&&frac(s)<1){S.en-=COST;if(hit(s))crit=true;did++}
 try{draw()}catch(e){}
 if(did>1){s.log=s.log.slice(0,-1);s.log.push("⚔ Серія з "+did+" штурмів: −"+fs(s.dm-before))}
 P.save();try{window.SFX&&SFX.play(crit?"boom":"slash")}catch(e){}
 var c=ov&&ov.querySelector(".dzfort");if(c){c.classList.remove("dzshk");void c.offsetWidth;c.classList.add("dzshk")}
 if(frac(s)>=1)P.toast("Фортеця «"+FORTS[s.f%FORTS.length][0]+"» узята! Забери нагороду.");
 render()}
function claim(i){var s=Wk();if(s.dm<s.hp*NEEDME){P.say("Щоб брати нагороди, вдар по фортеці хоч на "+Math.round(NEEDME*100)+"% її міцності сам.");return}
 if(s.c[i]||frac(s)<MS[i][0])return;s.c[i]=1;P.give(MS[i][1]);P.toast("Облога: "+P.rewTxt(MS[i][1]));render()}
/* ---- путівник ---- */
function msTable(){var h='<div class="dkh">';
 MS.forEach(function(m){h+='<div><b>'+Math.round(m[0]*100)+'% фортеці</b><small>'+P.rewTxt(m[1])+'</small></div>'});return h+'</div>'}
var GUIDE=[
 {t:"Що це і навіщо",b:function(){return ''+
  '<p>Щотижня (з понеділка до неділі) з’являється <b>одна фортеця</b> — спільна ціль тижня. У неї є «міцність» (HP). Мета: <b>зруйнувати її до кінця тижня</b>.</p>'+
  '<p>Руйнують її <b>двоє</b>: <b>🤖 козаки-боти</b> (самі, поволі, рівномірно за тиждень — до 60% міцності) і <b>ти</b> (штурмами за ⚡).</p>'+
  '<div class="dzhero"><div class="em">🏰</div><div style="flex:1"><b>Навіщо це тобі</b><small>За кожен рубіж (25%, 50%, 75%, 100%) дають нагороду: срібло, талери, мотлох, енергію. Чим більше зруйновано — тим краща.</small></div></div>'+
  '<p><b>Чесно про ботів.</b> Це умовні козаки, що імітують допомогу друзів. Живі гравці з’являться, коли буде сервер. Поки що боти — просто «фон», який бере на себе перші 60%.</p>'}},
 {t:"Твій штурм",b:function(){var s=Wk();return ''+
  '<p>Один штурм коштує <b>'+COST+' ⚡</b>. Шкода залежить від твого <b>рівня</b> і <b>сили</b> (чим більше — тим сильніше б’єш). Розкид ±20%, а у 12% випадків — <b>крит ×2</b>.</p>'+
  '<p>Силу удару гра <b>фіксує на початку тижня</b>. Зараз це ≈ <b>'+fs(Math.round(s.u))+'</b> за штурм, а вся фортеця має <b>'+fs(s.hp)+'</b>.</p>'+
  '<div class="dzhero"><div class="em">⚔</div><div style="flex:1"><b>У цифрах</b><small>Один штурм ≈ 0,7% фортеці. Щоб зняти 10% — близько 15 штурмів (≈45 ⚡).</small></div></div>'+
  '<p>Є кнопка <b>«Штурм ×5»</b> — п’ять ударів підряд за раз (15 ⚡), щоб не тицяти по сто разів.</p>'}},
 {t:"Нагороди і твоя частка",b:function(){var s=Wk(),h='<p>Чотири рубежі:</p>'+msTable();
  h+='<p style="margin-top:9px"><b>Головне правило.</b> Щоб <b>брати</b> нагороди, ти маєш сам нанести <b>не менше '+Math.round(NEEDME*100)+'%</b> міцності (≈'+strikesFor({hp:s.hp,dm:0,u:s.u},NEEDME)+' штурмів, ≈'+strikesFor({hp:s.hp,dm:0,u:s.u},NEEDME)*COST+' ⚡). Без цього навіть повна смужка нагород не дасть.</p>';
  h+='<p><b>Що роблять боти:</b> до 25% і 50% вони дойдуть <b>самі</b> (25% — приблизно в четвер, 50% — близько суботи), тобі треба лише свої '+Math.round(NEEDME*100)+'%.</p>';
  h+='<p>До <b>75%</b> боти <b>самі не дістануть</b> — решту (≥'+Math.round(needMe(s,.75)*100)+'% тобі) добиваєш ти. А для <b>100%</b> від тебе треба ≥'+Math.round(needMe(s,1)*100)+'% — це ≈'+strikesFor({hp:s.hp,dm:0,u:s.u},needMe(s,1))+' штурмів, ≈'+strikesFor({hp:s.hp,dm:0,u:s.u},needMe(s,1))*COST+' ⚡ за тиждень.</p>';
  h+='<p><b>Не встиг забрати?</b> Коли тиждень закінчується, усе, що вже було досягнуто, <b>видається само</b> (якщо в тебе було ≥'+Math.round(NEEDME*100)+'%).</p>';
  return h}}];
function guideHtml(){var g=GUIDE[gp],n=GUIDE.length;
 var s='<div class="dzc"><div class="dzt"><b>📖 Путівник · '+(gp+1)+'/'+n+'</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 s+='<div class="dkg"><h3>'+g.t+'</h3>'+g.b()+'</div>';
 s+='<div class="dkdots">';for(var i=0;i<n;i++)s+='<i class="'+(i==gp?'on':'')+'"></i>';s+='</div>';
 s+='<div style="display:flex;gap:8px;margin-top:10px">';
 s+=(gp>0?'<button class="dzb" style="flex:1;padding:11px" data-z="gp" data-k="'+(gp-1)+'">◀ Назад</button>':'<button class="dzb" style="flex:1;padding:11px" data-z="gp" data-k="-1">Пропустити</button>');
 s+=(gp<n-1?'<button class="dzb g" style="flex:1;padding:11px" data-z="gp" data-k="'+(gp+1)+'">Далі ▶</button>':'<button class="dzb g" style="flex:1;padding:11px" data-z="gp" data-k="-1">Зрозуміло</button>');
 return s+'</div></div>'}
/* ---- что делать дальше ---- */
function nextStep(s,f,mine){
 if(f>=1)return "Фортеця взята! Забери нагороди, які ще не взяв, і чекай наступного тижня ("+P.fmtLeft(P.msToWeekEnd())+").";
 if(claimable()>0)return "Є нагорода! Натисни «Забрати» нижче.";
 if(mine<NEEDME){var k=strikesFor(s,NEEDME);return "Крок 1: нанеси сам хоч "+Math.round(NEEDME*100)+"% — ще "+k+" "+(k==1?"штурм":"штурмів")+" (≈"+k*COST+" ⚡). Без цього нагороди не видають."}
 for(var i=0;i<MS.length;i++){if(s.c[i])continue;
  if(f>=MS[i][0])continue;
  var need=needMe(s,MS[i][0]),k2=strikesFor(s,need),bt=MS[i][0]<=BOTSHARE?botsAt(MS[i][0]):0;
  var t="Наступна нагорода — "+Math.round(MS[i][0]*100)+"% фортеці. ";
  if(bt>0)t+="Боти самі дойдуть приблизно через "+P.fmtLeft(bt)+"; можна прискорити своїми штурмами. ";
  else if(k2>0)t+="Від тебе до кінця тижня потрібно ще ≈"+k2+" штурмів (≈"+k2*COST+" ⚡). ";
  if((S.en||0)<COST)t+="Зараз бракує енергії.";
  return t}
 return "Усі рубежі досягнуто. Дочекайся кінця тижня — решту нагород видадуть самі."}
/* ---- экран ---- */
var ov;
function render(){if(!ov)return;
 if(gp>=0){ov.innerHTML=guideHtml();var n0=ov.querySelector(".dzc");if(n0)n0.scrollTop=0;return}
 var s=Wk(),f=frac(s),mine=s.dm/s.hp,bf=Math.min(1-0,botDone(s)/s.hp),fo=FORTS[s.f%FORTS.length],h="";
 var myw=Math.max(0,Math.min(f-bf,1-bf));
 h+='<div class="dzc"><div class="dzt"><b>🏰 Облога</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 if(s.note)h+='<div class="dzrow cu"><div class="dzn">🎁</div><div class="dzx"><small>'+esc(s.note)+'</small></div></div>';
 h+='<div class="dzk">«Фортеця стоїть — отже, ще не прийшли ми». Цього тижня облягаємо «'+fo[0]+'».</div>';
 h+='<div class="dzhero"><div class="em dzfort">'+(f>=1?'🚩':fo[1])+'</div><div style="flex:1"><b>'+fo[0]+'</b><small>'+(f>=1?'Взята! Хоругва над брамою.':'Міцність: '+fs(Math.max(0,s.hp-total(s)))+' з '+fs(s.hp))+'</small>'+
  '<div class="dzbar sg2"><i class="b" style="width:'+(bf*100).toFixed(1)+'%"></i><i class="m" style="width:'+(myw*100).toFixed(1)+'%"></i><u style="left:25%"></u><u style="left:50%"></u><u style="left:75%"></u></div>'+
  '<small style="margin-top:3px">Взято '+Math.round(f*100)+'% · до кінця тижня '+P.fmtLeft(P.msToWeekEnd())+'</small></div></div>';
 h+='<div class="dzchips"><span class="sgb">🤖 Боти: '+Math.round(bf*100)+'% <em>(самі, до '+Math.round(BOTSHARE*100)+'%)</em></span><span class="sgm">🎯 Ти: '+(mine*100).toFixed(1).replace(".0","")+'% <em>('+(mine>=NEEDME?'✓ нагороди відкриті':'потрібно ≥'+Math.round(NEEDME*100)+'%')+')</em></span><span>Штурмів: '+s.n+'</span></div>';
 h+='<div class="dzk" style="margin-top:8px;font-style:normal">👉 '+esc(nextStep(s,f,mine))+'</div>';
 h+='<div style="display:flex;gap:8px"><button class="dzb g dzbig'+(f>=1?' off':'')+'" style="flex:2;margin-top:6px" data-z="hit">Штурм · −'+COST+' ⚡ · ≈'+fs(Math.round(s.u))+'</button>'+
  '<button class="dzb dzbig'+(f>=1?' off':'')+'" style="flex:1;margin-top:6px;font-size:13px" data-z="hit5">×5 · −'+COST*5+' ⚡</button></div>';
 h+='<button class="dzb dkhelp" style="width:100%;margin-top:7px" data-z="gp" data-k="0">📖 Як це працює? Путівник</button>';
 if(s.log.length){h+='<div class="dzlog" style="text-align:left">';s.log.slice().reverse().forEach(function(l){h+='<div>'+esc(l)+'</div>'});h+='</div>'}
 h+='<div class="dzs"><h4>Нагороди за облогу</h4>';
 MS.forEach(function(m,i){var ok=f>=m[0],got=s.c[i],can=ok&&!got&&mine>=NEEDME,nm=needMe(s,m[0]),k=strikesFor(s,nm),sub;
  if(got)sub='Отримано';
  else if(ok&&mine<NEEDME){var k3=strikesFor(s,NEEDME);sub='Рубіж досягнуто, але ти вдарив мало: ще '+k3+' шт. (≈'+k3*COST+' ⚡), щоб брати'}
  else if(ok)sub='Готово — можна забрати';
  else{sub='Від тебе до кінця тижня ≥'+Math.round(nm*100)+'%'+(k>0?' · ще ≈'+k+' шт. (≈'+k*COST+' ⚡)':' · вже достатньо');
   if(m[0]<=BOTSHARE){var bt=botsAt(m[0]);if(bt>0)sub+=' · боти самі: через ~'+P.fmtLeft(bt)}else sub+=' · боти самі не дойдуть'}
  h+='<div class="dzrow'+(got?' dn':(can?' cu':''))+'"><div class="dzn">'+(got?'✓':Math.round(m[0]*100)+'')+'</div><div class="dzx"><b>'+Math.round(m[0]*100)+'% фортеці</b><small>'+P.rewTxt(m[1])+'</small><small style="color:#bfa77a">'+esc(sub)+'</small></div>'+(got?'<span style="color:#8fcf7a">✓</span>':(can?'<button class="dzb g" data-z="cl" data-k="'+i+'">Забрати</button>':'<span style="color:#9d8a62">'+(ok?'🔒':'')+'</span>'))+'</div>'});
 h+='<small style="color:#9d8a62;display:block;margin-top:4px">Не встиг забрати до кінця тижня — усе досягнуте видасться само (якщо в тебе ≥'+Math.round(NEEDME*100)+'%).</small></div>';
 h+='<div class="dzs"><small style="color:#9d8a62;display:block">🤖 Козаки-боти умовні: вони імітують допомогу друзів. Живі гравці з’являться, коли буде сервер.</small></div></div>';
 var sc=ov.querySelector(".dzc"),tp=sc?sc.scrollTop:0;ov.innerHTML=h;var n=ov.querySelector(".dzc");if(n)n.scrollTop=tp}
function open(){var d=T();if(!d.sgSeen){d.sgSeen=1;gp=0;P.save()}else gp=-1;render();ov.classList.add("on")}
function act(k,a){var kk=+a.getAttribute("data-k");
 if(k=="hit")assault(1);else if(k=="hit5")assault(5);else if(k=="cl")claim(kk);else if(k=="gp"){gp=kk;render()}}
function boot(){ov=P.ov("dzG",act);
 window.D9G={open:open,ready:ready,state:Wk,assault:assault,claim:claim,frac:function(){return frac(Wk())},MS:MS}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
