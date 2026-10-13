from playwright.sync_api import sync_playwright
stub="window.Telegram={WebApp:{ready(){},expand(){},initDataUnsafe:{}}};"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':780},has_touch=True,is_mobile=True)
    er=[];pg.on('pageerror',lambda e:er.append(str(e)))
    pg.route('**/telegram-web-app.js',lambda r:r.fulfill(body=stub,content_type='application/javascript'))
    pg.goto('file:///mnt/user-data/outputs/index.html');pg.wait_for_timeout(2500)
    print(pg.inner_text('#hver'),pg.evaluate('DAYLIM'))
    print('drop',pg.evaluate('(function(){var c={};for(var i=0;i<20000;i++){var d=herbDrop()||"none";c[d]=(c[d]||0)+1}return c})()'))
    print('hike drops',pg.evaluate('(function(){var n=0;S.bag={};for(var i=0;i<200;i++){S.pw=9999;S.en=MAXEN;S.sv=6000;HPREP={food:1,wat:1,sp:0};hikeOpen();hStart("field");if(S.hike)hFinish(1);hDone()}return JSON.stringify([S.bag.kropiva,S.bag.chebrets,S.bag.rozryv])})()'))
    pg.evaluate('S.pw=40;S.fz=50;S.bag.kropiva=2;S.bag.chebrets=2;draw();bossOpen()');pg.wait_for_timeout(400)
    pg.evaluate('bossPick(0)');pg.wait_for_timeout(300);pg.screenshot(path='/tmp/h1.png')
    print('dlg',pg.is_visible('#hdg'))
    pg.click('#hdg button[data-h=chebrets]');pg.wait_for_timeout(500)
    print('hb',pg.evaluate('S.hb'),'bag',pg.evaluate('S.bag.chebrets'),'fight',pg.is_visible('#boss'))
    pg.evaluate('S.mode="grp";bossCheck();B().hp=B().max=99999')
    ds=[]
    for i in range(5):
        h0=pg.evaluate('B().hp');pg.evaluate('useFuse()');ds.append(h0-pg.evaluate('B().hp'))
    print('chebrets shots(grp incl bots)',ds)
    pg.evaluate('S.mode="solo";bossCheck();S.hb="kropiva";B().hp=B().max=99999');h0=pg.evaluate('B().hp');pg.evaluate('useFuse()');print('kropiva solo dmg',h0-pg.evaluate('B().hp'),'base',pg.evaluate('FUSE_DMG'))
    pg.evaluate('B().hp=1;useFuse()');print('after kill hb',pg.evaluate('S.hb'))
    pg.evaluate('bossClose()')
    # cache event
    print(pg.evaluate('(function(){S.bag={rozryv:1};S.pw=9999;S.en=MAXEN;S.sv=6000;HPREP={food:1,wat:1,sp:0};hikeOpen();hStart("oak");hShow("cache");var e=HEVT.cache;var i=e.ch.findIndex(function(c){return c.need&&c.need.item=="rozryv"});hChoice(i);return JSON.stringify([HK.out.t,S.bag.rozryv,HK.bag.rozryv,HK.sv])})()'))
    pg.screenshot(path='/tmp/h2.png')
    print(er or 'нет ошибок');b.close()
