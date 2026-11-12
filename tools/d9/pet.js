(function(){
/* v361: Кіт-питомець (як «Улюбленець» у «Братві і кільці»): годуєш за срібло, він росте й дає три навички. Без сервера. Числа — черновик. */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc,fs=P.fs;
var NAMES=["Мурзик","Пан Котовський","Пампушка","Кіт Баюн","Шельма","Отаман Мурко","Бровко","Тарас Мурченко","Сірко","Мотрона","Кошовий","Булька"];
var FOOD=[["🥛","Молочко",40,10,25],["🌭","Ковбаска",160,45,55],["🐟","Чумацька тараня",600,170,100]];
var SK=[
 {ic:"🐽",n:"Нюх на ніштяки",d:"Частіше знаходить речі для колекцій у поході: +1,5% до шансу на кожному кроці й шанс на ще одну знахідку в кінці."},
 {ic:"🛡",n:"Сторожа хуторів",d:"Бот рідше відбиває твої хутори: кожен ранг зменшує шанс на 17%."},
 {ic:"🎶",n:"Мур-р",d:"Гладиш кота раз на день — отримуєш ⚡. Чим вище ранг, тим більше. З 3-го рангу гладити можна двічі на день."}];
var LVMAX=16,SKMAX=5,BOSS="marena";
function C(){var d=T();if(!d.pet)d.pet={n:0,xp:0,lv:1,sk:[0,0,0],sat:70,at:Date.now(),pat:{d:"",n:0}};var c=d.pet;if(!c.sk)c.sk=[0,0,0];return c}
function need(l){return 30+20*l}
function own(){return !!C().own}
function sat(){var c=C(),now=Date.now();c.sat=Math.max(0,Math.min(100,c.sat-(now-(c.at||now))/36e5*5));c.at=now;return c.sat}
function hungry(){return sat()<20}
function rank(i){var c=C();return !own()||hungry()?0:(c.sk[i]|0)}
function sp(){var c=C();return Math.max(0,c.lv-1-c.sk.reduce(function(a,b){return a+b},0))}
function patMax(){return 1+(rank(2)>=3?1:0)}
function patsLeft(){var c=C(),p=c.pat;if(p.d!==P.day()){p.d=P.day();p.n=0}return Math.max(0,patMax()-p.n)}
function ready(){return own()&&(patsLeft()>0||sp()>0)?1:0}
function addXp(n){var c=C(),up=0;if(c.lv>=LVMAX)return 0;c.xp+=n;while(c.lv<LVMAX&&c.xp>=need(c.lv)){c.xp-=need(c.lv);c.lv++;up++}if(c.lv>=LVMAX)c.xp=0;return up}
var PAT_J=["Мурчить, як трактор без глушника.","Подивився на тебе так, ніби ти йому винен.","Тицьнувся лобом у шаблю й задоволений.","Лизнув вус. Сказав би «дякую», та не вміє.","Залишив на штанах шерсть — на згадку.","Перекинувся на спину: можна чухати, але недовго."];
function rescue(row){var c=C();if(c.own)return false;c.own=1;c.at=Date.now();c.sat=50;
 if(!(c.xp>0||c.lv>1))c.n=Math.floor(Math.random()*NAMES.length);
 P.save();try{P.say("🐈 Ти визволив кота з клітки Марени! Він тепер живе у Скрині.")}catch(e){}return true}
function pat(){var c=C(),l=patsLeft();if(!c.own)return;if(!l){P.say("Кіт сьогодні вже налаштований на «хватить». Приходь завтра.");return}
 if(hungry()){P.say("Голодного кота гладити — тільки образити. Нагодуй спершу.");return}
 c.pat.n++;var e=2+rank(2);P.give({en:e});var up=addXp(5);
 P.toast("Кіт «"+NAMES[c.n%NAMES.length]+"»: "+PAT_J[Math.floor(Math.random()*PAT_J.length)]+" +"+e+" ⚡"+(up?" · Новий рівень!":""));P.save()}
function feed(i){var c=C(),f=FOOD[i];if(!c.own)return;if(sat()>=95){P.say("Кіт ситий і дивиться зверхньо. Зайде ще за годину.");return}
 if((S.sv||0)<f[2]){P.say("Бракує срібла на «"+f[1]+"»: треба "+fs(f[2])+" 🥈. Кіт не їсть у борг.");return}
 S.sv-=f[2];c.sat=Math.min(100,sat()+f[4]);var up=addXp(f[3]);try{draw()}catch(e){}P.save();
 P.toast(f[0]+" Кіт їсть «"+f[1]+"» і муркоче. +"+f[3]+" досвіду"+(up?" · Новий рівень, +1 очко навички!":""))}
function upSk(i){var c=C();if(!c.own)return;if(sp()<=0||c.sk[i]>=SKMAX)return;c.sk[i]++;P.save();P.toast("Навичка «"+SK[i].n+"» — ранг "+c.sk[i])}
function rename(){var c=C();c.n=(c.n+1)%NAMES.length;P.save()}
P.petSk=rank;
P.reg.pet=function(){return ready()};
/* ---- экран ---- */
var ov;
function bar(a,b,cls){var p=Math.max(0,Math.min(100,Math.round(a/b*100)));return '<div class="dzbar'+(cls?' '+cls:'')+'"><i style="width:'+p+'%"></i></div>'}
function lockHTML(){var dev=window.JUNK_DEV&&JUNK_DEV.always;
 return '<div class="dzc"><div class="dzt"><b>🐈 Кіт</b><button data-z="x" aria-label="Закрити">✕</button></div>'+
 '<div class="dzk">'+P.kob(5)+'</div>'+
 '<div class="dzhero"><div class="em dzcat sad">🔒</div><div style="flex:1"><b>Кіт у клітці</b><small>Його тримає відьма Марена для своїх чарів. Така істота — не для кожного.</small></div></div>'+
 '<div class="dzs"><h4>Як отримати</h4><div class="dzrow"><div class="dzn" style="font-size:16px">🧙</div><div class="dzx"><b>Переможи Марену</b><small>Будь-яка ярість, соло чи з відрядом. Після першої перемоги клітка відчиниться, кіт піде з тобою й оселиться у Скрині.</small></div></div>'+
 '<small style="color:#9d8a62;display:block;margin-top:6px">Кіт дає навички: частіші знахідки в поході, захист хуторів і щоденну енергію від гладження.</small></div>'+
 (dev?'<button class="dzb dzbig" data-z="free">🛠 Тест: звільнити кота зараз</button>':'')+'</div>'}
function render(){if(!ov)return;if(!own()){ov.innerHTML=lockHTML();return}
 var c=C(),s=sat(),h="",nm=NAMES[c.n%NAMES.length],pts=sp(),pl=patsLeft();
 h+='<div class="dzc"><div class="dzt"><b>🐈 Кіт</b><button data-z="x" aria-label="Закрити">✕</button></div>';
if(!c.seen)h+='<div class="dzk" style="border-color:#ffd978">🎉 Кіт Марени тепер твій! Він схуд у клітці — нагодуй його й погладь.</div>';
 h+='<div class="dzk">'+(hungry()?'«Голодний кіт не працює — профспілка». Нагодуй його.':P.kob(5))+'</div>';
 h+='<div class="dzhero"><div class="em dzcat'+(hungry()?' sad':'')+'">'+(hungry()?'😿':'🐈')+'</div><div style="flex:1"><b>'+esc(nm)+'</b><small>Рівень '+c.lv+(c.lv>=LVMAX?' (максимум)':'')+'</small>';
 if(c.lv<LVMAX)h+=bar(c.xp,need(c.lv))+'<small style="margin-top:2px">досвід '+c.xp+' / '+need(c.lv)+'</small>';
 h+='<small style="margin-top:4px">Ситість '+Math.round(s)+'%</small>'+bar(s,100,s<20?'low':'')+'</div></div>';
 h+='<div class="dzs"><h4>Годування</h4><div class="dzgrid">';
 FOOD.forEach(function(f,i){h+='<div class="dztile" data-z="feed" data-k="'+i+'"><span>'+f[0]+'</span>'+f[1]+'<small style="display:block;color:#b9a47b;font-weight:400">'+fs(f[2])+' 🥈 · +'+f[3]+' дос.</small></div>'});
 h+='</div><button class="dzb g dzbig'+(pl?'':' off')+'" data-z="pat">Погладити ('+pl+' з '+patMax()+' сьогодні) · +'+(2+rank(2))+' ⚡</button><small style="color:#9d8a62;display:block;margin-top:4px">Гладити — кнопка вище, раз на добу. Голодного кота не погладиш.</small></div>';
 h+='<div class="dzs"><h4>Навички · вільних очок: '+pts+'</h4>';
 SK.forEach(function(k,i){var r=c.sk[i]|0,pips="";for(var j=0;j<SKMAX;j++)pips+=j<r?'●':'○';
  h+='<div class="dzrow"><div class="dzn" style="font-size:16px">'+k.ic+'</div><div class="dzx"><b>'+k.n+' <span style="color:#ffd978;letter-spacing:1px;font-size:12px">'+pips+'</span></b><small>'+k.d+'</small></div>'+(pts>0&&r<SKMAX?'<button class="dzb g" data-z="up" data-k="'+i+'">+1</button>':'')+'</div>'});
 h+='<small style="color:#9d8a62;display:block;margin-top:4px">Очко навички дає кожен новий рівень кота. Навички не працюють, поки кіт голодний.</small></div>';
 h+='<button class="dzb dzbig" data-z="name">Інше ім\'я</button></div>';
 var sc=ov.querySelector(".dzc"),top=sc?sc.scrollTop:0;ov.innerHTML=h;var n=ov.querySelector(".dzc");if(n)n.scrollTop=top}
function open(){render();ov.classList.add("on")}
function act(k,a){var kk=+a.getAttribute("data-k");if(k=="free"){rescue();P.save();render();return}if(own()&&!C().seen){C().seen=1;P.save()}
 if(k=="feed")feed(kk);else if(k=="pat")pat();else if(k=="up")upSk(kk);else if(k=="name")rename();
 render()}
function hook(){var _lw=window.lootWin;if(typeof _lw!="function"||_lw._pt)return;
 var nw=function(t,first,pd){var r=_lw.apply(this,arguments);try{if(r&&t&&t.bid==BOSS&&rescue()&&r.rows)r.rows.push(["🐈 Кіт врятований!","Кіт Марени тепер живе у твоїй Скрині"])}catch(e){}return r};nw._pt=1;window.lootWin=nw}
function boot(){ov=P.ov("dzP",act);hook();setTimeout(hook,3000);setTimeout(hook,6000);setInterval(function(){if(ov&&ov.classList.contains("on"))render()},15000);
 window.D9P={own:own,rescue:rescue,open:open,ready:ready,rank:rank,state:C,sat:sat,feed:feed,pat:pat,up:upSk,sp:sp,SK:SK}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
