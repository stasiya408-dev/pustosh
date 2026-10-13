from playwright.sync_api import sync_playwright
stub="window.Telegram={WebApp:{ready(){},expand(){},initDataUnsafe:{}}};"
RUN='''(function(){var res={runs:0,ok:0,bad:[],ev:{}};
function inv(t){var h=S.hike;if(!h)return;if(!(h.hp>=0&&h.hp<=h.hpm))res.bad.push(t+" hp");if(!(h.st>=0&&h.st<=100))res.bad.push(t+" st");if(h.food<0||h.wat<0||h.fz<0)res.bad.push(t+" res");if(h.step>HLOC[h.loc].len)res.bad.push(t+" step")}
for(var i=0;i<45;i++){var loc=["field","oak","farm"][i%3];S.lv=R(1,12);S.pw=9999;S.en=MAXEN;S.sv=6000;S.fz=R(0,6);S.bag={};HPREP={food:1,wat:1,sp:R(0,2)};hikeOpen();hStart(loc);var n=0;
while(S.hike&&S.hike.ph!="res"&&n<900){n++;var h=S.hike;inv(loc+n);var ph=h.ph;
if(ph=="trip"){if(h.hp<50&&hHave("herbs")){hView("bag");hHerb();hView(null)}else if(h.st<25&&h.food>0){hView("bag");hEat();hView(null)}else if(Math.random()<.2)hLook();else hStep()}
else if(ph=="ev"){res.ev[h.ev]=1;var e=HEVT[h.ev],o=[];e.ch.forEach(function(c,k){if(h.dc[h.ev+k])return;if(c.need&&c.need.item&&!hHave(c.need.item))return;if(c.need&&c.need.food&&h.food<c.need.food)return;if(c.cost&&S.sv<c.cost)return;if(c.sp&&h.fz<c.sp)return;o.push(k)});if(o.length)hChoice(o[R(0,o.length-1)]);else hLeave()}
else if(ph=="boss"){var a=Math.random();if(a<.35)hBossGo("fight");else if(a<.6){hBossGo("friends");hBossGo("fight")}else hBossGo("run")}else if(ph=="out")hNext();else if(ph=="fight"){if(h.hp<35&&h.fz>0)hAct("gun");else hAct("hit")}
else if(ph=="camp"){hCampAct("fire");hCampAct("eat");hSleep()}}
if(S.hike&&S.hike.ph=="res"){res.runs++;if(S.hike.res.ok)res.ok++;hDone()}else res.bad.push(loc+" не завершился")}
res.ev=Object.keys(res.ev).length;return res})()'''
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    pg=b.new_page(viewport={'width':390,'height':700},has_touch=True,is_mobile=True)
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.route('**/telegram-web-app.js',lambda r:r.fulfill(body=stub,content_type='application/javascript'))
    pg.goto('file:///mnt/user-data/outputs/index.html'); pg.wait_for_timeout(700)
    print('версия:',pg.inner_text('#hver'),'| случайные походы:',pg.evaluate(RUN))
    pg.evaluate('S.en=50;S.sv=1000;draw()')
    for i,nm in enumerate(['Поход','Майдан','Курень']):
        e0=pg.evaluate('S.en=50;S.en'); pg.evaluate(f"document.querySelectorAll('.map .loc')[{i}].click()"); pg.wait_for_timeout(150)
        if i==0: print('Поход открывается:',pg.is_visible('#hike')); pg.click('#hike .tbar button')
        else: print(nm,'энергия',e0,'→',pg.evaluate('S.en'))
    pg.click('.nb[data-a=tav]'); pg.wait_for_timeout(300); print('кости:',pg.is_visible('#dice')); pg.click('#dice .hit:nth-of-type(2)')
    pg.click('.nb[data-a=boss]'); pg.wait_for_timeout(400); print('босс:',pg.is_visible('#bmenu'))
    print('ошибки',errs or 'нет'); b.close()
