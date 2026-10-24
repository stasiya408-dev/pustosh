# -*- coding: utf-8 -*-
"""Подставной интернет для тестов поиска групп: «поисковики» и страницы t.me/имя (та же форма, что у настоящих)."""
import base64, os, re, sys, threading, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))
import net, websearch


def G(title, members, online, about='', join=False):
    return {'type': 'group', 'title': title, 'members': members, 'online': online, 'about': about, 'join': join}


PAGES = {
    'ryba_ua': G('Рыбалка Украина', 5400, 321, 'Чат рыбаков Украины'),
    'spin_all': G('Спиннинг для всех', 1200, 50, 'Всё про спиннинг'),
    'lviv_fish': G('Рибалки Львова', 80, 5, 'Рибалки Львова', join=True),
    'hunt_chat': G('Охота и егеря', 2300, 93, 'Охотники'),
    'tanks_chat': G('Танки и не только', 15000, 600, 'Танки и всё остальное'),
    'memes_games': G('Мемы про игры', 700, 29, 'Мемы'),
    'gamers_ua': G('Геймеры Украины', 3000, 217, 'Играем вместе'),
    'autoua': G('Автомеханики Украины', 4000, 100, 'Мой чат (я в нём уже состою)'),
    'tiny_group': G('Почти пустая группа', 5, 1),
    'hidden_group': G('Группа без онлайна', 1500, None, 'Онлайн скрыт'),
    'fish_channel': {'type': 'channel', 'title': 'Рыбалка новости', 'members': 90000, 'about': 'Канал, писать нельзя'},
    'some_person': {'type': 'user', 'title': 'Иван Рыбаков'},
    # gone_group: страницы нет совсем
}
# что «находят поисковики» по слову (все слова, которых тут нет, дают ryba_ua и канал)
WORDS = {
    'рыбалка': ['ryba_ua', 'autoua', 'fish_channel', 'spin_all'],
    'рибалка': ['ryba_ua', 'lviv_fish'],
    'охота': ['hunt_chat', 'some_person'],
    'игры': ['tanks_chat', 'memes_games', 'tiny_group'],
    'геймеры': ['gamers_ua', 'gone_group'],
}
DEFAULT = ['ryba_ua', 'fish_channel']

LOCK = threading.Lock()
SEARCHES = []          # (поисковик, запрос)
TME = []               # имена, страницы которых открывали
WORDS_SEEN = []        # слова по порядку первого появления
ENGINE_FAIL = {}       # поисковик -> код ответа вместо результатов (например {'brave': 429})
NET_DOWN = [False]     # нет интернета
TME_BLOCK = [0]        # сколько страниц t.me подряд отвечать «слишком часто» (429)
TME_NETFAIL = [False]  # t.me не отвечает (ошибка связи)
OTHER = []             # любые другие адреса


def reset():
    del SEARCHES[:], TME[:], WORDS_SEEN[:], OTHER[:]
    ENGINE_FAIL.clear()
    NET_DOWN[0] = False
    TME_BLOCK[0] = 0
    TME_NETFAIL[0] = False


def tme_page(name):
    p = PAGES.get(name.lower()) or PAGES.get(name)
    if not p:
        return '<html><head><title>Telegram: Contact @%s</title></head><body><div class="tgme_page"><div class="tgme_page_description">If you have <strong>Telegram</strong>, you can contact <a href="tg://resolve?domain=%s">@%s</a> right away.</div></div></body></html>' % (name, name, name)
    t = p['type']
    if t == 'group':
        extra = '%s members' % format(p['members'], ',').replace(',', ' ') + (', %d online' % p['online'] if p['online'] is not None else '')
        btn = 'Request to Join Group' if p.get('join') else 'Join Group'
    elif t == 'channel':
        extra = '%s subscribers' % format(p['members'], ',').replace(',', ' ')
        btn = 'View in Telegram'
    else:
        extra = '@' + name
        btn = 'Send Message'
    return ('<html><head><meta property="og:title" content="%s"></head><body><div class="tgme_page_wrap"><div class="tgme_page">'
            '<div class="tgme_page_photo"></div><div class="tgme_page_title" dir="auto"><span dir="auto">%s</span></div>'
            '<div class="tgme_page_extra">%s</div><div class="tgme_page_description" dir="auto">%s</div>'
            '<div class="tgme_page_action"><a class="tgme_action_button_new shine" href="tg://resolve?domain=%s">%s</a></div></div></div></body></html>'
            % (p['title'], p['title'], extra, p.get('about', ''), name, btn))


def engine_page(eid, names):
    if eid == 'ddg':
        return '<html><body>' + ''.join('<div class="result"><a class="result__a" href="//duckduckgo.com/l/?uddg=%s&amp;rut=abc">%s</a></div>'
                                         % (urllib.parse.quote('https://t.me/' + n, safe=''), n) for n in names) + '</body></html>'
    if eid == 'bing':
        out = ''
        for n in names:
            u = base64.urlsafe_b64encode(('https://t.me/' + n).encode()).decode().rstrip('=')
            out += '<li class="b_algo"><h2><a href="https://www.bing.com/ck/a?!&amp;&amp;p=x1&amp;u=a1%s&amp;ntb=1">%s</a></h2><cite>https://t.me › %s</cite></li>' % (u, n, n)
        return '<html><body><ol>' + out + '</ol></body></html>'
    return '<html><body>' + ''.join('<a href="https://t.me/%s">%s</a>' % (n, n) for n in names) + '</body></html>'


def fake_fetch(url, headers=None, timeout=20):
    if NET_DOWN[0]:
        raise net.NetError('нет связи с интернетом (тест)')
    u = urllib.parse.urlparse(url)
    host = u.netloc.lower()
    if host == 't.me':
        name = u.path.strip('/')
        with LOCK:
            TME.append(name)
            blocked = TME_BLOCK[0] > 0
            if blocked:
                TME_BLOCK[0] -= 1
        if TME_NETFAIL[0]:
            raise net.NetError('нет связи с интернетом (t.me, тест)')
        if blocked:
            return 429, 'Too Many Requests', 1
        return 200, tme_page(name), 0
    for eid, name, tpl, *_ in websearch.ENGINES:
        if urllib.parse.urlparse(tpl).netloc.lower() == host:
            q = urllib.parse.parse_qs(u.query).get('q', [''])[0]
            m = re.search(r'(?:site:t\.me )?(.+?) чат', q)
            w = m.group(1) if m else q
            with LOCK:
                SEARCHES.append((eid, q))
                if w not in WORDS_SEEN:
                    WORDS_SEEN.append(w)
            if eid in ENGINE_FAIL:
                return ENGINE_FAIL[eid], 'blocked', 0
            return 200, engine_page(eid, WORDS.get(w, DEFAULT)), 0
    OTHER.append(url)
    return 404, '', 0


def install():
    websearch.fetch = fake_fetch
