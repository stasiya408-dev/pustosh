# -*- coding: utf-8 -*-
"""Поиск публичных групп Telegram В ИНТЕРНЕТЕ. Аккаунт Telegram здесь не используется вообще:
  1) слова по теме ищутся в поисковиках (DuckDuckGo, Bing, Mojeek, Brave) и каталогах, из ответов достаются имена вида t.me/имя;
  2) каждое имя проверяется по публичной странице https://t.me/имя (её видит любой человек в браузере):
     там написаны название, сколько участников и сколько сейчас онлайн, описание и это группа или канал.
Только стандартная библиотека."""
import base64, gzip, html.parser, random, re, threading, time, urllib.parse
import net

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
TME = 'https://t.me/'
MIN_MEMBERS = 10           # совсем пустые группы не берём
BLOCK_MIN = 5              # сколько секунд ждать, если t.me просит подождать (и не сказал сколько)

COOL = 25                  # секунд «отдыха» поисковика после отказа (умножается на число отказов подряд)

# Источники: (id, название, адрес с {q}, как спрашиваем про слово w; None = TEMPLATES)
ENGINES = [
    ('ddg', 'DuckDuckGo', 'https://html.duckduckgo.com/html/?q={q}', None),
    ('bing', 'Bing', 'https://www.bing.com/search?q={q}&count=50&setlang=ru', None),
    ('lyzem', 'Lyzem', 'https://lyzem.com/search?q={q}', ['{w}', '{w} чат']),     # поисковик по Telegram
    ('mojeek', 'Mojeek', 'https://www.mojeek.com/search?q={q}', None),
    ('brave', 'Brave', 'https://search.brave.com/search?q={q}&source=web', None),
]
# Как спрашиваем у обычного поисковика про слово w
TEMPLATES = ['site:t.me {w} чат', '{w} чат telegram t.me']

# Служебные адреса t.me, которые не являются именами групп
RESERVED = {'joinchat', 'addstickers', 'addemoji', 'share', 's', 'c', 'proxy', 'socks', 'iv', 'login', 'setlanguage', 'addtheme', 'boost', 'giftcode',
            'invoice', 'confirmphone', 'bg', 'msg', 'contact', 'addlist', 'm', 'web', 'apps', 'privacy', 'tos', 'blog', 'faq', 'dl', 'download',
            'auth', 'username', 'telegram', 'support', 'botfather', 'durov', 'favicon', 'img', 'css', 'js', 'api', 'tgcatalog', 'stickers'}
NAME = r'[A-Za-z][A-Za-z0-9_]{3,30}[A-Za-z0-9]'
LINK_RE = re.compile(r'(?<![\w-])(?:t\.me|telegram\.me|telegram\.dog)/(?:s/)?(' + NAME + r')(?![A-Za-z0-9_])', re.I)
TG_RE = re.compile(r'tg://resolve\?domain=(' + NAME + r')(?![A-Za-z0-9_])', re.I)
CAT_RE = re.compile(r'tgstat\.[a-z]+/(?:chat|channel)/@(' + NAME + r')(?![A-Za-z0-9_])', re.I)
CK_RE = re.compile(r'[?&;]u=a1([A-Za-z0-9_\-]+)')           # Bing прячет адрес результата в base64


class Blocked(Exception):
    """t.me или поисковик просит подождать (слишком частые запросы)."""
    def __init__(self, wait=0):
        Exception.__init__(self, 'просит подождать')
        self.wait = wait


