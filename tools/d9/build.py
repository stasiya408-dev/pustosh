import re,subprocess,sys
VER=int(sys.argv[1]) if len(sys.argv)>1 else 366
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
open('/home/claude/pustosh/index.html','w',encoding='utf-8').write(s)
print('ok',len(s))
