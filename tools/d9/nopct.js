/* d9np v378: проценты ВЕРОЯТНОСТИ нигде не показываются (шанс выпадения, ковки, заточки, побега, крита).
   Числа остаются в логике; в тексте вместо них слова. Бонусы (+% урона, срібла, сили) не трогаем. */
(function(){
function wd(v){return v>=50?"часто":v>=15?"нерідко":v>=3?"рідко":"дуже рідко"}
var N="\\d+(?:[.,]\\d+)?";
var TRI=new RegExp(N+"\\s*%\\s*\\/\\s*"+N+"\\s*%\\s*\\/\\s*"+N+"\\s*%","g");
var SEQ=new RegExp("("+N+")%(?:\\s*\\/\\s*"+N+"%)*","g");
var CH=new RegExp("([Шш]анс[^%\\d<]{0,90}?[:—-]?\\s*(?:[А-Яа-яІіЇїЄє’' ]{0,12})?)\\+?("+N+"%(?:\\s*\\/\\s*"+N+"%)*)","g");
function mx(s){var m=s.match(/\d+(?:[.,]\d+)?/g)||[],b=0;m.forEach(function(x){x=parseFloat(x.replace(",","."));if(x>b)b=x});return b}
function clean(t){
 if(t.indexOf("%")<0&&t.indexOf("в.п.")<0)return t;
 var o=t;
 t=t.replace(TRI,function(m){return wd(mx(m))});
 t=t.replace(CH,function(m,a,b){return a+wd(mx(b))});
 t=t.replace(/\+?[\d.,]+\s*в\.п\.\s*шансу/g,"більше шансу");
 return t}
var busy=0;
function node(n){
 var v=n.nodeValue;if(!v)return;
 var c=clean(v);if(c!==v){n.nodeValue=c;return}
 /* «шанс <b>16%</b>» и пары «Шанс» + элемент с процентом */
 if(/[Шш]анс[^%\d]{0,40}$/.test(v)){var s=n.nextSibling;
  if(s&&s.nodeType==1&&/^\s*\+?\d+(?:[.,]\d+)?%\s*$/.test(s.textContent))s.textContent=wd(parseFloat(s.textContent.replace(",",".").replace(/[^\d.]/g,"")))}
}
/* таблица наград: значения строк вида «12,5%» */
function rows(root){
 var l=root.querySelectorAll?root.querySelectorAll(".k em"):[];
 for(var i=0;i<l.length;i++){var e=l[i],tx=e.textContent;
  if(/^\s*\d+(?:[.,]\d+)?%\s*$/.test(tx)){e.textContent=wd(parseFloat(tx.replace(",",".").replace(/[^\d.]/g,"")))}}}
function scan(root){
 var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:function(n){var p=n.parentNode&&n.parentNode.nodeName;return p=="SCRIPT"||p=="STYLE"||p=="TEXTAREA"?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}}),n,a=[];
 while(n=w.nextNode())a.push(n);
 a.forEach(node);rows(root)}
var q=[],sch=0;
function flush(){sch=0;var l=q;q=[];l.forEach(function(r){if(r&&r.isConnected)scan(r)})}
var mo=new MutationObserver(function(ms){
 ms.forEach(function(m){
  if(m.type=="characterData"){var p=m.target.parentNode;if(p)q.push(p)}
  else m.addedNodes.forEach(function(a){q.push(a.nodeType==1?a:a.parentNode)})});
 if(!sch){sch=1;requestAnimationFrame(flush)}});
function boot(){if(!document.body)return;mo.observe(document.body,{childList:true,subtree:true,characterData:true});scan(document.body);
 setInterval(function(){scan(document.body)},3000)}
if(document.readyState=="loading")document.addEventListener("DOMContentLoaded",boot);else boot();
window.D9NP={scan:function(){scan(document.body)},clean:clean};
})();