def fetch(url, headers=None, timeout=20):
    """Возвращает (код, текст, секунд_ждать). Сетевые ошибки — net.NetError. Тесты подменяют эту функцию."""
    h = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8', 'Accept-Language': 'ru,en;q=0.8'}
    h.update(headers or {})
    try:
        st, hdr, body = net.request('GET', url, h, None, timeout)
    except net.NetError:
        raise
    except Exception as e:
        raise net.NetError('нет связи с интернетом (%s)' % (e,))
    try:
        if hdr and 'gzip' in (hdr.get('Content-Encoding') or '').lower():
            body = gzip.decompress(body)
    except Exception:
        pass
    cs = 'utf-8'
    try:
        m = re.search(r'charset=([\w-]+)', (hdr.get('Content-Type') or '') if hdr else '', re.I)
        if m:
            cs = m.group(1)
        text = body.decode(cs, 'replace')
    except LookupError:
        text = body.decode('utf-8', 'replace')
    wait = 0
    try:
        wait = int((hdr.get('Retry-After') or 0)) if hdr else 0
    except (TypeError, ValueError):
        wait = 0
    return st, text, wait


# ---------------------------------------------------------------- имена из ответа
def extract(text):
    """Все имена вида t.me/имя в тексте страницы (вместе с адресами, зашифрованными в ссылках поисковиков). Порядок сохраняется."""
    out, seen = [], set()

    def add(n):
        k = n.lower()
        if k in seen or k in RESERVED or k.endswith('bot'):
            return
        seen.add(k)
        out.append(n)
    t2 = html.unescape(text or '')
    chunks = [text or '', t2, urllib.parse.unquote(t2)]
    for m in CK_RE.finditer(t2):
        try:
            b = m.group(1)
            raw = base64.urlsafe_b64decode(b + '=' * (-len(b) % 4)).decode('utf-8', 'replace')
            chunks.append(raw)
            chunks.append(urllib.parse.unquote(raw))
        except Exception:
            pass
    for ch in chunks:
        for rx in (LINK_RE, TG_RE, CAT_RE):
            for m in rx.finditer(ch):
                add(m.group(1))
    return out


# ---------------------------------------------------------------- поисковики
class Engine:
    def __init__(self, eid, name, url, templates=None):
        self.id, self.name, self.url = eid, name, url
        self.templates = list(templates or TEMPLATES)
        self.ok = self.found = self.bad = self.empty = 0
        self.off = False
        self.err = ''
        self.cool_until = 0.0

    def success(self, n):
        self.ok += 1
        self.bad = 0
        if n:
            self.empty = 0
            self.found += n
        else:
            self.empty += 1
            if self.empty >= 4:
                self.off, self.err = True, 'не отдаёт ссылки (возможно, просит капчу)'

    def fail(self, msg):
        """Отказ (код не 200, нет связи): сначала поисковик отдыхает всё дольше, после трёх подряд выключается на этот запуск."""
        self.bad += 1
        self.err = msg
        if self.bad >= 3:
            self.off = True
        else:
            self.cool_until = time.time() + COOL * self.bad

    @property
    def cooling(self):
        return not self.off and self.cool_until > time.time()

    def report(self):
        return {'id': self.id, 'name': self.name, 'ok': self.ok, 'found': self.found, 'off': self.off, 'cool': self.cooling,
                'err': self.err if (self.off or not self.ok or self.cooling) else ''}


def make_engines():
    return [Engine(*e) for e in ENGINES]


def search_word(word, engines, pause, stop=lambda: False):
    """Ищет слово во всех включённых поисковиках (поисковики работают одновременно, каждый — по очереди с паузами).
    Возвращает {имя_в_нижнем_регистре: (имя, поисковик)}."""
    res, lock = {}, threading.Lock()

    def work(e):
        for ti, t in enumerate(e.templates):
            if stop() or e.off or e.cooling:
                return
            if ti:
                time.sleep(pause())
            try:
                st, text, wait = fetch(e.url.format(q=urllib.parse.quote_plus(t.format(w=word))))
            except net.NetError as ex:
                e.fail(ex.msg)
                continue
            if st != 200:
                e.fail('ответ сервера %s' % st)
                continue
            names = extract(text)
            with lock:
                for n in names:
                    res.setdefault(n.lower(), (n, e.name))
            e.success(len(names))
    ths = [threading.Thread(target=work, args=(e,), daemon=True) for e in engines if not e.off and not e.cooling]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    return res


