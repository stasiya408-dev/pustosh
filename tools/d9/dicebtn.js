/* d9db: минималистичные кнопки таверны (тонкая рамка: зелёная/красная) */
(function(){
var P='html body #dice ';
var G=[P+'#dsbtn',P+'#thb',P+'#keb',P+'button[onclick="dmAgain()"]',P+'button[onclick="dmFxClose()"]',P+'#dbuy'];
var R=[P+'#rkb',P+'#reb',P+'#dsb',P+'button[onclick="dmDefend(1)"]'];
var ALL=G.concat(R);
var css=ALL.join(',')+'{background-image:none!important;background-color:rgba(16,11,7,.74)!important;border:1.5px solid var(--c)!important;border-radius:12px!important;aspect-ratio:auto!important;filter:none!important;height:auto!important;min-height:46px!important;padding:10px 14px!important;width:88%!important;max-width:none!important;font:600 16px/1.2 Georgia,serif!important;letter-spacing:.4px!important;color:var(--t)!important;text-shadow:none!important;box-shadow:0 0 0 1px rgba(0,0,0,.5),0 0 9px var(--g)!important;display:flex;align-items:center;justify-content:center;gap:8px;position:relative;transition:box-shadow .2s,background-color .2s}'
+G.join(',')+'{--c:#5fbf6a;--t:#d8f3d6;--g:rgba(95,191,106,.28)}'
+R.join(',')+'{--c:#d2514a;--t:#ffd9d4;--g:rgba(210,81,74,.28)}'
+ALL.join(':active,')+':active{background-color:rgba(40,28,18,.9)!important;box-shadow:0 0 0 1px rgba(0,0,0,.5),0 0 14px var(--c)!important}'
+P+'#rkb{width:80%!important;opacity:.7}'
+P+'#rkb.on{opacity:1;background-color:rgba(60,16,14,.85)!important;box-shadow:0 0 0 1px rgba(0,0,0,.5),0 0 16px var(--c)!important}'
+P+'#rkb.on::after{position:static!important;transform:none!important;font:bold 18px Georgia,serif!important;color:var(--c)!important;text-shadow:none!important}'
+ALL.join('::before,')+'::before{display:none!important}';
var s=document.createElement('style');s.id='d9dbcss';s.textContent=css;document.head.appendChild(s);
window.D9DB={on:1};
})();
