#!/usr/bin/env python3
"""Non-destructive v172 -> v173 patch for the Pustosh Telegram Mini App."""
from pathlib import Path
import base64
import re
import sys


def build(src: Path, target: Path) -> None:
    s = src.read_text(encoding="utf-8")
    assert '<meta name="ver" content="172">' in s, "Expected v172 source"

    def rep(before, after, n=1):
        nonlocal s
        count = s.count(before)
        assert count == n, (count, n, before[:120])
        s = s.replace(before, after)

    def section(begin, end, replacement):
        nonlocal s
        assert s.count(begin) == 1, begin
        i = s.index(begin)
        j = s.index(end, i + len(begin))
        s = s[:i] + replacement + s[j:]

    rep('<meta name="ver" content="172">', '<meta name="ver" content="173">')
    rep('var VER=172;', 'var VER=173;')
    rep('id="hver">v172<', 'id="hver">v173<')

    # New permanent, per-boss daily counters; switching bosses doesn't erase uses.
    rep('/* ---------- события ---------- */', """/* v173: daily boss starts are individual, use Kyiv's calendar day. */
function perBossDay(){
 var p=PG(),d=kyivDate();
 if(!p.bossDaily||p.bossDaily.date!==d)p.bossDaily={date:d,uses:{}};
 return p.bossDaily.uses;
}
window.pgBossRuns=function(bid){
 var id=bid||(BOSSES[S.cb]&&BOSSES[S.cb].id),o=perBossDay();
 return Math.max(0,o[id]||0);
};
window.pgBossMarkRun=function(bid){
 var id=bid||(BOSSES[S.cb]&&BOSSES[S.cb].id),o=perBossDay();
 if((o[id]||0)>=CFG.BOSS_RUNS_PER_DAY)return false;
 o[id]=(o[id]||0)+1;sv();return true;
};
""" + '/* ---------- события ---------- */')
    rep('tk=function(){return S.bd.runs||0};',
        'tk=function(){return window.pgBossRuns?pgBossRuns():0};')
    rep('b.pe!==b.end&&(S.bd.runs||0)>=DAYLIM',
        'b.pe!==b.end&&tk()>=DAYLIM')
    rep('if((S.bd.runs||0)>=DAYLIM){toast(',
        'if(tk()>=DAYLIM){toast(')
    rep('S.bd.runs=(S.bd.runs||0)+1;b.pe=b.end;b.pd=0',
        'if(!pgBossMarkRun(BOSSES[S.cb].id)){toast("Ліміт для цього боса.");return}'
        ';S.bd.runs=(S.bd.runs||0)+1;b.pe=b.end;b.pd=0')
    rep('За день можна розпочати до "+DAYLIM+" боїв (разом соло і відряд).',
        'За день можна розпочати до "+DAYLIM+" боїв із КОЖНИМ босом (соло і відряд разом).')
    rep('Спроб на день: "+DAYLIM+" (перший постріл по новому босу).',
        'Спроб на день ДЛЯ КОЖНОГО БОСА: "+DAYLIM+" (перший постріл по новому босу).')

    # A large readable detail card compensates for labels baked into poster art.
    rep('var scr="",on=0,tmr=0,ttm=0,lastEv="",lastFd=0,hudOld="";',
        'var scr="",on=0,tmr=0,ttm=0,lastEv="",lastFd=0,hudOld="",previewBossId=-1;')
    rep('/* ---------- нажатия ---------- */', """/* v173: accessible card with large text and an explicit confirmation. */
function bossPreview(i){
 var b=BOSSES[i],a=window.bossAccess?bossAccess(i):{ok:1};previewBossId=i;
 var body='<p><i>'+b.w+'</i></p>'
  +'<div class="k"><span>❤️ Здоров’я</span><em>'+nf(b.hp)+'</em></div>'
  +'<div class="k"><span>💪 Сила за перемогу</span><em>+'+nf(b.pw)+'</em></div>'
  +'<div class="k"><span>⚔️ Спроби з цим босом</span><em>'+pgBossRuns(b.id)+' / '+DAYLIM+'</em></div>'
  +'<p>Перстень, камінь і уламки можуть випасти з шансом. Срібло і сила — за перемогу.</p>';
 if(!a.ok)body+='<p>🔒 Бос поки недоступний: виконай вимоги глави й збери ключі.</p>';
 else if(pgBossRuns(b.id)>=DAYLIM)body+='<p>На сьогодні всі спроби використані.</p>';
 else body+='<div class="nbb" data-a="confirmboss" style="width:74%">ДО БОЮ</div>';
 modal(b.n,body);
}
""" + '/* ---------- нажатия ---------- */')
    rep('else if(a=="dplus")toast(',
        'else if(a=="confirmboss"){g("nbmd").classList.remove("on");if(previewBossId>=0)pick(previewBossId)}\n  else if(a=="dplus")toast(')
    rep('else if(d.pk!=null)pick(+d.pk);',
        'else if(d.pk!=null)bossPreview(+d.pk);')

    # Forging balance: 100, 120, 140… shards; low rising success rate.
    rep('RING_SHARDS_PER_WIN:1,RING_SHARDS_TO_CRAFT:5,RING_DROP_CHANCE:.12,GEM_DROP_CHANCE:.25,',
        'RING_SHARDS_PER_WIN:0,RING_SHARDS_TO_CRAFT:100,RING_DROP_CHANCE:.02,GEM_DROP_CHANCE:.015,'
        'RING_SHARDS_DROP_CHANCE:.65,RING_SHARDS_MIN:10,RING_SHARDS_MAX:25,')
    rep('var J=CFG.JEWEL=CFG.JEWEL||{',
        'var J=CFG.JEWEL=CFG.JEWEL||{\n CRAFT:{baseChance:.08,stepChance:.02,maxChance:.40,baseShards:100,stepShards:20},')
    rep('function rar(it,kind){var G=J.GROUPS[it.g],r=kind=="ring"?G.ring:G.gem,t=r[1]>r[0]?(it.pct-r[0])/(r[1]-r[0]):.5;return t<.34?"обычный":t<.8?"редкий":"эпический"}',
        'function rar(it,kind){return "редкий"}')
    rep('function JS(){var p=P();if(!p.jewel)p.jewel={};var j=p.jewel;["crafted","inserted","swapped","ringsFound","gemsFound"].forEach(function(k){if(j[k]===undefined)j[k]=0});return j}',
        'function JS(){var p=P();if(!p.jewel)p.jewel={};var j=p.jewel;["crafted","inserted","swapped","ringsFound","gemsFound","forgeFailures","forgeAttempts"].forEach(function(k){if(j[k]===undefined)j[k]=0});if(!j.failsByGroup)j.failsByGroup={};return j}')
    rep('function pc(x){return "+"+Math.round(x*100)+"%"}',
        'function pc(x){return "+"+Math.round(x*100)+"%"}\n'
        'function cfInfo(g){var n=JS().failsByGroup["g"+g]||0,C=J.CRAFT;'
        'return{fails:n,need:C.baseShards+n*C.stepShards,'
        'chance:Math.min(C.maxChance,C.baseChance+n*C.stepChance)}}')
    rep('''  p.ringShards[sh]=(p.ringShards[sh]||0)+CFG.RING_SHARDS_PER_WIN;
  rows.push(["🧩 Уламок перстня","+"+CFG.RING_SHARDS_PER_WIN+" · "+p.ringShards[sh]+"/"+CFG.RING_SHARDS_TO_CRAFT]);''',
        '''  if(Math.random()<CFG.RING_SHARDS_DROP_CHANCE){
    var count=rnd(CFG.RING_SHARDS_MIN,CFG.RING_SHARDS_MAX);
    p.ringShards[sh]=(p.ringShards[sh]||0)+count;
    rows.push(["🧩 Уламки персня","+"+count+" · усього "+p.ringShards[sh]]);
  }''')
    rep('Трофеї з боса: 🔑 ключ і 🧩 уламок завжди, 💍 перстень та 💎 камінь — з шансом. Ювелір чекає на ринку.',
        'Трофеї з боса: 🔑 ключ за перемогу. 🧩 уламки, 💍 перстень і 💎 камінь — з шансом. Ювелір чекає на ринку.')

    section('function shopBox(){', 'function pickBox(){', """function shopBox(){
 var p=P(),h="";
 [1,2,3].forEach(function(g){
  var G=J.GROUPS[g],F=cfInfo(g),n=p.ringShards["g"+g]||0,ok=n>=F.need;
  h+='<div class="jit"><b>🧩 '+G.ic+' '+G.ru+' перстень</b> · '+n+'/'+F.need+' осколків'
  +'<small>Спроба №'+(F.fails+1)+' · шанс успіху '+Math.round(F.chance*100)+'%. При невдачі осколки та срібло зникають. Наступна спроба дорожча, але шанс вищий.</small>'
  +'<small>Робота: '+nf(G.craft)+' 🥈 · можливий бонус: '+pc(G.ring[0]/100)+' … '+pc(G.ring[1]/100)+'</small>'
  +'<div class="jac"><button data-a="craft" data-g="'+g+'"'+(ok?'':' disabled')+'>Спробувати скувати</button></div></div>';
 });
 return h+'<div class="jem">Уламки випадають з босів із шансом. Ковка не гарантує перстень.</div>';
}
""")
    section('function confirmBox(){', 'function find(a,id){', """function confirmBox(){
 var c=st.cf,h='<div class="jcf"><h4>Підтвердити?</h4>';
 if(c.t=="ins"){
  var r=find(P().rings,c.id),g=find(P().gems,c.gid),G=J.GROUPS[r.g],cost=r.gem?G.swap:G.insert;
  var tot=Math.min(CFG.RING_GEM_BOSS_DAMAGE_CAP,r.pct/100+g.pct/100);
  h+='<p>'+ringName(r)+' + '+gemName(g)+' = '+pc(tot)+'</p><p>Робота: '+nf(cost)+' 🥈</p>';
 }else if(c.t=="craft"){
  var G2=J.GROUPS[c.g],F=cfInfo(c.g);
  h+='<p>Спроба №'+(F.fails+1)+': витратити '+F.need+' осколків і '+nf(G2.craft)+' 🥈?</p>'
   +'<p>Шанс '+Math.round(F.chance*100)+'%. За невдачі ресурси не повернуться.</p>';
 }
 return h+'<div class="jac"><button data-a="yes">Так</button><button class="alt" data-a="no">Ні</button></div></div>';
}
""")
    section('function doConfirm(){', 'function open(){', """function doConfirm(){
 var c=st.cf,p=P(),js=JS();st.cf=null;
 if(c.t=="ins"){
  var r=find(p.rings,c.id),g=find(p.gems,c.gid);if(!r||!g){st.msg="Предмет не знайдено.";return}
  var G=J.GROUPS[r.g],cost=r.gem?G.swap:G.insert;
  if(S.sv<cost){st.msg="Потрібно "+nf(cost)+" 🥈.";return}
  S.sv-=cost;if(r.gem){p.gems.push(r.gem);js.swapped++}else js.inserted++;
  r.gem=g;p.gems=p.gems.filter(function(x){return x.id!=g.id});sv();
  try{draw()}catch(e){}st.tab="rings";st.msg="Готово: "+ringName(r)+" "+pc(Math.min(CFG.RING_GEM_BOSS_DAMAGE_CAP,r.pct/100+g.pct/100))+" до урону по босах.";
 }else if(c.t=="craft"){
  var G2=J.GROUPS[c.g],sh="g"+c.g,F=cfInfo(c.g);
  if((p.ringShards[sh]||0)<F.need){st.msg="Не вистачає осколків: потрібно "+F.need;return}
  if(S.sv<G2.craft){st.msg="Не вистачає срібла: потрібно "+nf(G2.craft)+" 🥈.";return}
  S.sv-=G2.craft;p.ringShards[sh]-=F.need;js.forgeAttempts++;
  if(Math.random()>=F.chance){
   js.forgeFailures++;js.failsByGroup[sh]=F.fails+1;sv();try{draw()}catch(e){}
   st.tab="shop";var N=cfInfo(c.g);
   st.msg="❌ Невдала ковка. Наступна спроба: "+N.need+" осколків, шанс "+Math.round(N.chance*100)+"%.";
  }else{
   js.failsByGroup[sh]=0;var nr=mkRing(c.g,"craft");p.rings.push(nr);js.crafted++;
   sv();try{draw()}catch(e){}st.tab="rings";
   st.msg="🎉 Перстень скуто: "+ringName(nr)+" "+pc(nr.pct/100)+" до урону по босах!";
  }
 }
}
""")

    # Export the ten heavyweight illustrated boss backgrounds unchanged.
    keys = ("list", "kul", "pet", "sul", "nag", "var", "kar", "ost", "kos", "cha")
    dest = target.parent / "assets" / "boss"
    dest.mkdir(parents=True, exist_ok=True)
    for key in keys:
        pat = r'("' + key + r'": ")data:image/webp;base64,([A-Za-z0-9+/=]+)(")'
        matches = list(re.finditer(pat, s))
        assert len(matches) == 1, (key, len(matches))
        m = matches[0]
        raw = base64.b64decode(m.group(2), validate=True)
        assert raw[:4] == b"RIFF" and raw[8:12] == b"WEBP", key
        (dest / (key + ".webp")).write_bytes(raw)
        s = s[:m.start()] + m.group(1) + "assets/boss/" + key + ".webp" + m.group(3) + s[m.end():]

    # Readability and reduced-motion accessibility, no lossy art processing.
    rep('</body></html>', """<style id="quality-v173">
#nbmp{overflow-y:auto;max-height:calc(100% - 380px)}
#nbmp p{line-height:1.45!important}
#nbmp .k{min-height:45px;align-items:center}
#nbmp .nbb{min-height:58px;display:flex;align-items:center;justify-content:center}
#nbmp *{overflow-wrap:break-word}
@media(max-width:380px){#rtx .rtt button,#rtx .rtm button{font-size:12px}}
@media(prefers-reduced-motion:reduce){#nbx .ncur,#nbx .nbd,#nbx #nbs.shk{animation:none!important}}
</style>
</body></html>""")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(s, encoding="utf-8")
    print(f"v173 prepared: {target} / {len(keys)} original WebP files; {len(s):,} HTML chars")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python patch_v173.py V172.html OUTPUT_DIR/index.html")
    build(Path(sys.argv[1]), Path(sys.argv[2]))

