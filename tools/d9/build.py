import re,subprocess,sys
VER=int(sys.argv[1]) if len(sys.argv)>1 else 368
import os
D=os.path.dirname(os.path.abspath(__file__))+'/'
s=subprocess.check_output(['git','-C','/home/claude/pustosh','show','refs/heads/v358-stable:index.html']).decode('utf-8')
# 1. прогресс достижений
a='function ladder(pre,ic,names,desc,th,rws,get){th.forEach(function(t,i){add(pre+t,ic,names[i],desc.replace("{n}",fs(t)),rws[i],function(){return get()>=t})})}'
assert s.count(a)==1
b='var PR=window.GPROG=window.GPROG||{};function ladder(pre,ic,names,desc,th,rws,get){th.forEach(function(t,i){PR[pre+t]=[get,t];add(pre+t,ic,names[i],desc.replace("{n}",fs(t)),rws[i],function(){return get()>=t})})}'
s=s.replace(a,b)
# 1б. выстрел с заданным оружием (для «Колоди»): shoot(OW) пропускает КД/замок, но проверяет патроны
a1='function shoot(){\n  bossCheck();var T=btActive();'
assert s.count(a1)==1
s=s.replace(a1,'function shoot(OW){\n  bossCheck();var T=btActive();')
a2='var W=WP.sel(),rs=WP.ready(W);if(rs=="cd"'
assert s.count(a2)==1
s=s.replace(a2,'var W=OW||WP.sel(),rs=OW?(WP.ammo(W)>=1?"ok":"ammo"):WP.ready(W);if(rs=="cd"')
a3='function buy(){if(typeof window._mkOld=="function")'
assert s.count(a3)==1
s=s.replace(a3,'window._nbShoot=shoot;'+a3)
# 1в. кони: ступень коня = +1 ячейка мешка в налёте на обоз и чуть легче побег
c1='raid:{mulPer:.012,minMul:.6,maxMul:1.08,leadPer:.6,leadMax:20},'
assert s.count(c1)==1
s=s.replace(c1,'raid:{mulPer:.012,minMul:.55,maxMul:1.08,leadPer:.6,leadMax:20,tierMul:.03},')
c2='H.raidMul=function(){var sp=H.speed();return Math.max(C.raid.minMul,Math.min(C.raid.maxMul,1-(sp-10)*C.raid.mulPer))};'
assert s.count(c2)==1
s=s.replace(c2,'H.tier=function(){var h=act();var B=h&&(C.breeds[h.b]||C.breeds[0]);return B?B.r:0};H.bagBonus=function(){return H.tier()};H.raidMul=function(){var sp=H.speed();return Math.max(C.raid.minMul,Math.min(C.raid.maxMul,(1-(sp-10)*C.raid.mulPer)*(1-H.tier()*C.raid.tierMul)))};')
c3='cargoCapacity:C.cargoCap,'
assert s.count(c3)==1
s=s.replace(c3,'cargoCapacity:C.cargoCap+(window.HORSE&&HORSE.bagBonus?HORSE.bagBonus():0),')
c4="<p><i>🚚</i>Наліт на обоз: '+(raidPct>0?"
assert s.count(c4)==1
s=s.replace(c4,"<p><i>🎒</i>Мішок у нальоті: <b>'+(4+H.bagBonus())+' комірок</b> (кожен кращий кінь +1)</p><p><i>🚚</i>Наліт на обоз: '+(raidPct>0?")
# 2. версия
for pat,rep in [(r'name="ver" content="358"','name="ver" content="%d"'%VER),(r'var VER=358','var VER=%d'%VER),(r'id="hver">v358<','id="hver">v%d<'%VER)]:
    assert len(re.findall(pat,s))==1,pat
    s=re.sub(pat,rep,s)
# 3. блоки
css=open(D+'css.css',encoding='utf-8').read()
blocks='<style id="d9css">'+css+'</style>\n'
for n,f in [('d9core','core.js'),('d9hub','hub.js'),('d9skr','skr.js'),('d9bc','bcombo.js'),('d9ar','arena.js'),('d9pet','pet.js'),('d9wh','wheel.js'),('d9sg','siege.js'),('d9x','extra.js'),('d9tp','tips.js')]:
    blocks+='<script id="%s">\n%s\n</script>\n'%(n,open(D+f,encoding='utf-8').read())
i=s.rfind('</body>'); assert i>0
s=s[:i]+blocks+s[i:]
sys.path.insert(0,D); import apply_tr
s=apply_tr.apply(s,D)
open('/home/claude/pustosh/index.html','w',encoding='utf-8').write(s)
print('ok',len(s))
