from playwright.sync_api import sync_playwright
stub="window.Telegram={WebApp:{ready(){},expand(){},initDataUnsafe:{}}};"
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':390,'height':780},has_touch=True,is_mobile=True)
    er=[];pg.on('pageerror',lambda e:er.append(str(e)))
    pg.route('**/telegram-web-app.js',lambda r:r.fulfill(body=stub,content_type='application/javascript'))
    pg.goto('file:///mnt/user-data/outputs/index.html');pg.wait_for_timeout(3500);print(pg.inner_text('#hver'))
    pg.evaluate('S.pw=9999;S.en=50;S.sv=100000;draw();$("hike").style.display="flex";hStart("field")');pg.wait_for_timeout(800)
    res=[]
    def st(ev,out,n):
        pg.evaluate('hShow("%s")'%ev)
        if out:pg.evaluate('HK.out={t:%r,c:"",end:0};HK.ph="out";hRender()'%out)
        pg.wait_for_timeout(700);k=pg.evaluate('$("hfb").dataset.k');res.append((n,k));pg.screenshot(path='/tmp/g_%s.png'%n)
    pg.wait_for_timeout(500);res.append(('trip',pg.evaluate('$("hfb").dataset.k')));pg.screenshot(path='/tmp/g_trip.png')
    st('hunt',None,'hunt');st('hunt','Выстрел гремит над степью. Олень упал.','shot');st('hunt','Олень ушёл, а ты зря измотался.','miss')
    st('glint',None,'gl');st('glint','Ты нашёл старый нож. Но рядом видны свежие следы лошадей.','knife');st('glint','В траве только битые черепки.','shards')
    st('bandit_camp','Ключ теперь твой.','keyok');st('bandit_camp','Ты задел котелок. Шум! Но ключ уже в руке.','keybad');st('tracks','Тебя заметили!','chase')
    st('trader','Ты получил пучок целебных трав.','herbs')
    print(res);print(er or 'нет ошибок');b.close()
