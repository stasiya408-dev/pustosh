from playwright.sync_api import sync_playwright
stub="window.Telegram={WebApp:{ready(){},expand(){},initDataUnsafe:{}}};"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':780},has_touch=True,is_mobile=True)
    er=[];pg.on('pageerror',lambda e:er.append(str(e)))
    pg.route('**/telegram-web-app.js',lambda r:r.fulfill(body=stub,content_type='application/javascript'))
    pg.goto('file:///mnt/user-data/outputs/index.html');pg.wait_for_timeout(2500);print(pg.inner_text('#hver'))
    pg.evaluate('S.pw=40;S.fz=50;draw();bossOpen()');pg.wait_for_timeout(300);pg.evaluate('bossPick(0)');pg.wait_for_timeout(300);pg.evaluate('setMode("grp")')
    pg.evaluate('useFuse()');print('my',pg.evaluate('S.bd.grp.my'),'hp',pg.evaluate('B().hp'))
    pg.evaluate('S.bd.grp.ft=Date.now()-1');pg.evaluate('friendTick()');print('after tick',pg.evaluate('B().hp'))
    sv=pg.evaluate('S.sv');pw=pg.evaluate('S.pw')
    pg.evaluate('S.bd.grp.ft=Date.now()-1e8;friendTick()')
    print('друзья убили, hp',pg.evaluate('B().hp'),'k',pg.evaluate('tk()'),'sv+',pg.evaluate('S.sv')-sv,'pw+',pg.evaluate('S.pw')-pw)
    # без моих ударов
    pg.evaluate('S.bd.grp.end=0;bossCheck()');print('respawn hp',pg.evaluate('B().hp'),'my',pg.evaluate('S.bd.grp.my'))
    pg.evaluate('S.bd.grp.ft=Date.now()-1e8;friendTick()');print('без меня hp',pg.evaluate('B().hp'),'k',pg.evaluate('tk()'))
    pg.wait_for_timeout(1500);print(er or 'нет ошибок');b.close()
