from playwright.sync_api import sync_playwright
stub="window.Telegram={WebApp:{ready(){},expand(){},initDataUnsafe:{}}};"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':780},has_touch=True,is_mobile=True)
    er=[];pg.on('pageerror',lambda e:er.append(str(e)))
    pg.route('**/telegram-web-app.js',lambda r:r.fulfill(body=stub,content_type='application/javascript'))
    pg.goto('file:///mnt/user-data/outputs/index.html');pg.wait_for_timeout(2500)
    print('ver',pg.inner_text('#hver'),'fz',pg.evaluate('S.fz'),'sv',pg.evaluate('S.sv'),'gd',pg.evaluate('S.gd'))
    pg.evaluate('S.pw=40;draw();bossOpen()');pg.wait_for_timeout(600);pg.screenshot(path='/tmp/b1.png')
    print([pg.inner_text('#bmn%d'%i) for i in range(5)],pg.inner_text('#bm_a0'),pg.inner_text('#bm_b0'),pg.inner_text('#bm_a1'))
    pg.evaluate('bossPick(1)');pg.wait_for_timeout(300);print('locked stays menu',pg.is_visible('#bmenu'))
    pg.evaluate('bossPick(0)');pg.wait_for_timeout(600);pg.screenshot(path='/tmp/b2.png')
    print('hp',pg.evaluate('B().hp+"/"+B().max'),'dmg',pg.evaluate('FUSE_DMG'))
    pg.evaluate('S.fz=20;S.pw=40');
    for i in range(6):
        pg.evaluate('useFuse()')
    print('solo hp',pg.evaluate('B().hp'),'k',pg.evaluate('tk()'),'pw',pg.evaluate('S.pw'),'sv',pg.evaluate('S.sv'))
    pg.evaluate('setMode("grp")');pg.wait_for_timeout(300)
    print('grp hp',pg.evaluate('B().hp+"/"+B().max'))
    for i in range(6):pg.evaluate('useFuse()')
    print('grp hp',pg.evaluate('B().hp'),'k',pg.evaluate('tk()'),'pw',pg.evaluate('S.pw'))
    pg.screenshot(path='/tmp/b3.png')
    pg.evaluate('bossClose()');pg.evaluate('S.tl=100;marketOpen()');pg.wait_for_timeout(200);pg.click('#mkbuy');print('fz',pg.evaluate('S.fz'),'tl',pg.evaluate('S.tl'),pg.inner_text('#mkbuy'));pg.screenshot(path='/tmp/b4.png')
    print(er or 'нет ошибок');b.close()
