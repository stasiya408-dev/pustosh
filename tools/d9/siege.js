(function(){
/* v361: «Облога» — недельная фортеця. Козаки-боти (честно подписаны) бьють її самі до ~60%, решту маєш добити ти. Штурм −3 ⚡. Нагороди на 25/50/75/100%. Без сервера. Числа — чернетка. */
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
   if(tot){P.give(rw);note="Минулого тижня «"+FORTS[old.f%FORTS.length][0]+"»: автоматично забрано "+tot+" нагород: "+P.rewTxt(rw)}}
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
function assault(){var s=Wk();if(frac(s)>=1){P.say("Фортеця вже взята. Дочекайся наступного тижня.");return}
 if((S.en||0)<COST){P.say("Бракує енергії на штурм: треба "+COST+" ⚡.");return}
 S.en-=COST;try{draw()}catch(e){}
 var crit=Math.random()<.12,dm=Math.round(s.u*(.8+Math.random()*.4)*(crit?2:1));
 s.dm+=dm;s.n++;s.log.push((crit?"💥 Крит! ":"⚔ ")+"−"+fs(dm)+" · "+JOK[Math.floor(Math.random()*JOK.length)]);if(s.log.length>5)s.log=s.log.slice(-5);
 P.cnt("sgn");P.save();try{window.SFX&&SFX.play(crit?"boom":"slash")}catch(e){}
 var c=ov&&ov.querySelector(".dzfort");if(c){c.classList.remove("dzshk");void c.offsetWidth;c.classList.add("dzshk")}
 if(frac(s)>=1)P.toast("Фортеця «"+FORTS[s.f][0]+"» узята! Забери нагороду.");
 render()}
function claim(i){var s=Wk();if(s.dm<s.hp*NEEDME){P.say("Щоб брати нагороди, вдар по фортеці хоч на "+Math.round(NEEDME*100)+"% її міцності самому.");return}
 if(s.c[i]||frac(s)<MS[i][0])return;s.c[i]=1;P.give(MS[i][1]);P.toast("Облога: "+P.rewTxt(MS[i][1]));render()}
/* ---- экран ---- */
var ov;
function render(){if(!ov)return;var s=Wk(),f=frac(s),mine=s.dm/s.hp,fo=FORTS[s.f%FORTS.length],h="";
 var r=P.rng("sgb|"+s.w+"|"+Math.floor(Date.now()/36e5)),top=[];for(var i=0;i<4;i++)top.push(BN[Math.floor(r()*BN.length)]);
 h+='<div class="dzc"><div class="dzt"><b>🏰 Облога</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 if(s.note)h+='<div class="dzrow cu"><div class="dzn">🎁</div><div class="dzx"><small>'+esc(s.note)+'</small></div></div>';
 h+='<div class="dzk">«Фортеця стоїть — отже, ще не прийшли ми». Цього тижня облягаємо «'+fo[0]+'».</div>';
 h+='<div class="dzhero"><div class="em dzfort">'+(f>=1?'🚩':fo[1])+'</div><div style="flex:1"><b>'+fo[0]+'</b><small>'+(f>=1?'Взята! Хоругва над брамою.':'Міцність: '+fs(Math.max(0,s.hp-total(s)))+' з '+fs(s.hp))+'</small>'+
  '<div class="dzbar"><i style="width:'+Math.round(f*100)+'%"></i></div><small style="margin-top:3px">Взято '+Math.round(f*100)+'% · до кінця тижня '+P.fmtLeft(P.msToWeekEnd())+'</small></div></div>';
 h+='<div class="dzchips"><span>🤖 Козаки-боти: '+fs(botDone(s))+'</span><span>🎯 Ти: '+fs(s.dm)+' ('+Math.round(mine*100)+'%)</span><span>Штурмів: '+s.n+'</span></div>';
 h+='<button class="dzb g dzbig'+(f>=1?' off':'')+'" data-z="hit">Штурм · −'+COST+' ⚡ · ≈'+fs(Math.round(s.u))+' шкоди</button>';
 if(s.log.length){h+='<div class="dzlog" style="text-align:left">';s.log.slice().reverse().forEach(function(l){h+='<div>'+esc(l)+'</div>'});h+='</div>'}
 h+='<div class="dzs"><h4>Нагороди за облогу</h4>';
 MS.forEach(function(m,i){var ok=f>=m[0],got=s.c[i],can=ok&&!got&&mine>=NEEDME;
  h+='<div class="dzrow'+(got?' dn':(can?' cu':''))+'"><div class="dzn">'+(got?'✓':Math.round(m[0]*100)+'')+'</div><div class="dzx"><b>'+Math.round(m[0]*100)+'% фортеці</b><small>'+P.rewTxt(m[1])+'</small></div>'+(got?'<span style="color:#8fcf7a">✓</span>':(ok?(mine>=NEEDME?'<button class="dzb g" data-z="cl" data-k="'+i+'">Забрати</button>':'<small style="color:#e1a98f;max-width:90px">треба й твій удар</small>'):''))+'</div>'});
 h+='<small style="color:#9d8a62;display:block;margin-top:4px">Боти-козаки б\'ють фортецю самі приблизно до '+Math.round(BOTSHARE*100)+'%, решту має доробити ти. Щоб брати нагороди, треба нанести хоча б '+Math.round(NEEDME*100)+'% загальної міцності особисто. Невзяті нагороди з минулого тижня автоматично видаються, коли настає новий.</small></div>';
 h+='<div class="dzs"><h4>Хто штурмує з тобою <span style="text-transform:none;letter-spacing:0;font-weight:400;color:#9d8a62">(боти, живі люди — із сервером)</span></h4>';
 top.forEach(function(n,i){var q=Math.round(botDone(s)/(4+i)*(.9+r()*.2));h+='<div class="dzrow" style="padding:5px 9px;margin-bottom:4px"><div class="dzx"><small style="color:#e8d6ab"><b style="display:inline;font-size:12px">'+esc(n)+'</b> завдав '+fs(q)+' шкоди</small></div></div>'});
 h+='</div></div>';
 var sc=ov.querySelector(".dzc"),tp=sc?sc.scrollTop:0;ov.innerHTML=h;var n=ov.querySelector(".dzc");if(n)n.scrollTop=tp}
function open(){render();ov.classList.add("on")}
function act(k,a){var kk=+a.getAttribute("data-k");if(k=="hit")assault();else if(k=="cl")claim(kk)}
function boot(){ov=P.ov("dzG",act);
 window.D9G={open:open,ready:ready,state:Wk,assault:assault,claim:claim,frac:function(){return frac(Wk())},MS:MS}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
