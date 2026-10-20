#!/usr/bin/env python3
"""Allow purchasing multiple pistols in one transaction from the existing market."""
from pathlib import Path

source=Path("index.html")
html=source.read_text(encoding="utf-8")
start=html.find("function marketOpen(){")
end=html.find("\n\nfunction bossOpen()",start)
if start<0 or end<0:
    raise SystemExit("Could not isolate existing marketOpen() safely")
old=html[start:end]
if "mkqty" in old:
    print("Bulk pistol purchases already installed")
    raise SystemExit(0)
if 'id="mkbuy"' not in old or "S.fz++" not in old:
    raise SystemExit("Unknown market structure; preserving game rather than replacing it")

replacement=r"""function marketOpen(){
 var m=$("mkt");
 if(!m){
  m=document.createElement("div");
  m.id="mkt";
  m.style.cssText="position:fixed;left:0;top:0;right:0;bottom:0;z-index:99999;background:rgba(0,0,0,.7);display:none;align-items:center;justify-content:center";
  m.innerHTML='<div style="background:#2a1a0c;border:3px solid #c9a24a;border-radius:14px;padding:18px;width:min(90vw,370px);color:#f3e2b8;text-align:center;max-height:92vh;overflow-y:auto;box-sizing:border-box">'
   +'<div style="font-size:22px;font-weight:bold;margin-bottom:8px">🛒 Рынок</div>'
   +'<div id="mktxt" style="margin-bottom:12px;font-size:14px;line-height:1.5"></div>'
   +'<div style="border:1px solid #947344;border-radius:10px;padding:12px;margin-bottom:12px;background:rgba(0,0,0,.18)">'
   +'<label for="mkqty" style="display:block;font-size:13px;margin-bottom:9px;font-weight:bold;letter-spacing:.06em">КОЛИЧЕСТВО САМОПАЛОВ</label>'
   +'<div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:9px">'
   +'<button type="button" id="mkminus" aria-label="Уменьшить количество" style="width:44px;height:44px;border:1px solid #c9a24a;border-radius:8px;background:#45311d;color:#f3e2b8;font-size:24px">−</button>'
   +'<input id="mkqty" type="number" inputmode="numeric" min="1" max="9999" step="1" value="1" aria-label="Количество самопалов" style="width:104px;height:44px;border:2px solid #c9a24a;border-radius:8px;background:#f7eac9;color:#31200e;font-size:22px;font-weight:bold;text-align:center;box-sizing:border-box">'
   +'<button type="button" id="mkplus" aria-label="Увеличить количество" style="width:44px;height:44px;border:1px solid #c9a24a;border-radius:8px;background:#45311d;color:#f3e2b8;font-size:24px">+</button></div>'
   +'<div style="display:flex;justify-content:center;gap:6px;margin-bottom:10px">'
   +'<button type="button" data-mkq="1" style="flex:1;padding:8px 3px;border:1px solid #927146;background:#49321a;color:#f3e2b8;border-radius:7px">1</button>'
   +'<button type="button" data-mkq="10" style="flex:1;padding:8px 3px;border:1px solid #927146;background:#49321a;color:#f3e2b8;border-radius:7px">10</button>'
   +'<button type="button" data-mkq="100" style="flex:1;padding:8px 3px;border:1px solid #927146;background:#49321a;color:#f3e2b8;border-radius:7px">100</button>'
   +'<button type="button" data-mkq="max" style="flex:1;padding:8px 3px;border:1px solid #927146;background:#49321a;color:#f3e2b8;border-radius:7px">МАКС</button></div>'
   +'<div id="mkTotal" aria-live="polite" style="font-size:18px;font-weight:bold;color:#f4d48c"></div>'
   +'</div>'
   +'<button type="button" id="mkbuy" style="width:100%;min-height:47px;padding:10px;font-size:16px;border-radius:10px;border:0;background:#c9a24a;color:#2a1a0c;font-weight:bold;margin-bottom:10px"></button>'
   +'<div style="font-size:12px;opacity:.7;margin-bottom:12px">Настойки, барахолка и талеры за звёзды — скоро</div>'
   +'<button type="button" id="mkx" style="width:100%;padding:10px;border-radius:10px;border:1px solid #c9a24a;background:none;color:#f3e2b8;font-size:15px">Закрыть</button></div>';
  document.body.appendChild(m);
  function quantity(){var n=Math.floor(Number($("mkqty").value));return Number.isFinite(n)?Math.max(1,Math.min(9999,n)):1}
  function refresh(){
   var n=quantity(),single=_mp(),sum=n*single;
   $("mktxt").textContent="1 самопал — "+single+" 💰 · У тебя "+S.tl+" 💰 и "+S.fz+" 🔫";
   $("mkTotal").textContent="Итого: "+n+" × "+single+" = "+sum+" 💰";
   $("mkbuy").textContent="Купить "+n+" 🔫 за "+sum+" 💰";
   $("mkbuy").style.opacity=S.tl<sum?".72":"1";
  }
  $("mkqty").oninput=refresh;
  $("mkqty").onchange=function(){$("mkqty").value=quantity();refresh()};
  $("mkminus").onclick=function(){$("mkqty").value=Math.max(1,quantity()-1);refresh()};
  $("mkplus").onclick=function(){$("mkqty").value=Math.min(9999,quantity()+1);refresh()};
  Array.from(m.querySelectorAll("[data-mkq]")).forEach(function(el){
   el.onclick=function(){
    var q=el.getAttribute("data-mkq");
    $("mkqty").value=q==="max"?Math.max(1,Math.min(9999,Math.floor(S.tl/_mp()))):q;
    refresh();
   };
  });
  $("mkx").onclick=function(){m.style.display="none"};
  $("mkbuy").onclick=function(){
   var n=quantity(),total=n*_mp();
   $("mkqty").value=n;
   if(S.tl<total){say("Не хватает талеров: нужно "+total+" 💰");refresh();return}
   S.tl-=total;S.fz+=n;S.mb=(S.mb||0)+n;
   if(typeof save==="function")save();
   draw();
   if(typeof window._mkOld==="function")window._mkOld();
   try{bossUI()}catch(e){}
   say("Куплено "+n+" самопалов 🔫 за "+total+" 💰");
   refresh();
  };
  m._mkRefresh=refresh;
 }
 $("mkqty").value=1;
 m._mkRefresh();
 m.style.display="flex";
}"""
html=html[:start]+replacement+html[end:]
source.write_text(html,encoding="utf-8")
print("Installed bulk self-pistol purchases with live taler total")
