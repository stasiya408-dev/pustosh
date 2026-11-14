(function(){
/* ЄДИНИЙ ЕКРАН ЗАВАНТАЖЕННЯ: чорний фон і білі козаки на конях замість смужки (і при вході, і між вкладками) */
var css=document.createElement("style");css.id="d9ldcss";
css.textContent="#ldr{background:#000!important}#ldr>.lsc,#ldr>.lmid,#ldr>.lbw{display:none!important}#ldr #ldcv{position:absolute;inset:0;width:100%;height:100%;display:block}";
document.head.appendChild(css);
var el=document.getElementById("ldr");if(!el)return;
var cv=document.createElement("canvas");cv.id="ldcv";el.insertBefore(cv,el.firstChild);
var cx=cv.getContext("2d"),W=0,H=0,DPR=1,run=0,T0=performance.now();
function size(){DPR=Math.min(window.devicePixelRatio||1,1.5);W=el.clientWidth||innerWidth;H=el.clientHeight||innerHeight;cv.width=Math.round(W*DPR);cv.height=Math.round(H*DPR)}
function leg(x,y,ph,up,lo,sc){
 var a=Math.sin(ph)*.75,b=Math.max(0,-Math.cos(ph))*1.15+.1;
 var kx=x+Math.sin(a)*up,ky=y+Math.cos(a)*up,fx=kx+Math.sin(a-b)*lo,fy=ky+Math.cos(a-b)*lo;
 cx.beginPath();cx.moveTo(x,y);cx.lineTo(kx,ky);cx.lineTo(fx,fy);cx.stroke();
 cx.beginPath();cx.arc(fx,fy,3.2,0,6.3);cx.fill()}
function rider(x,y,s,t,off){
 var ph=t*9+off,bob=Math.sin(ph*2)*2.5;
 cx.save();cx.translate(x,y+bob*s);cx.scale(s,s);cx.translate(0,-10);
 cx.fillStyle="#fff";cx.strokeStyle="#fff";cx.lineCap="round";cx.lineJoin="round";cx.lineWidth=7;
 /* ноги коня */
 cx.lineWidth=5.5;leg(28,-58,ph,30,34);leg(20,-58,ph+.6,30,34);leg(-28,-58,ph+Math.PI,30,34);leg(-38,-58,ph+Math.PI+.6,30,34);
 /* тулуб */
 cx.beginPath();cx.ellipse(-4,-72,42,14,-.06,0,6.3);cx.fill();
 /* шия і голова */
 cx.beginPath();cx.moveTo(30,-80);cx.quadraticCurveTo(48,-98,54,-116);cx.lineTo(66,-114);cx.quadraticCurveTo(84,-106,86,-98);cx.lineTo(72,-96);cx.quadraticCurveTo(60,-90,46,-68);cx.closePath();cx.fill();
 cx.beginPath();cx.moveTo(55,-116);cx.lineTo(54,-128);cx.lineTo(62,-117);cx.fill();
 /* грива і хвіст */
 var w=Math.sin(ph*1.3)*6;
 cx.lineWidth=4;cx.beginPath();cx.moveTo(34,-112);cx.quadraticCurveTo(20,-122+w,10,-104);cx.stroke();
 cx.lineWidth=5;cx.beginPath();cx.moveTo(-46,-76);cx.bezierCurveTo(-68,-76+w,-80,-58-w,-100,-60+w);cx.stroke();
 /* козак */
 cx.lineWidth=8;cx.beginPath();cx.moveTo(-4,-80);cx.lineTo(8,-112);cx.stroke();
 cx.beginPath();cx.arc(13,-122,8,0,6.3);cx.fill();
 /* шапка з шликом */
 cx.beginPath();cx.moveTo(4,-126);cx.lineTo(8,-142);cx.lineTo(24,-140);cx.lineTo(22,-124);cx.closePath();cx.fill();
 cx.lineWidth=4;cx.beginPath();cx.moveTo(8,-140);cx.quadraticCurveTo(-4,-140+w,-12,-128);cx.stroke();
 /* нога у стремені */
 cx.lineWidth=6;cx.beginPath();cx.moveTo(-2,-78);cx.lineTo(10,-62);cx.lineTo(4,-52);cx.stroke();
 /* рука з шаблею */
 var sw=Math.sin(ph)*.12;
 cx.lineWidth=5;cx.beginPath();cx.moveTo(10,-108);cx.lineTo(28,-128);cx.stroke();
 cx.lineWidth=3;cx.beginPath();cx.moveTo(28,-128);cx.lineTo(28+Math.cos(-.9+sw)*46,-128+Math.sin(-.9+sw)*46);cx.stroke();
 cx.restore()}
var R=[[.0,.86,1.15,0],[.22,.80,.8,2.1],[.47,.84,1.0,4.2],[.71,.78,.7,1.3],[.9,.88,1.3,3.3]];
function frame(now){
 if(!run)return;
 var t=(now-T0)/1000;
 cx.setTransform(DPR,0,0,DPR,0,0);cx.clearRect(0,0,W,H);
 var gy=H*.62,sp=W*.28+60,span=W+520;
 /* земля і смуги швидкості */
 cx.fillStyle="rgba(255,255,255,.10)";
 for(var i=0;i<9;i++){var yy=gy+10+i*((H*.2)/9),len=40+((i*53)%70),xx=((-(t*(260+i*40))+i*173)%(W+160)+(W+160))%(W+160)-80;cx.fillRect(xx,yy,len,1.5)}
 for(var k=0;k<R.length;k++){var r=R[k],s=r[2]*Math.max(.8,W/460),x=((t*sp*(.9+r[2]*.2)+r[0]*span)%span)-260,y=gy+(r[1]-.78)*H*.3+s*30;
  rider(x,y,s*1.1,t,r[3])}
 var tw=cx.measureText;
 requestAnimationFrame(frame)}
function start(){if(run)return;run=1;size();requestAnimationFrame(frame)}
function stop(){run=0}
function sync(){var c=el.className||"";if(c.indexOf("gone")>=0)stop();else start()}
new MutationObserver(sync).observe(el,{attributes:true,attributeFilter:["class"]});
addEventListener("resize",function(){if(run)size()});
sync();
window.D9LD={start:start,stop:stop}
})();
