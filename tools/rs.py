from playwright.sync_api import sync_playwright
stub="window.Telegram={WebApp:{ready(){},expand(){},initDataUnsafe:{}}};"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':780},has_touch=True,is_mobile=True)
    er=[];pg.on('pageerror',lambda e:er.append(str(e)))
    pg.route('**/telegram-web-app.js',lambda r:r.fulfill(body=stub,content_type='application/javascript'))
    pg.add_init_script('localStorage.setItem("kozak3",JSON.stringify({pw:5000,lv:30,sv:999999,fz:7,bossKills:50,parts:5,eq:1,en:3}))')
    pg.goto('file:///mnt/user-data/outputs/index.html');pg.wait_for_timeout(3000)
    print(pg.inner_text('#hver'),pg.evaluate('[S.pw,S.lv,S.sv,S.fz,S.en,S.parts,S.bossKills,S.eq,FUSE_DMG]'),pg.inner_text('#en'))
    pg.reload();pg.wait_for_timeout(2500);print('после перезагрузки',pg.evaluate('[S.pw,S.fz,S.en]'))
    pg.evaluate('S.pw=40;draw();bossOpen()');pg.wait_for_timeout(300);pg.evaluate('bossPick(0)');pg.evaluate('S.fz=20');pg.evaluate('for(var i=0;i<4;i++)useFuse()');print('выстрелов ок',pg.evaluate('S.fz'),pg.evaluate('S.en'))
    print(er or 'нет ошибок');b.close()