# ---------------------------------------------------------------- страница t.me/имя
def _txt(frag):
    frag = re.sub(r'<br\s*/?>', '\n', frag or '', flags=re.I)
    frag = re.sub(r'<[^>]+>', '', frag)
    return html.unescape(frag).replace('\xa0', ' ').strip()


def _div(text, cls):
    m = re.search(r'<div class="tgme_page_%s"[^>]*>(.*?)</div>' % cls, text, re.S)
    return _txt(m.group(1)) if m else ''


NUM = r'(\d[\d\s   ,\.]*)'
MEM_RE = re.compile(NUM + r'\s*(?:members?|участник\w*|учасник\w*)', re.I)
SUB_RE = re.compile(NUM + r'\s*(?:subscribers?|подписчик\w*|підписник\w*)', re.I)
ON_RE = re.compile(NUM + r'\s*(?:online|в сети|онлайн|у мережі)', re.I)


def _num(s):
    d = re.sub(r'\D', '', s or '')
    return int(d) if d else None


def parse_tme(text, username=''):
    """Разбор страницы t.me/имя -> {kind: group|channel|user|bot|other|none, title, members, online, about, join_request}."""
    title = _div(text, 'title')
    if not title:
        m = re.search(r'<meta property="og:title" content="([^"]*)"', text)
        t = html.unescape(m.group(1)).strip() if m else ''
        title = '' if t.lower().startswith('telegram') else t
    extra = _div(text, 'extra')
    about = _div(text, 'description')
    if not about:
        m = re.search(r'<meta property="og:description" content="([^"]*)"', text)
        about = html.unescape(m.group(1)).strip() if m else ''
    mem, sub, onl = MEM_RE.search(extra), SUB_RE.search(extra), ON_RE.search(extra)
    if mem:
        kind = 'group'
    elif sub:
        kind = 'channel'
    elif extra.startswith('@'):
        kind = 'bot' if username.lower().endswith('bot') else 'user'
    elif title:
        kind = 'other'
    else:
        kind = 'none'
    btn = re.search(r'tgme_action_button_new[^>]*>(.*?)</a>', text, re.S)
    label = _txt(btn.group(1)).lower() if btn else ''
    return {'kind': kind, 'title': title, 'members': _num(mem.group(1)) if mem else (_num(sub.group(1)) if sub else None),
            'online': _num(onl.group(1)) if onl else None, 'about': about[:300],
            'join_request': ('request' in label or 'заявк' in label or 'заявок' in label)}


def check(username):
    """Открывает t.me/имя и разбирает страницу. Blocked — просят подождать; net.NetError — нет связи."""
    st, text, wait = fetch(TME + username, {'Accept-Language': 'en-US,en;q=0.9'}, 20)
    if st == 429:
        raise Blocked(wait or 20)
    if st >= 500:
        raise net.NetError('t.me ответил %s' % st)
    if st != 200:
        return {'kind': 'none', 'title': '', 'members': None, 'online': None, 'about': '', 'join_request': False}
    if 'tgme_page' not in text:                      # не страница Telegram (заглушка, капча)
        raise Blocked(30)
    return parse_tme(text, username)


