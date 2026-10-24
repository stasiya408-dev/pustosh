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
        names = ['cfg', 'net', 'gen', 'card', 'pubs', 'yt', 'cats', 'tgu', 'jobs', 'update', 'version', 'imggen', 'websearch', 'finder', 'server']
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

    def web_():
        import websearch, finder
        page = ('<div class="tgme_page_title" dir="auto"><span dir="auto">Рыбалка Украина</span></div>'
                '<div class="tgme_page_extra">5 400 members, 321 online</div>'
                '<div class="tgme_page_description" dir="auto">Чат рыбаков</div>'
                '<div class="tgme_page_action"><a class="tgme_action_button_new shine" href="tg://resolve?domain=ryba_ua">Join Group</a></div>')
        d = websearch.parse_tme(page, 'ryba_ua')
        assert d['kind'] == 'group' and d['members'] == 5400 and d['online'] == 321 and d['title'] == 'Рыбалка Украина', d
        assert websearch.parse_tme(page.replace('members', 'subscribers'), 'x')['kind'] == 'channel'
        assert websearch.parse_tme('<html>If you have Telegram, you can contact @zzzzz</html>', 'zzzzz')['kind'] == 'none'
        assert websearch.extract('<a href="https://t.me/ryba_ua">x</a> t.me/joinchat/AAA t.me/some_bot') == ['ryba_ua']
        assert len(finder.plan(['fishing', 'games'])) == 23 and not finder.plan(['other'])
        return 'разбор страниц t.me и ссылок из поисковиков работает'
    step('поиск групп в интернете: разбор страниц', web_)


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

        def lw():
            import websearch
            lines = []
            websearch.diagnose(lines.append)
            p = os.path.join(os.path.dirname(os.path.abspath(out)), 'web_probe.txt')
            with open(p, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            ok = [l for l in lines if l.startswith('проверено страниц')]
            return ok[0] if ok else 'проба записана в web_probe.txt'
        step('ЖИВОЙ тест: поиск групп в интернете (не ломает сборку)', lw)

    LINES.append('')
    LINES.append('ИТОГО: %s' % ('ВСЁ ХОРОШО' if not FAILED else 'ПРОВАЛ: ' + ', '.join(FAILED)))
    try:
        with open(out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(LINES))
    except OSError:
        pass
    print('\n'.join(LINES))
    return 1 if FAILED else 0
