(function(){
/* v361: мини-список справ на главном экране, лента событий в бою с боссом, музыка «Гопак» (синтез, по желанию). Без сервера. */
var P=window.D9;if(!P)return;
var esc=P.esc,fs=P.fs;
/* ================= 1. мини-список справ ================= */
var mini;
function visibleMain(){var nav=document.getElementById("nav2");if(!nav||!nav.offsetParent)return false;
 var r=nav.getBoundingClientRect(),e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
 if(!e||!e.closest("#nav2"))return false;
 if(document.documentElement.classList.contains("gdon")||P.anyOpen())return false;
 var app=document.getElementById("app");if(app&&(app.classList.contains("gm")||app.classList.contains("uioff")))return false;
 return true}
function miniPos(){if(!mini)return;
 if(!visibleMain()||!window.D9H){mini.style.display="none";return}
 var tasks=D9H.tasks,k=D9H.state().dd,done=k&&k.p?k.p:{},h="",n=0;
 tasks.forEach(function(t){var d=!!done[t.id];if(d)n++;h+='<i class="'+(d?'d':'')+'" title="'+esc(t.t)+'">'+(d?'✓':t.ic)+'</i>'});
 var extra=0;
 
 try{if(window.D9W&&D9W.ready())extra++}catch(e){}
 try{if(window.D9P&&D9P.ready())extra++}catch(e){}
 try{if(window.D9G&&D9G.ready())extra++}catch(e){}
 mini.innerHTML='<b>Справи '+n+'/'+tasks.length+'</b>'+h+(extra?'<u>🔔 '+extra+'</u>':'');
 var g=document.getElementById("hgear");if(!g){mini.style.display="none";return}
 var r=g.getBoundingClientRect();
 mini.style.display="flex";mini.style.left=Math.max(2,Math.round(r.left+r.width/2-mini.offsetWidth/2))+"px";mini.style.top=Math.round(r.bottom+10)+"px"}
function bootMini(){mini=document.createElement("div");mini.id="mn9";
 mini.addEventListener("click",function(e){e.stopPropagation();if(window.D9H)D9H.open("day")});
 document.body.appendChild(mini);setInterval(miniPos,900);miniPos()}
/* ================= 2. лента событий в бою ================= */
var fd,fdSeen={},fdKey="",hpMark=100,lastHit=0;
function fight(){var nb=document.getElementById("nbF");return !!(nb&&nb.getClientRects().length)}
function line(txt,cls){if(!fd)return;var e=document.createElement("div");e.className="l "+(cls||"");e.textContent=txt;fd.appendChild(e);
 while(fd.children.length>4)fd.removeChild(fd.firstChild);
 setTimeout(function(){e.classList.add("o");setTimeout(function(){e.remove()},700)},5200)}
function fdTick(){try{
 var t=window.btActive&&btActive();
 if(!t||!fight()){fd.style.display="none";return}
 fd.style.display="flex";
 var b=S.bd&&S.bd[t.mode];if(!b||!b.max)return;
 var key=t.mode+"|"+b.end;if(key!==fdKey){fdKey=key;fdSeen={};hpMark=100;fd.innerHTML="";line("⚔ Бій розпочато. «Бий, поки гарячий»","m")}
 if(t.mode=="grp"&&b.fd){Object.keys(b.fd).forEach(function(n){var v=b.fd[n],o=fdSeen[n]||0;if(v>o){fdSeen[n]=v;if(o||true)line("🤝 "+n+" вдарив −"+fs(v-o),"f")}})}
 var p=Math.max(0,b.hp/b.max*100);
 [75,50,25,10].forEach(function(m){if(hpMark>m&&p<=m){hpMark=m;line(m==10?"💀 Бос ледве дихає — добивай!":"📉 Здоров'я боса: "+m+"%","m")}})
}catch(e){}}
function bootFeed(){fd=document.createElement("div");fd.id="fd9";document.body.appendChild(fd);setInterval(fdTick,600);
 /* мої влучання */
 var w=function(){var D=window.DSTAT;if(!D||typeof D.hit!="function"||D.hit._d9)return false;var h=D.hit,n=function(pd,crt,wid){var r=h.apply(this,arguments);try{if(fight()&&pd>0){var now=Date.now();if(now-lastHit>350){lastHit=now;line((crt?"💥 Крит! Ти вдарив −":"🎯 Ти вдарив −")+fs(pd),crt?"c":"y")}}}catch(e){}return r};n._d9=1;D.hit=n;return true};
 if(!w()){var q=setInterval(function(){if(w())clearInterval(q)},1500)}}
/* ================= 3. музыка «Гопак» ================= */
var HK_KEY="hopak",on=false,ac=null,mg=null,tm=0,nextT=0,step=0,noise=null,duckCur;
try{on=localStorage.getItem(HK_KEY)=="1"}catch(e){}
function mv(){var v=.8;try{var q=localStorage.getItem("mvol");if(q!==null&&q!==""&&!isNaN(+q))v=Math.max(0,Math.min(1,+q))}catch(e){}return v}
function duck(){var d=duckCur;return d==null?1:d}
function m2f(m){return 440*Math.pow(2,(m-69)/12)}
/* 8 тактов 2/4 по 8 шістнадцятих: Am Am E E Am Dm E Am */
var CH=[[45,[57,60,64]],[45,[57,60,64]],[40,[56,59,64]],[40,[56,59,64]],[45,[57,60,64]],[38,[57,62,65]],[40,[56,59,64]],[45,[57,60,64]]];
var ML=[[76,0,76,77,76,72,69,0],[72,0,72,74,72,69,64,0],[71,0,71,72,71,68,64,0],[68,71,74,71,76,0,0,0],[76,0,76,77,76,72,69,0],[74,0,74,76,77,74,69,0],[76,0,71,0,68,71,76,0],[69,72,76,81,76,72,69,0]];
function noiseBuf(){if(noise)return noise;var n=ac.sampleRate*.25,b=ac.createBuffer(1,n,ac.sampleRate),d=b.getChannelData(0);for(var i=0;i<n;i++)d[i]=Math.random()*2-1;return noise=b}
function env(g,t,a,pk,dec){g.gain.setValueAtTime(.0001,t);g.gain.linearRampToValueAtTime(pk,t+a);g.gain.exponentialRampToValueAtTime(.0001,t+a+dec)}
function osc(type,f,t,dur,pk,lp){var o=ac.createOscillator(),g=ac.createGain(),fl=ac.createBiquadFilter();o.type=type;o.frequency.setValueAtTime(f,t);fl.type="lowpass";fl.frequency.value=lp||2400;env(g,t,.006,pk,dur);o.connect(fl);fl.connect(g);g.connect(mg);o.start(t);o.stop(t+dur+.05)}
function kick(t){var o=ac.createOscillator(),g=ac.createGain();o.type="sine";o.frequency.setValueAtTime(130,t);o.frequency.exponentialRampToValueAtTime(45,t+.12);env(g,t,.003,.5,.16);o.connect(g);g.connect(mg);o.start(t);o.stop(t+.22)}
function clap(t){var s=ac.createBufferSource(),g=ac.createGain(),f=ac.createBiquadFilter();s.buffer=noiseBuf();f.type="bandpass";f.frequency.value=1800;f.Q.value=.8;env(g,t,.002,.2,.07);s.connect(f);f.connect(g);g.connect(mg);s.start(t,Math.random()*.1);s.stop(t+.12)}
function sched(st,t,sd){var bar=Math.floor(st/8)%8,s=st%8,c=CH[bar],ph=Math.floor(st/64)%2;
 if(s==0||s==4){osc("triangle",m2f(c[0]+(s==4?7:0)),t,sd*3.2,.34,700);kick(t)}
 if(s==2||s==6){c[1].forEach(function(m){osc("sawtooth",m2f(m),t,sd*1.5,.045,1500)});clap(t)}
 var m=ML[bar][s];
 if(m){var mm=m-(ph?12:0),du=sd*(ML[bar][(s+1)%8]?1.7:2.6);osc("sawtooth",m2f(mm),t,du,.15,2600);osc("triangle",m2f(mm+12),t,du*.8,.05,3000);
  if(!ph&&bar%4==3&&s==6){osc("square",m2f(mm+12),t+sd*.5,sd,.04,2200)}}}
function loop(){if(!ac||!mg)return;
 var bpm=138,sd=60/bpm/4,now=ac.currentTime;
 if(nextT<now-.2)nextT=now+.05;
 while(nextT<now+.45){sched(step,nextT,sd);nextT+=sd;step++}}
function wantPlay(){if(!on)return false;if(document.hidden)return false;var a=document.getElementById("app");if(!a||!(a.classList.contains("room")||a.classList.contains("swamp")))return false;
 if(mv()<.001||duck()<.001)return false;
 if(window.VOL===0)return false;return true}
function startH(){if(tm)return;try{ac=window._ac&&window._ac();if(!ac)return;if(ac.state=="suspended")ac.resume();
 mg=ac.createGain();mg.gain.setValueAtTime(0,ac.currentTime);mg.gain.linearRampToValueAtTime(.5*mv()*duck(),ac.currentTime+1.5);mg.connect(ac.destination);
 nextT=ac.currentTime+.1;step=0;tm=setInterval(loop,110);loop()}catch(e){stopH(true)}}
function stopH(now){if(tm){clearInterval(tm);tm=0}
 if(mg){var g=mg;mg=null;try{var t=ac.currentTime;g.gain.cancelScheduledValues(t);g.gain.setValueAtTime(g.gain.value,t);g.gain.linearRampToValueAtTime(0,t+(now?.05:1));setTimeout(function(){try{g.disconnect()}catch(e){}},now?200:1200)}catch(e){}}}
function syncH(){var w=wantPlay();if(w&&!tm){if(ac&&ac.state=="running"||window._ac&&window._ac()&&window._ac().state=="running")startH()}
 else if(!w&&tm)stopH();
 if(tm&&mg){try{mg.gain.setTargetAtTime(.5*mv()*duck(),ac.currentTime,.2)}catch(e){}}}
function setOn(v){on=!!v;try{localStorage.setItem(HK_KEY,on?"1":"0")}catch(e){}
 if(on){try{var c=window._ac&&window._ac();if(c&&c.state=="suspended")c.resume()}catch(e){}}
 paintBtn();syncH()}
var btn;
function paintBtn(){if(!btn)return;btn.innerHTML=on?'🪕 Гопак: <b>ВКЛ</b> — старий мотив вимкнено':'🪕 Гопак: <b>ВИКЛ</b> — грає старий мотив';btn.className="hpk"+(on?" on":"")}
function bootMusic(){
 /* перехват _mduck: старый мотив молчит, пока включён гопак; запись игры (0/1) сохраняется */
 duckCur=window._mduck;
 try{Object.defineProperty(window,"_mduck",{configurable:true,get:function(){return on?0:duckCur},set:function(v){duckCur=v}})}catch(e){}
 var row=document.getElementById("msl");row=row&&row.parentNode;
 if(row&&!document.getElementById("hpk9")){btn=document.createElement("button");btn.id="hpk9";btn.type="button";
  btn.addEventListener("click",function(){setOn(!on)});row.parentNode.insertBefore(btn,row.nextSibling);
  var p=document.createElement("p");p.className="hpkn";p.textContent="«Гопак» — веселий мотив, що грає прямо з коду (без файлів): акордеон, бас, бубон. Гучність — той самий повзунок вище. Не сподобався — натисни ще раз, повернеться старий.";btn.parentNode.insertBefore(p,btn.nextSibling);paintBtn()}
 setInterval(syncH,500);
 ["pointerdown","touchend","click"].forEach(function(ev){window.addEventListener(ev,function(){if(on&&!tm)syncH()},true)});
 window.D9M={on:function(){return on},set:setOn,playing:function(){return !!tm},sync:syncH}}
/* ================= запуск ================= */
function boot(){try{bootMini()}catch(e){window._d9err=e}try{bootFeed()}catch(e){window._d9err=e}try{bootMusic()}catch(e){window._d9err=e}}
if(document.readyState=="complete")setTimeout(boot,1200);else window.addEventListener("load",function(){setTimeout(boot,1200)});
})();