def verify_many(names, stop, pause, progress=None, workers=2):
    """Проверяет имена по странице t.me. Возвращает ({имя: описание}, просили_подождать, ошибка_связи).
    Если t.me два раза подряд просит подождать, останавливается (непроверенные потом проверятся при следующем поиске)."""
    todo = list(names)
    out, lock = {}, threading.Lock()
    state = {'blocked': 0, 'abort': False, 'neterr': '', 'neterr_n': 0, 'done': 0, 'resume': 0.0}

    def work():
        while True:
            with lock:
                if state['abort'] or stop() or not todo:
                    return
                n = todo.pop(0)
            now = time.time()
            if state['resume'] > now:                # кто-то получил «подождите»: ждём все
                time.sleep(min(60, state['resume'] - now))
            retry = False
            try:
                d = check(n)
                with lock:
                    out[n] = d
                    state['blocked'] = 0
                    state['neterr_n'] = 0
            except Blocked as b:
                with lock:
                    state['blocked'] += 1
                    if state['blocked'] >= 2:
                        state['abort'] = True
                    else:
                        state['resume'] = time.time() + min(60, max(BLOCK_MIN, b.wait))
                        todo.insert(0, n)
                        retry = True
            except net.NetError as ex:
                with lock:
                    state['neterr_n'] += 1
                    state['neterr'] = ex.msg
                    if state['neterr_n'] >= 4:
                        state['abort'] = True
            if retry:
                continue
            with lock:
                state['done'] += 1
                k = state['done']
            if progress:
                try:
                    progress(min(k, len(names)), len(names))
                except Exception:
                    pass
            time.sleep(pause())
    ths = [threading.Thread(target=work, daemon=True) for _ in range(max(1, workers))]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    return out, state['blocked'] >= 2, state['neterr'] if state['neterr_n'] >= 4 else ''


# ---------------------------------------------------------------- живая проверка для самопроверки сборки
PROBE_URLS = [
    ('Yahoo', 'https://search.yahoo.com/search?p={q}'),
    ('DuckDuckGo lite', 'https://lite.duckduckgo.com/lite/?q={q}'),
    ('Bing (cn)', 'https://cn.bing.com/search?q={q}&setmkt=ru-RU'),
    ('Qwant (api)', 'https://api.qwant.com/v3/search/web?q={q}&count=10&locale=ru_RU&offset=0&device=desktop'),
    ('Yandex', 'https://yandex.ru/search/?text={q}'),
    ('Lyzem стр.2 (p)', 'https://lyzem.com/search?q={w}&p=2'),
    ('Lyzem стр.2 (page)', 'https://lyzem.com/search?q={w}&page=2'),
    ('tgramsearch', 'https://tgramsearch.com/search?query={w}'),
    ('tgramsearch en', 'https://en.tgramsearch.com/search?query={w}'),
    ('tgramsearch чаты', 'https://tgramsearch.com/search?query={w}&type=chats'),
    ('teleteg ?s', 'https://teleteg.com/?s={w}'),
    ('teleteg search', 'https://teleteg.com/search?q={w}'),
    ('telesearch', 'https://telesearch.me/search?q={w}'),
    ('groupda', 'https://groupda.com/tgme/?q={w}'),
    ('tdirectory', 'https://tdirectory.me/?search={w}'),
    ('tdirectory groups', 'https://tdirectory.me/groups?search={w}'),
    ('xtea', 'https://xtea.io/ts_ru.html?q={w}'),
    ('tgstat поиск', 'https://tgstat.ru/search?q={w}&sort=members&type=chat'),
    ('telemetr каталог', 'https://telemetr.me/catalog/activity/fishing/'),
    ('combot top чаты', 'https://combot.org/top/telegram/chats?q={w}'),
]


def _probe_url(write, name, url, deep=False):
    """Одна проба адреса для журнала: код, длина, имена t.me, @имена и (для подробной пробы) вид ссылок в ответе."""
    try:
        st, text, _ = fetch(url, None, 20)
        names = extract(text)
        at = set(re.findall(r'@([A-Za-z][A-Za-z0-9_]{4,31})', text))
        write('%s: код %s, длина %d, имён t.me: %d: %s; @имён: %d%s' % (name, st, len(text), len(names), ', '.join(names[:10]), len(at),
                                                                    (' (' + ', '.join(sorted(at)[:8]) + ')') if at and not names else ''))
        low = text.lower()
        if any(w in low for w in ('captcha', 'unusual traffic', 'are you a robot', 'verify you are', 'anomaly')):
            write('    | похоже на капчу/проверку на робота')
        if deep:
            if not names or 'bing' in url:
                hrefs = []
                for h in re.findall(r'href="(https?://[^"]+)"', html.unescape(text)):
                    if h not in hrefs and not re.search(r'\.(css|js|png|jpg|ico|svg)(\?|$)', h):
                        hrefs.append(h)
                write('    | ссылок в ответе: %d; первые: %s' % (len(hrefs), ' ; '.join(x[:110] for x in hrefs[:10])))
                cites = [re.sub(r'<[^>]+>', '', c)[:70] for c in re.findall(r'<cite[^>]*>(.*?)</cite>', text, re.S)[:10]]
                if cites:
                    write('    | cite: ' + ' ; '.join(cites))
                if len(text) < 6000:
                    write('    | начало ответа: ' + re.sub(r'\s+', ' ', text[:400]))
            elif names:
                i = text.lower().find('t.me/' + names[0].lower())
                write('    | вокруг первого t.me: ' + re.sub(r'\s+', ' ', text[max(0, i - 200):i + 200]))
    except Exception as e:
        write('%s: ОШИБКА %s' % (name, e))


