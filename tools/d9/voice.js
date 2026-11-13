/* d9gv v374: голос Діда Охріма — бормотання при появі хмарки + кнопка «прочитати вголос» (Web Speech, uk-UA).
   Гучність = VOL × SFXVOL. Нічого не вантажить, файлів немає. */
(function(){
var cl=null,last="",busy=0,spk=0;
function vol(){var v=(typeof window.VOL==="number"?window.VOL:1),s=(typeof window.SFXVOL==="number"?window.SFXVOL:1);return Math.min(1,v)*s}
function ctx(){try{return window._ac&&window._ac()}catch(e){return null}}
/* бормотання: серія низьких «бу-бу» зі зміною висоти, довжина від довжини тексту */
function mumble(txt){
 var A=ctx(),V=vol();if(!A||V<=0.01)return;
 try{if(A.state==="suspended")A.resume()}catch(e){}
 var n=Math.max(4,Math.min(16,Math.round((txt||"").length/7)));
 var t=A.currentTime+.02,base=105+Math.random()*18;
 var g=A.createGain();g.gain.value=1;g.connect(A.destination);
 for(var i=0;i<n;i++){
  var f=base*(0.85+Math.random()*.5),d=.075+Math.random()*.05;
  var o=A.createOscillator(),fl=A.createBiquadFilter(),e=A.createGain();
  o.type="sawtooth";o.frequency.setValueAtTime(f,t);o.frequency.linearRampToValueAtTime(f*(0.8+Math.random()*.35),t+d);
  fl.type="bandpass";fl.Q.value=4;fl.frequency.setValueAtTime(380+Math.random()*320,t);fl.frequency.linearRampToValueAtTime(520+Math.random()*420,t+d);
  e.gain.setValueAtTime(0,t);e.gain.linearRampToValueAtTime(.2*V,t+.02);e.gain.linearRampToValueAtTime(0,t+d);
  o.connect(fl);fl.connect(e);e.connect(g);o.start(t);o.stop(t+d+.02);
  t+=d+.03+(Math.random()<.2?.09:0);
 }
}
function txtOf(){if(!cl)return"";var a=cl.querySelector(".gdt"),b=cl.querySelector(".gdx");return((a?a.textContent+". ":"")+(b?b.textContent:"")).replace(/\s+/g," ").trim()}
function speak(){
 var T=txtOf();if(!T)return;
 if(!window.speechSynthesis||!window.SpeechSynthesisUtterance){if(window.say)window.say("На цьому телефоні немає голосу");return}
 try{
  var ss=window.speechSynthesis;
  if(spk){ss.cancel();spk=0;paint();return}
  var u=new SpeechSynthesisUtterance(T);u.lang="uk-UA";u.rate=.88;u.pitch=.6;u.volume=Math.max(.3,vol());
  var vs=ss.getVoices()||[];for(var i=0;i<vs.length;i++){if(/^uk/i.test(vs[i].lang)){u.voice=vs[i];break}}
  u.onend=u.onerror=function(){spk=0;paint()};
  spk=1;ss.cancel();ss.speak(u);paint();
 }catch(e){spk=0}
}
function paint(){var b=cl&&cl.querySelector(".gdsp");if(b)b.classList.toggle("on",!!spk)}
function sync(){
 if(!cl||busy)return;
 busy=1;
 try{
  var bt=cl.querySelector(".gdbt");
  if(bt&&!bt.querySelector(".gdsp")){
   var b=document.createElement("button");b.className="gdsp";b.type="button";b.setAttribute("aria-label","Прочитати вголос");
   b.innerHTML="🔊";b.addEventListener("click",function(e){e.stopPropagation();speak()});
   bt.insertBefore(b,bt.firstChild);paint();
  }
  var T=txtOf();
  if(cl.classList.contains("on")&&T&&T!==last){last=T;try{window.speechSynthesis&&window.speechSynthesis.cancel()}catch(e){}spk=0;mumble(T)}
  if(!cl.classList.contains("on"))last="";
 }catch(e){}
 if(window.MutationObserver)try{mo.takeRecords()}catch(e){}
 busy=0;
}
var mo=null;
function init(){
 cl=document.getElementById("gdc");
 if(!cl){setTimeout(init,700);return}
 var st=document.createElement("style");
 st.textContent="#gdc .gdbt .gdsp{width:34px;height:34px;padding:0;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0}#gdc .gdbt .gdsp .ig{width:18px;height:18px}#gdc .gdbt .gdsp.on{box-shadow:0 0 12px rgba(255,200,80,.6);background:rgba(120,80,30,.95)}";
 document.head.appendChild(st);
 mo=new MutationObserver(sync);mo.observe(cl,{childList:true,subtree:true,attributes:true,attributeFilter:["class"]});
 sync();
}
window.D9V={mumble:mumble,speak:speak};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();
