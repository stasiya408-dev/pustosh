(function(){
// v382: рука Нагая ближче к плечу + виньетка на фоне боя (блок d9ng)
var DX=-12,DY=-17;
function arm(){
  var M=window.NGM;if(!M||M._d9)return;
  ["arm2","arm2up"].forEach(function(k){if(M[k]&&M[k].A){M[k].A[4]+=DX;M[k].A[5]+=DY;}});
  M._d9=1;
}
arm();
var st=document.createElement("style");st.id="d9ngcss";
st.textContent="#nbF.i-nag_fight::after{content:'';position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:1;"+
"background:radial-gradient(ellipse 46% 36% at 46% 42%,rgba(0,0,0,0) 0%,rgba(0,0,0,0) 55%,rgba(6,2,2,.55) 100%),"+
"radial-gradient(ellipse 80% 70% at 46% 42%,rgba(0,0,0,0) 40%,rgba(4,1,1,.6) 100%);-webkit-mask-image:linear-gradient(#000 0,#000 66%,transparent 74%);mask-image:linear-gradient(#000 0,#000 66%,transparent 74%)}"+
"#nbF.i-nag_fight #nbNg{filter:drop-shadow(0 0 22px rgba(255,170,90,.38)) drop-shadow(0 0 3px rgba(255,220,170,.35))}";
document.head.appendChild(st);
window.D9NG={arm:arm};
})();
