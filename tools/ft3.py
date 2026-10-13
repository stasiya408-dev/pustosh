from playwright.sync_api import sync_playwright
stub="window.Telegram={WebApp:{ready(){},expand(){},initDataUnsafe:{}}};"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':780},has_touch=True,is_mobile=True)
    er=[];pg.on('pageerror',lambda e:er.append(str(e)))
    pg.route('**/telegram-web-app.js',lambda r:r.fulfill(body=stub,content_type='application/javascript'))
    pg.goto('file:///mnt/user-data/outputs/index.html');pg.wait_for_timeout(2500);print(pg.inner_text('#hver'))
    pg.evaluate('S.pw=40;S.fz=50;draw();bossOpen()');pg.wait_for_timeout(300)
    print(pg.inner_text('#bm_b1'))
    pg.evaluate('bossPick(0)');pg.wait_for_timeout(300)
    print('solo',pg.evaluate('B().hp+"/"+B().max'))
    pg.evaluate('setMode("grp")');print('grp',pg.evaluate('B().hp+"/"+B().max'))
    # миграция: старый босс 8000
    pg.evaluate('S.bd.grp.max=8000;S.bd.grp.hp=4000;bossCheck()');print('migr',pg.evaluate('B().hp+"/"+B().max'))
    print(er or 'нет ошибок');b.close()
