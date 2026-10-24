# -*- coding: utf-8 -*-
"""Самопроверка собранной программы (запускается на сборке: PustoshMarketing.exe --selftest файл.txt)."""
import datetime, io, json, os, sys, tempfile, threading, traceback

LINES = []
FAILED = []


def step(name, fn):
    try:
        r = fn()
        LINES.append('OK   %s%s' % (name, (' — ' + str(r)) if r else ''))
    except BaseException as e:
        FAILED.append(name)
        LINES.append('FAIL %s: %s' % (name, e))
        LINES.append(''.join('     ' + l for l in traceback.format_exc().splitlines(True)))


def run(out, live=False):
    home = tempfile.mkdtemp(prefix='mkt_self_')
    os.environ['MKT_HOME'] = home
    os.environ['MKT_TG_API_ID'] = '12345'
    os.environ['MKT_TG_API_HASH'] = '0123456789abcdef0123456789abcdef'
    os.environ['MKT_IDLE_EXIT'] = '0'
    LINES.append('python %s, frozen=%s' % (sys.version.split()[0], getattr(sys, 'frozen', False)))

    def imports():
        names = ['cfg', 'net', 'gen', 'card', 'pubs', 'yt', 'cats', 'tgu', 'jobs', 'update', 'version', 'imggen', 'finder', 'server']
        for n in names:
            __import__(n)
        import version
        return 'версия ' + version.VERSION
    step('импорт всех модулей программы', imports)

    def pil():
        from PIL import Image, ImageDraw, ImageFont  # noqa
        import card
        im = Image.new('RGB', (1200, 800), (60, 40, 20))
        p = os.path.join(home, 's.jpg')
        im.save(p)
        out_p = os.path.join(home, 'card.jpg')
        card.make_card(p, 'Тугар вышел на тропу войны', 'Попробуй уложить его', 'Играть: t.me/pustosh_bot', out_p)
        sz = Image.open(out_p).size
        assert sz == (1080, 1350), sz
        f = card._font(40)
        return 'картинка 1080×1350, шрифт: %s' % getattr(f, 'path', 'встроенный (кириллицы может не быть!)')
    step('Pillow и картинка с надписью', pil)

    def tele():
        import telethon
        from telethon.tl import types as T
        from telethon import utils
        import tgu
        now = datetime.datetime.now(datetime.timezone.utc)
        ph = T.ChatPhotoEmpty()
        mega = T.Channel(id=1, title='Рыбалка', photo=ph, date=now, megagroup=True, slowmode_enabled=True,
                         default_banned_rights=T.ChatBannedRights(until_date=None, send_messages=False, send_media=True),
                         username='fish', participants_count=300)
        r = tgu.classify(mega)
        assert r and r['can_write'] and r['slow'] and r['no_photo'] and r['username'] == 'fish' and r['members'] == 300, r
        ro = T.Channel(id=2, title='Только чтение', photo=ph, date=now, megagroup=True,
                       default_banned_rights=T.ChatBannedRights(until_date=None, send_messages=True))
        assert not tgu.classify(ro)['can_write']
        ch = T.Channel(id=3, title='Чужой канал', photo=ph, date=now, broadcast=True)
        assert not tgu.classify(ch)['can_write']
        mine = T.Channel(id=4, title='Мой канал', photo=ph, date=now, broadcast=True, creator=True)
        assert tgu.classify(mine)['can_write']
        adm = T.Channel(id=5, title='Адм', photo=ph, date=now, broadcast=True, admin_rights=T.ChatAdminRights(post_messages=True))
        assert tgu.classify(adm)['can_write']
        left = T.Channel(id=6, title='Вышел', photo=ph, date=now, megagroup=True, left=True)
        assert tgu.classify(left) is None
        grp = T.Chat(id=7, title='Группа', photo=ph, participants_count=10, date=now, version=1)
        g = tgu.classify(grp)
        assert g and g['can_write'] and g['kind'] == 'group', g
        assert tgu.classify(T.User(id=8)) is None
        pid = utils.get_peer_id(mega)
        assert pid == -1000000000001, pid
        return 'telethon %s: типы и права распознаются' % telethon.__version__
    step('Telethon: типы чатов и права', tele)

    def search_():
        import datetime, telethon, tgu, finder, cats
        from telethon.tl import types as T
        from telethon import functions
        now = datetime.datetime.now(datetime.timezone.utc)
        ph = T.ChatPhotoEmpty()
        ok_ = T.Channel(id=11, title='Рыбалка Украина', photo=ph, date=now, megagroup=True, username='ryba_ua', participants_count=5400)
        r = tgu.classify_found(ok_)
        assert r and r['username'] == 'ryba_ua' and r['members'] == 5400 and r['kind'] == 'group', r
        assert tgu.classify_found(T.Channel(id=12, title='Канал', photo=ph, date=now, broadcast=True, username='chan')) is None
        assert tgu.classify_found(T.Channel(id=13, title='Без имени', photo=ph, date=now, megagroup=True)) is None
        assert tgu.classify_found(T.Channel(id=14, title='Нельзя писать', photo=ph, date=now, megagroup=True, username='ro',
                                            default_banned_rights=T.ChatBannedRights(until_date=None, send_messages=True))) is None
        assert tgu.classify_found(T.Channel(id=15, title='Мошенники', photo=ph, date=now, megagroup=True, username='sc', scam=True)) is None
        alt = T.Channel(id=16, title='Запасное имя', photo=ph, date=now, megagroup=True, usernames=[T.Username(username='alt16', editable=False, active=True)])
        assert tgu.classify_found(alt)['username'] == 'alt16'
        flags = T.Channel(id=17, title='Флаги', photo=ph, date=now, megagroup=True, username='fl', join_request=True, slowmode_enabled=True, forum=True)
        f = tgu.classify_found(flags)
        assert f['join_request'] and f['slow'] and f['forum'], f
        q = functions.contacts.SearchRequest(q='рыбалка', limit=100)
        assert q.q == 'рыбалка' and q.limit == 100
        assert len(finder.plan(['fishing', 'games'])) == 23 and not finder.plan(['other'])
        # онлайн в группах: полный профиль канала по id и access_hash, который запомнили при поиске
        hh = T.Channel(id=18, title='С ключом', photo=ph, date=now, megagroup=True, username='hh', access_hash=987654321)
        c = tgu.classify_found(hh)
        assert c['cid'] == 18 and c['hash'] == 987654321, c
        fr = functions.channels.GetFullChannelRequest(T.InputChannel(channel_id=c['cid'], access_hash=c['hash']))
        assert fr.channel.channel_id == 18 and fr.channel.access_hash == 987654321
        import inspect
        params = inspect.signature(T.ChannelFull.__init__).parameters
        for k in ('online_count', 'participants_count', 'about'):
            assert k in params, 'в ChannelFull нет поля ' + k
        return 'telethon %s: глобальный поиск, разбор групп и запрос онлайна (GetFullChannel)' % telethon.__version__
    step('Telethon: поиск новых групп', search_)

    def errors():
        import tgu
        from telethon import errors as E
        names = [n for n in tgu.NAMES if n != 'FloodWaitError' and n != 'SlowModeWaitError']
        missing = [n for n in tgu.NAMES if not hasattr(E, n)]
        fw = tgu.translate(E.FloodWaitError(request=None, capture=125))
        assert fw.kind == 'flood' and fw.wait == 125, (fw.kind, fw.wait)
        return 'нет таких классов ошибок в этой версии Telethon: %s' % (missing or 'всё на месте')
    step('Telethon: ошибки и FloodWait', errors)

    def client():
        import tgu
        t = tgu.TgUser()
        c = t._run(t._amake(''), 20)
        assert c.parse_mode is None
        return 'клиент создаётся'
    step('Telethon: создание клиента', client)

    def srv():
        import server, net
        h = server.bind(0)
        port = h.server_port
        threading.Thread(target=h.serve_forever, daemon=True).start()
        st, hh, b = net.request('GET', 'http://127.0.0.1:%d/api/state' % port, {'X-Token': server.TOKEN}, None, 10)
        j = json.loads(b.decode('utf-8'))
        assert st == 200 and j['ok'] and 'chats' in j and j['conn']['card'], j
        st, hh, b = net.request('GET', 'http://127.0.0.1:%d/' % port, None, None, 10)
        assert st == 200 and 'Пустошь Маркетинг'.encode('utf-8') in b
        return 'порт %d, интерфейс отдаётся' % port
    step('локальный сервер и интерфейс', srv)

    def cats_():
        import cats
        assert cats.guess('Рыбалка Киев') == 'fishing' and cats.guess('Автомеханики') == 'auto'
        return 'категории определяются'
    step('категории чатов', cats_)

    if live:
        def lv():
            import tgu
            t = tgu.TgUser()
            try:
                t.login_phone('+380000000001')
            except tgu.TgError as e:
                return 'ответ Телеграма понятен: %s' % e.msg
            return 'неожиданно: Телеграм принял фальшивые ключи'
        step('ЖИВОЙ тест: связь с серверами Telegram', lv)

    LINES.append('')
    LINES.append('ИТОГО: %s' % ('ВСЁ ХОРОШО' if not FAILED else 'ПРОВАЛ: ' + ', '.join(FAILED)))
    try:
        with open(out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(LINES))
    except OSError:
        pass
    print('\n'.join(LINES))
    return 1 if FAILED else 0
