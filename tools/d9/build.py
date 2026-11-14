import re,subprocess,sys
VER=int(sys.argv[1]) if len(sys.argv)>1 else 369
import os
D=os.path.dirname(os.path.abspath(__file__))+'/'
s=subprocess.check_output(['git','-C','/home/claude/pustosh','show','refs/heads/v358-stable:index.html']).decode('utf-8')
# 1. прогресс достижений
a='function ladder(pre,ic,names,desc,th,rws,get){th.forEach(function(t,i){add(pre+t,ic,names[i],desc.replace("{n}",fs(t)),rws[i],function(){return get()>=t})})}'
assert s.count(a)==1
b='var PR=window.GPROG=window.GPROG||{};function ladder(pre,ic,names,desc,th,rws,get){th.forEach(function(t,i){PR[pre+t]=[get,t];add(pre+t,ic,names[i],desc.replace("{n}",fs(t)),rws[i],function(){return get()>=t})})}'
s=s.replace(a,b)
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
# 1д. v371: награды за достижения забираются вручную
a1='if(!S.gach)S.gach={};S.svm=Math.max(S.svm||0,S.sv||0);var s=G(),got=0;GA.forEach(function(a){if(!S.gach[a[0]]&&a[5](s)){S.gach[a[0]]=1;S.tl+=a[4];got=1;toast(achHTML(a))}})'
assert s.count(a1)==1
s=s.replace(a1,'if(!S.gach)S.gach={};if(!S.gcl){S.gcl={};for(var q in S.gach)S.gcl[q]=1}S.svm=Math.max(S.svm||0,S.sv||0);var s=G(),got=0;GA.forEach(function(a){if(!S.gach[a[0]]&&a[5](s)){S.gach[a[0]]=1;got=1;toast(achHTML(a))}})')
a2="""'</em></div><u>+'+a[4]+' 💰</u></div>'};"""
assert s.count(a2)==1
s=s.replace(a2,"""'</em></div><u>🎁 +'+a[4]+' 💰</u></div>'};""")
a2b='(kind||"Достижение выполнено")'
assert s.count(a2b)==1
s=s.replace(a2b,'(kind||"Досягнення виконано — забери нагороду")')
a3='function chk(){var s=ST();ACH.forEach(function(a){if(!S.ach[a[0]]&&a[5](s)){S.ach[a[0]]=1;S.tl+=a[4];toast(achHTML(a,"Достижение таверны"))}})'
assert s.count(a3)==1
s=s.replace(a3,'function chk(){var s=ST();if(!S.acl){S.acl={};for(var q in S.ach)S.acl[q]=1}ACH.forEach(function(a){if(!S.ach[a[0]]&&a[5](s)){S.ach[a[0]]=1;toast(achHTML(a,"Досягнення таверни — забери нагороду"))}})')
tail="""+(on?'<u class="ck">✔</u>':'<u>+'+a[4]+' <span class="tl">💰</span></u>')+'</div>'});"""
for var,flag,c in [('var on=S.gach[a[0]];if(on)n++;','S.gcl','g'),('var on=S.ach[a[0]];if(on)n++;','S.acl','a')]:
    assert s.count(var)==1,var
    s=s.replace(var,var.replace('var on=','var cl=%s&&%s[a[0]],on=' % (flag,flag)))
    i=s.find(var.replace('var on=','var cl=%s&&%s[a[0]],on=' % (flag,flag)))
    j=s.find(tail,i)
    assert 0<j-i<400,(var,j-i)
    s=s[:j]+"""+(on?(cl?'<u class="ck">✔</u>':'<button class="ack" data-c="%s" data-id="'+a[0]+'">Забрати +'+a[4]+' 💰</button>'):'<u>+'+a[4]+' <span class="tl">💰</span></u>')+'</div>'});"""%c+s[j+len(tail):]
for L,fl,gv in [('GA','S.gcl','S.gach'),('ACH','S.acl','S.ach')]:
    old=L+".forEach(function(a){var cl="+fl+"&&"+fl+"[a[0]],on="+gv+"[a[0]];if(on)n++;"
    assert s.count(old)==1,old
    new=("("+L+".slice().map(function(a,i){return [a,i,("+gv+"[a[0]]&&!("+fl+"&&"+fl+"[a[0]]))?0:1]}).sort(function(x,y){return x[2]-y[2]||x[1]-y[1]}).map(function(x){return x[0]})).forEach(function(a){var cl="+fl+"&&"+fl+"[a[0]],on="+gv+"[a[0]];if(on)n++;")
    s=s.replace(old,new)
# 2. версия
for pat,rep in [(r'name="ver" content="358"','name="ver" content="%d"'%VER),(r'var VER=358','var VER=%d'%VER),(r'id="hver">v358<','id="hver">v%d<'%VER)]:
    assert len(re.findall(pat,s))==1,pat
    s=re.sub(pat,rep,s)
# 3. блоки
css=open(D+'css.css',encoding='utf-8').read()
blocks='<style id="d9css">'+css+'</style>\n'
for n,f in [('d9core','core.js'),('d9lk','locks.js'),('d9hub','hub.js'),('d9skr','skr.js'),('d9ar','arena.js'),('d9pet','pet.js'),('d9wh','wheel.js'),('d9sg','siege.js'),('d9rd','raid.js'),('d9x','extra.js'),('d9tp','tips.js'),('d9ic','icons.js'),('d9gv','voice.js'),('d9np','nopct.js'),('d9ld','loader.js'),('d9cp','camp.js'),('d9du','duel.js')]:
    blocks+='<script id="%s">\n%s\n</script>\n'%(n,open(D+f,encoding='utf-8').read())
o='var IDS=["hike","gach","rtx","stx","rdx","ward","dice","gtoast","hdg","jwx","nbmd","nbmp","talentModal","mkt2","vfx"];'
assert s.count(o)==1
s=s.replace(o,'var IDS=[];')
assert s.count('id="dnav2" data-noic="1"')==1
s=s.replace('id="dnav2" data-noic="1"','id="dnav2"')
i=s.rfind('</body>'); assert i>0
s=s[:i]+blocks+s[i:]
sys.path.insert(0,D); import apply_tr
s=apply_tr.apply(s,D)
import short; s=short.apply(s)
open('/home/claude/pustosh/index.html','w',encoding='utf-8').write(s)
print('ok',len(s))
