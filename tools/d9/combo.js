(function(){
/* v359: «Комбо дня» — угадай порядок ударов (как «быки и коровы»). Одна загадка на сложность в сутки, одинаковая у всех (по дате). Без сервера. Числа — черновик. */
var P=window.D9;if(!P)return;
var T=P.T,esc=P.esc;
var W=[["fist","Дуля","✊"],["foot","Копняк","🦵"],["sabre","Шабля","⚔️"],["dagger","Кинджал","🗡"],["samopal","Самопал","🔫"],["rifle","Рушниця","🔫"],["volley","Залп стріл","🏹"],["cannon","Гармата","💣"]];
var LV=[{n:"Джура",len:3,kinds:5,rep:0,tries:6,rw:{sv:120,en:3}},{n:"Козак",len:4,kinds:6,rep:0,tries:6,rw:{sv:260,junk:3}},{n:"Отаман",len:5,kinds:8,rep:1,tries:7,rw:{sv:520,junk:8,tl:1}}];
function C(){var d=T(),td=P.day();if(!d.cb||d.cb.d!==td)d.cb={d:td,lv:[{g:[],st:0},{g:[],st:0},{g:[],st:0}]};return d.cb}
function pal(l){var r=P.rng(P.day()+"|pal|"+l),a=W.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(r()*(i+1)),t=a[i];a[i]=a[j];a[j]=t}return a.slice(0,LV[l].kinds)}
function sol(l){var r=P.rng(P.day()+"|sol|"+l),p=pal(l).map(function(x){return x[0]}),o=[],c=LV[l];
 if(c.rep){for(var i=0;i<c.len;i++)o.push(p[Math.floor(r()*p.length)])}
 else{var q=p.slice();for(var i2=0;i2<c.len;i2++){var j=Math.floor(r()*q.length);o.push(q.splice(j,1)[0])}}return o}
function fb(s,g){var n=s.length,r=[],left={},i;for(i=0;i<n;i++){if(g[i]==s[i])r[i]=2;else{r[i]=0;left[s[i]]=(left[s[i]]||0)+1}}
 for(i=0;i<n;i++){if(r[i]!=2&&left[g[i]]>0){r[i]=1;left[g[i]]--}}return r}
function ic(id){var e=W.filter(function(x){return x[0]==id})[0],u="";try{u=window.getItemIcon&&getItemIcon("w_"+id)}catch(x){}
 return u?'<img src="'+u+'" alt="" draggable="false">':'<span>'+e[2]+'</span>'}
function nm(id){return W.filter(function(x){return x[0]==id})[0][1]}
var ov,lv=0,sel=[];
function status(){var c=C();return c.lv.map(function(x){return x.st})}
function playedToday(){return status().filter(function(s){return s>0}).length}
function shareText(){var c=C(),L=c.lv[lv],t="Пустошь · Комбо дня ("+LV[lv].n+") "+c.d+"\n";
 var s=sol(lv);L.g.forEach(function(g){t+=fb(s,g).map(function(x){return x==2?"🟩":x==1?"🟨":"⬛"}).join("")+"\n"});
 t+=L.st==1?"Розгадав за "+L.g.length+" з "+LV[lv].tries:"Не розгадав"; return t}
function render(){if(!ov)return;var c=C(),L=c.lv[lv],cf=LV[lv],s=sol(lv),h="";
 h+='<div class="dzc"><div class="dzt"><b>🧩 Комбо дня</b><button data-z="x" aria-label="Закрити">✕</button></div>';
 h+='<div class="dzk">Писар переплутав порядок ударів, яким козак вклав ворога. Підбери послідовність — зелений: удар на своєму місці, жовтий: удар є, але не тут.</div>';
 h+='<div class="dztabs">'+LV.map(function(x,i){var st=c.lv[i].st;return '<button data-z="lv" data-k="'+i+'" class="'+(lv==i?'on':'')+'">'+(st==1?'✅ ':st==2?'❌ ':'')+x.n+'</button>'}).join("")+'</div>';
 h+='<div class="dzx"><small>'+cf.len+' ударів · '+cf.kinds+' видів зброї · '+(cf.rep?'удари можуть повторюватись':'без повторів')+' · спроб: '+cf.tries+' · нагорода: '+P.rewTxt(cf.rw)+'</small></div>';
 L.g.forEach(function(g){var r=fb(s,g);h+='<div class="dzslots">'+g.map(function(id,i){return '<div class="dzsl f '+(r[i]==2?'g':r[i]==1?'y':'n')+'">'+ic(id)+'</div>'}).join("")+'</div>'});
 if(L.st==0){
  h+='<div class="dzslots">';for(var i=0;i<cf.len;i++){h+='<div class="dzsl'+(sel[i]?' f':'')+'" data-z="slot" data-k="'+i+'">'+(sel[i]?ic(sel[i]):'')+'</div>'}h+='</div>';
  h+='<div class="dzpal">'+pal(lv).map(function(x){var use=!cf.rep&&sel.indexOf(x[0])>=0;return '<div class="dzsl'+(use?' use':'')+'" data-z="pick" data-k="'+x[0]+'">'+ic(x[0])+'<small>'+x[1]+'</small></div>'}).join("")+'</div>';
  var ok=sel.filter(function(x){return x}).length==cf.len;
  h+='<button class="dzb g dzbig'+(ok?'':' off')+'" data-z="hit">Ударити ('+(cf.tries-L.g.length)+' спроб)</button>'}
 else{
  h+='<div class="dzx" style="text-align:center;margin-top:6px"><b>'+(L.st==1?'Розгадано за '+L.g.length+' з '+cf.tries+'!':'Не вийшло. Правильно було:')+'</b></div>';
  if(L.st==2)h+='<div class="dzslots">'+s.map(function(id){return '<div class="dzsl f g">'+ic(id)+'</div>'}).join("")+'</div>';
  h+='<button class="dzb dzbig" data-z="share">Поділитись результатом</button>'}
 h+='<small style="display:block;margin-top:8px;color:#9d8a62">Нова загадка через '+P.fmtLeft(P.msToDayEnd())+' · однакова для всіх козаків.</small></div>';
 var sc=ov.querySelector(".dzc"),top=sc?sc.scrollTop:0;ov.innerHTML=h;var n=ov.querySelector(".dzc");if(n)n.scrollTop=top}
function open(l){if(typeof l=="number")lv=l;else{var st=status();lv=st[0]==0?0:st[1]==0?1:st[2]==0?2:lv}sel=[];render();ov.classList.add("on")}
function act(k,a){var kk=a.getAttribute("data-k"),c=C(),L=c.lv[lv],cf=LV[lv];
 if(k=="lv"){lv=+kk;sel=[];render();return}
 if(k=="slot"){sel[+kk]=null;render();return}
 if(k=="pick"){if(L.st)return;if(!cf.rep&&sel.indexOf(kk)>=0)return;var i=0;while(i<cf.len&&sel[i])i++;if(i>=cf.len)return;sel[i]=kk;render();return}
 if(k=="hit"){if(L.st||sel.filter(function(x){return x}).length!=cf.len)return;var g=sel.slice(0,cf.len);L.g.push(g);var s=sol(lv),r=fb(s,g);sel=[];
  if(r.every(function(x){return x==2})){L.st=1;var left=cf.tries-L.g.length,rw={};Object.keys(cf.rw).forEach(function(q){rw[q]=cf.rw[q]});rw.sv=(rw.sv||0)+left*20;P.cnt("cmbw");P.give(rw);P.toast("Комбо розгадано! "+P.rewTxt(rw))}
  else if(L.g.length>=cf.tries){L.st=2;P.save();P.say("Комбо не розгадано. Писар розводить руками.")}
  else P.save();
  render();return}
 if(k=="share"){var t=shareText();try{navigator.clipboard&&navigator.clipboard.writeText(t).catch(function(){})}catch(e){}
  try{var u="https://t.me/share/url?url="+encodeURIComponent(location.origin+location.pathname)+"&text="+encodeURIComponent(t);if(window.Telegram&&Telegram.WebApp&&Telegram.WebApp.openTelegramLink)Telegram.WebApp.openTelegramLink(u);else window.open(u,"_blank")}catch(e){}
  P.say("Результат скопійовано, лишилось вставити друзям.");return}}
function boot(){ov=P.ov("dzK",act);window.D9K={open:open,status:status,playedToday:playedToday,sol:sol,fb:fb,pal:pal,LV:LV}}
if(document.readyState=="complete")setTimeout(boot,900);else window.addEventListener("load",function(){setTimeout(boot,900)});
})();