def diagnose(write):
    """Сходить в интернет по-настоящему и записать, что отвечает (для журнала сборки). Ничего не ломает."""
    t0 = time.time()
    write('== страницы t.me ==')
    for nm in ('TelethonChat', 'durov', 'pustosh_net_takoj_gruppy_x'):
        try:
            st, text, _ = fetch(TME + nm, {'Accept-Language': 'en-US,en;q=0.9'}, 20)
            info = parse_tme(text, nm)
            write('t.me/%s: код %s, длина %d, разбор %s' % (nm, st, len(text), info))
            lines = [l.strip()[:200] for l in text.splitlines() if 'tgme_page' in l or 'og:title' in l]
            for l in lines[:14]:
                write('    | ' + l)
        except Exception as e:
            write('t.me/%s: ОШИБКА %s' % (nm, e))
    write('== источники (слово «рыбалка») ==')
    for e in make_engines():
        for t in e.templates:
            q = t.format(w='рыбалка')
            _probe_url(write, '%s [%s]' % (e.name, q), e.url.format(q=urllib.parse.quote_plus(q)), deep=True)
            time.sleep(2.5)
    write('== другие адреса (проба, слово «рыбалка») ==')
    for name, url in PROBE_URLS:
        _probe_url(write, name, url.format(w=urllib.parse.quote('рыбалка'), q=urllib.parse.quote_plus('site:t.me рыбалка чат')))
        time.sleep(0.8)
    write('== сквозной прогон: слова «рыбалка» и «геймеры», все источники, проверка t.me ==')
    try:
        engines = make_engines()
        allnames = {}
        for w in ('рыбалка', 'геймеры'):
            cands = search_word(w, engines, lambda: 2.0)
            write('слово «%s»: кандидатов %d; источники: %s' % (w, len(cands), [e.report() for e in engines]))
            for k, v in cands.items():
                allnames.setdefault(k, v)
        names = [v[0] for v in list(allnames.values())[:40]]
        infos, blocked, neterr = verify_many(names, lambda: False, lambda: 0.4)
        groups = [(n, i) for n, i in infos.items() if i['kind'] == 'group']
        kinds = {}
        for i in infos.values():
            kinds[i['kind']] = kinds.get(i['kind'], 0) + 1
        write('проверено страниц: %d из %d, виды: %s, просили подождать: %s, ошибка связи: %s' % (len(infos), len(names), kinds, blocked, neterr or 'нет'))
        by = {}
        for n in names:
            by.setdefault(allnames[n.lower()][1], []).append(n)
        for en, lst in by.items():
            gl = [n for n in lst if (infos.get(n) or {}).get('kind') == 'group']
            write('  от «%s»: имён %d, из них групп %d' % (en, len(lst), len(gl)))
        for n, i in groups[:15]:
            write('  группа t.me/%s: %s | участников %s | онлайн %s | %s' % (n, i['title'], i['members'], i['online'], allnames.get(n.lower(), ('', '?'))[1]))
    except Exception as e:
        write('сквозной прогон: ОШИБКА %s' % e)
    write('время проверки: %.0f с' % (time.time() - t0))
