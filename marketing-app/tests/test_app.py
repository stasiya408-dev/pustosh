# -*- coding: utf-8 -*-
"""Проверка всей программы на поддельных серверах. Запуск: python tests/test_app.py"""
import io, json, os, shutil, sys, tempfile, threading, time, urllib.request, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(os.path.dirname(HERE), 'app')
sys.path.insert(0, APP)
sys.path.insert(0, HERE)
import fake
srv_fake, ST = fake.start()
BASE = 'http://127.0.0.1:%d' % ST.port
HOME = tempfile.mkdtemp(prefix='mkt_test_')
os.environ.update({
    'MKT_HOME': HOME, 'MKT_TG_IMPL': 'fake_tgu:FakeTg', 'MKT_IDLE_EXIT': '0',
    'MKT_ANTHROPIC_URL': BASE, 'MKT_OPENAI_URL': BASE, 'MKT_THREADS_BASE': BASE, 'MKT_THREADS_AUTH_URL': BASE + '/oauth/authorize', 'MKT_THREADS_POLL': '0.02',
    'MKT_GITHUB_API': BASE, 'MKT_YT_AUTH_URL': BASE + '/auth', 'MKT_YT_TOKEN_URL': BASE + '/token', 'MKT_YT_UPLOAD_URL': BASE + '/upload/youtube/v3/videos',
    'MKT_UPDATE_URL': BASE + '/upd', 'MKT_BASE_DEPS': 'deps-A',
})
import cfg, net, server, jobs, update, version, tgu, cats, yt, gen, card, imggen, finder, fake_tgu  # noqa
from PIL import Image

httpd = server.bind(0)
PORT = httpd.server_port
threading.Thread(target=httpd.serve_forever, daemon=True).start()
jobs.random_pause = lambda a, b: 0.05
OKS, FAILS = [], []


def ok(cond, label, extra=''):
    (OKS if cond else FAILS).append(label)
    print(('  ✔ ' if cond else '  ✘ ') + label + ((' — ' + str(extra)[:300]) if (extra and not cond) else ''))


def call(method, path, body=None, token=True, host=None, raw=None, headers=None):
    h = {'X-Token': server.TOKEN} if token else {}
    if host:
        h['Host'] = host
    h.update(headers or {})
    data = raw
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        h['Content-Type'] = 'application/json'
    st, hh, b = net.request(method, 'http://127.0.0.1:%d%s' % (PORT, path), h, data, 120)
    try:
        return st, json.loads(b.decode('utf-8'))
    except Exception:
        return st, b


def api(path, body=None, method=None):
    st, j = call(method or ('GET' if body is None else 'POST'), path, body)
    return j if isinstance(j, dict) else {'ok': False, 'raw': j}


def state():
    return api('/api/state')


def jpg(w=1600, h=900):
    im = Image.new('RGB', (w, h), (70, 40, 20))
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    for i in range(0, w, 80):
        d.rectangle([i, h // 9, i + 40, h - h // 9], fill=(200, 120 + i % 100, 40))
    b = io.BytesIO()
    im.save(b, 'JPEG')
    return b.getvalue()


def wait_job(timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        j = state()['job']
        if j and j['state'] != 'running':
            return j
        time.sleep(0.1)
    return state()['job']


def wait_extra(timeout=30):
    t0 = time.time()
    while time.time() - t0 < timeout:
        x = state()['extra']
        if x['state'] != 'running':
            return x
        time.sleep(0.1)
    return state()['extra']


def gen_files():
    return [f for f in os.listdir(cfg.MEDIA) if f.startswith(('gen_', 'ref_'))]


def by(job, key):
    return [i for i in job['items'] if i['key'] == key][0]


TG = server.TG
print('\n[1] Защита окна')
st, j = call('GET', '/api/state', token=False)
ok(st == 401, 'без ключа окна API закрыт', st)
st, j = call('GET', '/api/state', host='evil.example.com')
ok(st == 403, 'чужой адрес (DNS-rebinding) отклоняется', st)
st, b = call('GET', '/')
ok(st == 200 and b'__TOKEN__' not in b and server.TOKEN.encode() in b and 'Пустошь Маркетинг'.encode() in b, 'главная страница отдаётся с ключом окна')
st, j = call('GET', '/media/../data.json')
ok(st in (404, 401) or not isinstance(j, dict) or j.get('ok') is False, 'из media нельзя достать чужие файлы')
st, j = call('GET', '/api/nothing')
ok(st == 404, 'неизвестная команда -> 404')

print('\n[2] Настройки')
r = api('/api/settings', {'ANTHROPIC_API_KEY': 'good-key', 'GAME_BOT_LINK': 'https://t.me/pustosh_bot', 'GITHUB_TOKEN': 'ghp_test',
                           'GITHUB_MEDIA_REPO': 'me/media', 'THREADS_APP_ID': 'APP', 'THREADS_APP_SECRET': 'SEC',
                           'THREADS_REDIRECT_URI': 'https://example.github.io/pustosh/', 'TG_API_ID': '1234567', 'TG_API_HASH': 'a' * 32, 'EVIL': 'x'})
s = r['settings']
ok(s['ANTHROPIC_API_KEY']['set'] and s['ANTHROPIC_API_KEY']['hint'].startswith('••••'), 'секретный ключ сохранён и скрыт', s['ANTHROPIC_API_KEY'])
ok('good-key' not in json.dumps(r), 'ключ не уходит в окно открытым текстом')
ok(s['GAME_BOT_LINK'] == 'https://t.me/pustosh_bot' and 'EVIL' not in cfg.S['settings'], 'обычные настройки сохраняются, лишние нет')
r = api('/api/settings', {'ANTHROPIC_API_KEY': ''})
ok(r['settings']['ANTHROPIC_API_KEY']['set'], 'пустое поле не стирает сохранённый ключ')
ok(r['conn']['ai'] and r['conn']['host'] and r['conn']['threads']['app'], 'подключения видят настройки')
with open(os.path.join(HOME, 'data.json'), encoding='utf-8') as f:
    ok(json.load(f)['settings']['GITHUB_TOKEN'] == 'ghp_test', 'настройки лежат на диске')

print('\n[3] Telegram: вход')
ok(state()['conn']['tg']['state'] == 'need_phone' and state()['conn']['tg']['creds'], 'до входа: нужен номер, ключи есть')
r = api('/api/tg/phone', {'phone': '+000123'})
ok(r['ok'] is False and 'Неверный номер' in r['error'], 'плохой номер: понятная ошибка')
r = api('/api/tg/phone', {'phone': '+380501234567'})
ok(r['tg']['state'] == 'need_code', 'номер принят -> ждём код')
r = api('/api/tg/code', {'code': '00000'})
ok(r['ok'] is False and 'Неверный код' in r['error'], 'неверный код отклонён')
r = api('/api/tg/code', {'code': '99999'})
ok(r['tg']['state'] == 'need_password', 'аккаунт с двухэтапной защитой просит пароль')
r = api('/api/tg/password', {'password': 'bad'})
ok(r['ok'] is False and 'пароль' in r['error'].lower(), 'неверный пароль отклонён')
r = api('/api/tg/password', {'password': 'secret'})
ok(r['tg']['state'] == 'ready' and 'Тест' in r['tg']['me'], 'вход выполнен')

print('\n[4] Telegram: загрузка чатов и категории')
r = api('/api/tg/load', {})
ok(r['total'] == 13 and r['can_write'] == 11, 'загружено 13 чатов, писать можно в 11', (r['total'], r['can_write']))
chats = {c['id']: c for c in r['state']['chats']}
exp = {'-1001': 'fishing', '-1002': 'auto', '-1003': 'games', '-1005': 'cossacks', '-1007': 'humor', '-1009': 'sport', '-1012': 'fishing'}
bad = {k: (chats[k]['cat'], v) for k, v in exp.items() if chats[k]['cat'] != v}
ok(not bad, 'категории определились по названиям', bad)
ok(not chats['-1004']['can_write'] and not chats['-1008']['can_write'], 'чаты без права писать помечены')
r = api('/api/tg/chat', {'id': '-1004', 'sel': True})
ok(r['ok'] is False, 'в чат без права писать выбрать нельзя')
for cid in ('-1001', '-1002', '-1006'):
    api('/api/tg/chat', {'id': cid, 'sel': True})
r = api('/api/tg/chat', {'id': '-1013', 'cat': 'humor'})
c = {c['id']: c for c in state()['chats']}
ok(c['-1013']['cat'] == 'humor' and c['-1013']['manual'], 'категорию можно поменять вручную')
api('/api/tg/load', {})
c = {c['id']: c for c in state()['chats']}
ok(c['-1013']['cat'] == 'humor' and c['-1001']['sel'] and c['-1002']['sel'], 'повторная загрузка не сбрасывает выбор и ручные категории')
r = api('/api/cats', {'op': 'add', 'name': 'Мото и байкеры'})
newc = [x for x in r['cats'] if x['name'] == 'Мото и байкеры']
ok(len(newc) == 1 and r['cats'][-1]['id'] == 'other', 'своя категория добавлена перед «Другое»')
api('/api/tg/chat', {'id': '-1013', 'cat': newc[0]['id']})
r = api('/api/cats', {'op': 'rename', 'id': newc[0]['id'], 'name': 'Мотоциклисты'})
ok(any(x['name'] == 'Мотоциклисты' for x in r['cats']), 'категорию можно переименовать')
r = api('/api/cats', {'op': 'delete', 'id': newc[0]['id']})
c = {c['id']: c for c in r['chats']}
ok(c['-1013']['cat'] == 'other', 'при удалении категории чаты уходят в «Другое»')
r = api('/api/cats', {'op': 'delete', 'id': 'other'})
ok(r['ok'] is False, '«Другое» удалить нельзя')
r = api('/api/cats', {'op': 'add', 'name': 'Игры'})
ok(r['ok'] is False, 'дубликат категории отклонён')
r = api('/api/tg/bulk', {'ids': ['-1005', '-1007'], 'sel': True})
ok(r['changed'] == 2, 'массовый выбор работает')
api('/api/tg/bulk', {'ids': ['-1005', '-1007'], 'sel': False})
r = api('/api/tg/recat', {'all': True})
ok(r['ok'], 'автоопределение категорий заново')

print('\n[4б] Поиск новых групп в интернете и база найденных')
import fake_web, websearch, copy, base64, urllib.parse
fake_web.install()
REAL_PAUSE = finder.random_pause
finder.random_pause = lambda a, b: 0.02
websearch.BLOCK_MIN = 0.05
websearch.COOL = 0          # в обычных проверках поисковик после отказа не отдыхает


def wait_find(timeout=30):
    t0 = time.time()
    while time.time() - t0 < timeout:
        f = state()['find']
        if f['state'] != 'running':
            return f
        time.sleep(0.05)
    return state()['find']


def new_run(ids):
    fake_web.reset()
    r = api('/api/find/start', {'cats': ids})
    return r if not r.get('ok', True) else wait_find()


def wait_online(timeout=30):
    t0 = time.time()
    while time.time() - t0 < timeout:
        j = state()['find']['online_job']
        if j['state'] != 'running':
            return j
        time.sleep(0.05)
    return state()['find']['online_job']


# --- разбор ответов поисковиков и страниц t.me (на образцах той же формы, что у настоящих) ---
ex = websearch.extract
ddg = '<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Ft.me%2Fryba_ua&amp;rut=1">x</a> <a class="result__snippet">t.me/s/fish_chat_ua — чат</a>'
ok(ex(ddg) == ['fish_chat_ua', 'ryba_ua'] or sorted(ex(ddg)) == ['fish_chat_ua', 'ryba_ua'], 'из ответа DuckDuckGo достаются имена t.me', ex(ddg))
bu = base64.urlsafe_b64encode(b'https://t.me/spinning_all').decode().rstrip('=')
ok(ex('<a href="https://www.bing.com/ck/a?!&amp;&amp;p=1&amp;u=a1%s&amp;ntb=1">x</a>' % bu) == ['spinning_all'], 'из зашифрованной ссылки Bing достаётся имя t.me')
ok(ex('https://t.me/joinchat/AAAA https://t.me/+AbCdEf t.me/addstickers/xx t.me/some_bot https://t.me/share/url?u=1') == [], 'приглашения, стикеры, боты и служебные адреса отбрасываются')
ok(sorted(ex('tg://resolve?domain=hunt_chat и tgstat.ru/chat/@memes_games и telegram.me/Tanks_Chat')) == ['Tanks_Chat', 'hunt_chat', 'memes_games'], 'берутся и адреса tg://, tgstat и telegram.me')
def _ly(kind, name):
    return ('<li><div class="search-result-type-img"> <div class="search-%s"> <span>%s</span> </div> </div> </div> <div class="search-result-info"> '
            '<p class="search-result-title"> <a href="https://t.me/%s"> T </a> </p></div></li>' % (kind, kind, name))
ok(ex(_ly('channel', 'rybalka_dnm') + _ly('group', 'fish_chat_x') + _ly('bot', 'some_robot') + '<a href="https://t.me/rybalka_dnm/55">p</a>') == ['fish_chat_x'],
   'у Lyzem каналы и боты отбрасываются по подписи типа ещё до проверки страницы, группа остаётся')
pg = fake_web.tme_page('ryba_ua')
p = websearch.parse_tme(pg, 'ryba_ua')
ok(p['kind'] == 'group' and p['title'] == 'Рыбалка Украина' and p['members'] == 5400 and p['online'] == 321 and p['about'] == 'Чат рыбаков Украины' and not p['join_request'],
   'страница группы: название, участники, онлайн, описание', p)
PAGES_BACK = copy.deepcopy(fake_web.PAGES)
ok(websearch.parse_tme(fake_web.tme_page('lviv_fish'), 'lviv_fish')['join_request'], 'кнопка «Request to Join» = вступление по заявке')
ok(websearch.parse_tme(fake_web.tme_page('hidden_group'), 'hidden_group')['online'] is None, 'если онлайн скрыт, это видно (None, а не 0)')
ok(websearch.parse_tme(fake_web.tme_page('fish_channel'), 'fish_channel')['kind'] == 'channel', 'канал распознаётся по слову «subscribers»')
ok(websearch.parse_tme(fake_web.tme_page('some_person'), 'some_person')['kind'] == 'user' and websearch.parse_tme(fake_web.tme_page('some_x_bot'), 'some_x_bot')['kind'] == 'none',
   'человек распознаётся, а несуществующая страница — как «нет»')
ru = pg.replace('5 400 members, 321 online', '5 400 участников, 321 в сети')
p = websearch.parse_tme(ru, 'ryba_ua')
ok(p['kind'] == 'group' and p['members'] == 5400 and p['online'] == 321, 'русская версия страницы тоже читается (участников, в сети)', p)
p = websearch.parse_tme(pg.replace('5 400 members, 321 online', '1 member'), 'x')
ok(p['kind'] == 'group' and p['members'] == 1 and p['online'] is None, 'группа из одного участника читается')

r = api('/api/find/start', {'cats': []})
ok(r['ok'] is False and 'галочки' in r['error'], 'без выбранных тем поиск не запускается')
r = api('/api/find/start', {'cats': ['other']})
ok(r['ok'] is False, '«Другое» искать нельзя')
f = state()['find']
ok(f['queries']['fishing'] == 10 and f['queries']['other'] == 0 and f['total_base'] == 0, 'для каждой темы известно число слов, база пока пуста', f)
ok(len(finder.plan(['fishing', 'games'])) == 23 and finder.plan(['fishing', 'games'])[:2][0][0] != finder.plan(['fishing', 'games'])[:2][1][0],
   'слова разных тем идут вперемешку (поровну на каждую)')
ok(f['max_queries'] == 60 and not hasattr(tgu.TgUser, 'search') and not hasattr(tgu.TgUser, 'full'), 'поиск не использует аккаунт Telegram: в программе нет запросов поиска в Telegram')
try:
    finder._keep_awake(True); finder._keep_awake(False)
    ok(True, 'защита от сна Windows не ломает работу вне Windows')
except Exception as e:
    ok(False, 'защита от сна Windows не ломает работу вне Windows', e)

f = new_run(['fishing', 'games'])
ok(f['state'] == 'done' and f['done'] == 23 and f['total'] == 23, 'поиск прошёл все 23 слова', f)
ok(len(fake_web.WORDS_SEEN) == 23 and len(fake_web.SEARCHES) == 23 * 12 and {e for e, _ in fake_web.SEARCHES} == {'ddg', 'bing', 'lyzem', 'mojeek', 'brave'},
   'каждое слово искалось во всех пяти источниках (у Lyzem и Bing листаются страницы, пока на них есть новые имена)', (len(fake_web.WORDS_SEEN), len(fake_web.SEARCHES)))
ok(f['total_base'] == 7 and f['unsaved'] == 7 and f['new'] == 7 and f['kept'] == 7, 'в базе 7 новых групп (каналы, люди, пустые и мои чаты не попали)', f)
ok(f['checked'] == 11 and len(fake_web.TME) == 11 and len(set(fake_web.TME)) == 11 and 'autoua' not in fake_web.TME,
   'страница t.me открыта по разу для каждого нового имени (11), мой чат не проверялся', (f['checked'], fake_web.TME))
ok(f['raw'] > 11 and [e['name'] for e in f['engines']] == ['DuckDuckGo', 'Bing', 'Lyzem', 'Mojeek', 'Brave'] and not any(e['off'] for e in f['engines']) and all(e['found'] for e in f['engines']),
   'окну известно, сколько ссылок найдено и как отработал каждый поисковик', f['engines'])
b = finder.base()
ok(set(b) == {'w_ryba_ua', 'w_spin_all', 'w_lviv_fish', 'w_hunt_chat', 'w_tanks_chat', 'w_memes_games', 'w_gamers_ua'}, 'в базе нужные 7 групп', sorted(b))
ok(b['w_ryba_ua']['members'] == 5400 and b['w_ryba_ua']['online'] == 321 and b['w_ryba_ua']['online_at'] and b['w_ryba_ua']['about'] == 'Чат рыбаков Украины'
   and b['w_ryba_ua']['username'] == 'ryba_ua' and b['w_ryba_ua']['title'] == 'Рыбалка Украина', 'у группы сразу есть название, участники, онлайн и описание')
ok(b['w_ryba_ua']['cat'] == 'fishing' and b['w_tanks_chat']['cat'] == 'games' and b['w_lviv_fish']['cat'] == 'fishing' and b['w_memes_games']['cat'] == 'games',
   'темы групп расставлены по выбранным категориям', {k: v['cat'] for k, v in b.items()})
ok(b['w_lviv_fish']['join_request'] and not b['w_spin_all']['join_request'], 'пометка «по заявке» сохранилась')
ok(finder.seen().get('fish_channel', [0, ''])[1] == 'channel' and finder.seen().get('tiny_group'), 'каналы и пустые группы запомнены, чтобы не проверять их снова')

r = api('/api/find/list?cat=fishing')
ok([x['id'] for x in r['items']] == ['w_ryba_ua', 'w_hunt_chat', 'w_spin_all', 'w_lviv_fish'], 'тема «Рыбалка»: 4 группы, где больше онлайн — выше', [x['id'] for x in r['items']])
ok(r['counts'].get('fishing') == 4 and r['counts'].get('games') == 3, 'число групп по темам считается для всех тем сразу', r['counts'])
r = api('/api/find/list?cat=all&min=1000')
ok(len(r['items']) == 5 and all(x['members'] >= 1000 for x in r['items']), 'фильтр «от 1000 участников»', len(r['items']))
r = api('/api/find/list?cat=all&q=%D1%82%D0%B0%D0%BD%D0%BA%D0%B8')
ok([x['username'] for x in r['items']] == ['tanks_chat'], 'поиск по названию внутри базы')

own = cfg.S['chats']
own['-100500001'] = {'id': '-100500001', 'title': 'Рыбалка Украина', 'username': 'Ryba_UA'}
ok(api('/api/find/list?cat=all')['matched'] == 6 and state()['find']['total_base'] == 6, 'если я вступил в группу из базы, она пропадает из базы (по имени)')
del own['-100500001']
ok(state()['find']['total_base'] == 7, '...и возвращается, если чата у меня нет')

r = api('/api/find/cat', {'id': 'w_memes_games', 'cat': 'humor'})
ok(r['ok'] and finder.base()['w_memes_games']['cat'] == 'humor' and finder.base()['w_memes_games']['manual'], 'тему группы в базе можно поменять вручную')
r = api('/api/find/cat', {'id': 'w_memes_games', 'cat': 'нет_такой'})
ok(r['ok'] is False, 'неизвестная тема отклоняется')
r = api('/api/find/cat', {'id': '-1', 'cat': 'humor'})
ok(r['ok'] is False, 'неизвестная группа отклоняется')

r = api('/api/find/save', {})
ok(r['ok'] and r['saved_now'] == 7 and r['total'] == 7 and r['find']['unsaved'] == 0, 'кнопка «Сохранить базу» сохраняет 7 групп', r)
with open(os.path.join(HOME, 'data.json'), encoding='utf-8') as fh:
    dj = json.load(fh)
ok(len(dj.get('base', {})) == 7 and all(x['saved'] for x in dj['base'].values()), 'база лежит на диске и помечена сохранённой')

f = new_run(['fishing'])
ok(f['state'] == 'done' and f['new'] == 0 and f['unsaved'] == 0 and f['total_base'] == 7 and len(fake_web.TME) == 0, 'повторный поиск не дублирует группы и не открывает уже проверенные страницы', (f, fake_web.TME))
ok(finder.base()['w_memes_games']['cat'] == 'humor', 'ручная тема не сбрасывается повторным поиском')

# если убрать группу крестиком, она больше не предлагается
r = api('/api/find/drop', {'ids': ['w_hunt_chat']})
ok(r['dropped'] == 1 and 'w_hunt_chat' not in finder.base(), 'группу можно убрать из базы')
f = new_run(['fishing', 'games'])
ok('w_hunt_chat' not in finder.base() and 'hunt_chat' not in fake_web.TME, 'убранная крестиком группа больше не появляется и не проверяется')
finder.seen().pop('hunt_chat', None)
f = new_run(['fishing'])
ok('w_hunt_chat' in finder.base(), '...пока запись о ней не сотрётся (через три месяца)')
r = api('/api/find/drop', {'ids': ['w_hunt_chat']})
finder.seen().pop('hunt_chat', None)

# один поисковик отказал: остальные работают, отказавший отключается
finder.base().clear(); finder.seen().clear()
fake_web.reset()
fake_web.ENGINE_FAIL['brave'] = 429
api('/api/find/start', {'cats': ['fishing']})
f = wait_find()
br = [e for e in f['engines'] if e['id'] == 'brave'][0]
ok(f['state'] == 'done' and f['total_base'] == 4 and br['off'] and '429' in br['err'] and sum(1 for e, _ in fake_web.SEARCHES if e == 'brave') == 3,
   'если поисковик отвечает отказом, после трёх неудач он отключается, остальные продолжают', (f, br))

# поисковик просит «подождать»: отдыхает и не спрашивается заново, пока отдыхает (не выключается совсем)
finder.base().clear(); finder.seen().clear()
fake_web.reset()
fake_web.ENGINE_FAIL['ddg'] = 202
websearch.COOL = 600
api('/api/find/start', {'cats': ['fishing']})
f = wait_find()
dd = [e for e in f['engines'] if e['id'] == 'ddg'][0]
ok(f['state'] == 'done' and f['total_base'] == 4 and not dd['off'] and dd['cool'] and '202' in dd['err'] and sum(1 for e, _ in fake_web.SEARCHES if e == 'ddg') == 1,
   'поисковик с отказом 202 уходит на отдых и до его конца не опрашивается, остальные работают', (f, dd))
websearch.COOL = 0

# все источники отказывают, но отдыхают недолго: поиск ждёт их, а не пропускает слова, и в конце честно говорит, что не вышло
finder.base().clear(); finder.seen().clear()
fake_web.reset()
for _e in ('ddg', 'bing', 'lyzem', 'mojeek', 'brave'):
    fake_web.ENGINE_FAIL[_e] = 429
websearch.COOL = 0.3
_t0 = time.time()
api('/api/find/start', {'cats': ['fishing']})
f = wait_find(60)
ok(f['state'] == 'error' and 'не отвечают' in f['msg'] and time.time() - _t0 > 0.5 and f['done'] == 3 and len(fake_web.SEARCHES) == 15,
   'если все источники отказали, поиск ждёт их отдыха (а не пропускает слова), в итоге по 3 отказа на источник и честная ошибка', (f, len(fake_web.SEARCHES), time.time() - _t0))
websearch.COOL = 0

# все поисковики не отвечают
finder.base().clear(); finder.seen().clear()
fake_web.reset()
fake_web.NET_DOWN[0] = True
api('/api/find/start', {'cats': ['fishing']})
f = wait_find()
ok(f['state'] == 'error' and 'поисковики не отвечают' in f['msg'] and f['done'] < f['total'], 'нет интернета: поиск останавливается с понятным сообщением', f)

# t.me просит подождать
finder.base().clear(); finder.seen().clear()
fake_web.reset()
fake_web.TME_BLOCK[0] = 1000
api('/api/find/start', {'cats': ['fishing']})
f = wait_find()
ok(f['state'] == 'done' and 'подождать' in f['warn'] and f['done'] == 1 and f['total_base'] == 0 and not finder.seen(),
   'если t.me просит подождать, поиск останавливается, ничего лишнего не запоминая', f)
fake_web.TME_BLOCK[0] = 0
f = new_run(['fishing'])
ok(f['state'] == 'done' and f['total_base'] == 4, 'после паузы тот же поиск находит всё (ничего не потерялось)', f)

# t.me не открывается совсем
finder.base().clear(); finder.seen().clear()
fake_web.reset()
fake_web.TME_NETFAIL[0] = True
api('/api/find/start', {'cats': ['fishing']})
f = wait_find()
ok(f['state'] == 'error' and 'не открываются' in f['msg'], 'если страницы t.me не открываются, поиск говорит об этом, а не молчит', f)
fake_web.TME_NETFAIL[0] = False

# отмена и защита от двойного запуска
finder.base().clear(); finder.seen().clear()
finder.random_pause = lambda a, b: 0.5
fake_web.reset()
r = api('/api/find/start', {'cats': ['fishing', 'games']})
ok(r['ok'] and r['find']['state'] == 'running', 'поиск запускается и идёт в фоне', r)
time.sleep(0.3)
fw = state()['find']
ok(fw['state'] == 'running' and fw['cur'] and fw['total'] == 23, 'пока идёт поиск, окну известно, чем он занят', fw)
r2 = api('/api/find/start', {'cats': ['fishing']})
ok(r2['ok'] is False and 'уже идёт' in r2['error'], 'второй поиск параллельно не запускается')
r3 = api('/api/publish', {})
ok(r3['ok'] is False and 'поиск новых чатов' in r3['error'], 'во время поиска публикация не стартует')
api('/api/find/cancel', {})
f = wait_find()
ok(f['state'] == 'cancelled' and f['done'] < f['total'] and f['cur'] == '', 'кнопка «Остановить» останавливает поиск', f)
finder.random_pause = lambda a, b: 0.02

# удаление «несохранённых» не трогает сохранённое
f = new_run(['fishing', 'games'])
r = api('/api/find/save', {})
finder.base()['w_extra1'] = dict(finder.base()['w_ryba_ua'], id='w_extra1', username='extra1', saved=False)
finder.base()['w_extra2'] = dict(finder.base()['w_ryba_ua'], id='w_extra2', username='extra2', saved=False)
r = api('/api/find/drop', {'unsaved': True})
ok(r['dropped'] == 2 and len(finder.base()) == 7 and all(x['saved'] for x in finder.base().values()), '«Убрать несохранённые» не трогает сохранённое')

# --- онлайн кнопкой: страницы t.me, без аккаунта Telegram ---
ids = list(finder.base())
fake_web.reset()
r = api('/api/find/online', {'ids': ids})
j = wait_online()
ok(r['ok'] and j['state'] == 'done' and j['done'] == j['total'] == 7 and len(fake_web.TME) == 7 and not fake_web.SEARCHES, 'кнопка «Обновить онлайн» открывает страницу t.me каждой группы (7) и не ходит в поисковики', (j, fake_web.TME))
ok(api('/api/find/online', {'ids': ['нет']})['ok'] is False, 'без существующих групп обновлять нечего')
fp = fake_web.PAGES
fp['hunt_chat']['online'] = 77
fp['hunt_chat']['members'] = 2400
fp['spin_all'] = {'type': 'channel', 'title': 'Спиннинг', 'members': 5000}
del fp['lviv_fish']
fp['tanks_chat']['online'] = None
fake_web.reset()
api('/api/find/online', {'ids': ids})
j = wait_online()
b = finder.base()
ok(b['w_hunt_chat']['online'] == 77 and b['w_hunt_chat']['members'] == 2400, 'онлайн и участники обновились')
ok(b['w_spin_all']['gone'] and b['w_lviv_fish']['gone'] and b['w_lviv_fish']['online'] is None, 'если страницы нет или группа стала каналом, она помечается недоступной')
ok(b['w_tanks_chat']['online'] is None and b['w_tanks_chat']['online_at'] and not b['w_tanks_chat']['gone'], 'если онлайн скрыт, группа остаётся, а число пустое')
lst = api('/api/find/list?cat=all&min=0&sort=online')['items']
on = [x['online'] for x in lst if x['online'] is not None]
nn = [x['online'] is None for x in lst]
ok(on == sorted(on, reverse=True) and nn == sorted(nn) and nn[-1], 'сортировка «по онлайну»: больше онлайна выше, без онлайна в конце', [(x['title'], x['online']) for x in lst])
lst = api('/api/find/list?cat=all&min=0&sort=members')['items']
ok([x['members'] for x in lst] == sorted([x['members'] for x in lst], reverse=True), 'сортировка «по участникам»')
ok(len(api('/api/find/list?cat=all&min=0&sort=new')['items']) == len(lst), 'сортировка «сначала новые» работает')
fake_web.PAGES.clear(); fake_web.PAGES.update(copy.deepcopy(PAGES_BACK))

fake_web.reset()
fake_web.TME_BLOCK[0] = 1000
api('/api/find/online', {'ids': ids})
j = wait_online()
ok(j['state'] == 'done' and 'подождать' in j['warn'] and j['done'] < j['total'], 'если t.me просит подождать, обновление онлайна останавливается с предупреждением', j)
fake_web.TME_BLOCK[0] = 0

finder.random_pause = lambda a, b: 0.5
fake_web.reset()
api('/api/find/online', {'ids': ids})
r2 = api('/api/find/online', {'ids': ids})
ok(r2['ok'] is False and 'уже обновляется' in r2['error'], 'второе обновление онлайна параллельно не запускается')
r3 = api('/api/publish', {})
ok(r3['ok'] is False and 'онлайн' in r3['error'], 'пока идёт проверка онлайна, публикация не стартует')
api('/api/find/online/cancel', {})
j = wait_online()
ok(j['state'] == 'cancelled' and j['done'] < j['total'], 'обновление онлайна можно остановить', j)
finder.random_pause = lambda a, b: 0.02

# --- темы для игры «Пустошь»: стоят в начале списка, помечены, у каждой есть слова для поиска и для определения ---
cl = state()['cats']
ids = [c['id'] for c in cl]
ok(ids[:5] == ['promo', 'showcase', 'gamedev', 'tgdev', 'feedback'] and all(c['hot'] for c in cl[:5]) and not any(c['hot'] for c in cl[5:]),
   'пять новых тем для игры стоят в самом верху списка и помечены', ids[:7])
ok(all(len(cats.queries(i)) >= 6 for i in cats.HOT), 'у каждой новой темы есть слова для поиска', {i: len(cats.queries(i)) for i in cats.HOT})
exp = {'Взаимопиар игр и ботов': 'promo', 'Делимся своими играми': 'showcase', 'Разработчики игр Украины': 'gamedev', 'Telegram Mini Apps разработка': 'tgdev',
       'Тестеры игр — плейтест': 'feedback', 'Помощь в играх': 'feedback', 'Гайды по Dota': 'games', 'Hamster Kombat mini app': 'tggames', 'Новости игр': 'games'}
bad = {t: (cats.guess(t), v) for t, v in exp.items() if cats.guess(t) != v}
ok(not bad, 'чаты по названию попадают в новые темы, а обычные игровые остаются в «Игры»', bad)
f = new_run(['promo', 'tgdev'])
ok(f['state'] == 'done' and f['total'] == 13 and len(fake_web.WORDS_SEEN) == 13 and fake_web.WORDS_SEEN[0] == 'взаимопиар', 'поиск по новым темам идёт по их словам', f)

# перенос новых тем в уже сохранённый список (у тех, кто пользовался до обновления)
orig = copy.deepcopy(cfg.S['cats'])
old = [c for c in orig if c['id'] not in cats.HOT]
old.insert(0, {'id': 'cMy', 'name': 'Мои друзья', 'words': ''})
old.insert(1, {'id': 'cDup', 'name': 'Тест и помощь по играм', 'words': ''})      # такое же название уже занято своей темой
cfg.S['cats'] = old
cfg.S.pop('cats_v2', None)
ids = [c['id'] for c in cats.categories()]
ok(ids[:4] == ['promo', 'showcase', 'gamedev', 'tgdev'] and 'feedback' not in ids and ids[4:6] == ['cMy', 'cDup'] and cfg.S.get('cats_v2'),
   'в старый список новые темы добавляются в начало, свои темы не трогаются, одноимённая не дублируется', ids[:8])
api('/api/cats', {'op': 'delete', 'id': 'promo'})
ok('promo' not in [c['id'] for c in cats.categories()], 'удалённая тема не возвращается сама')
cfg.S['cats'] = orig
cfg.S['cats_v2'] = 1
cfg.save()

# таблица
finder.base().clear(); finder.seen().clear()
f = new_run(['fishing', 'games'])
h = {'X-Token': server.TOKEN}
st, hh, raw = net.request('GET', 'http://127.0.0.1:%d/api/find/export' % PORT, h, None, 30)
txt = raw.decode('utf-8-sig')
ok(st == 200 and raw[:3] == b'\xef\xbb\xbf' and 'attachment' in str(hh).lower(), 'таблица скачивается файлом (Excel откроет кириллицу)')
ok(txt.splitlines()[0].startswith('Название;Ссылка;Участников;Онлайн;Тема') and 'https://t.me/tanks_chat' in txt and len(txt.splitlines()) == 8 and ';600;' in txt, 'в таблице заголовок, все группы и онлайн')
st, _ = call('GET', '/api/find/export', token=False)
ok(st == 401, 'без ключа окна таблица не отдаётся')
st, _ = call('GET', '/api/find/list', token=False)
ok(st == 401, 'без ключа окна база не отдаётся')

print('\n[5] Файлы')
png = jpg()
st, j = call('PUT', '/api/upload?name=boss.jpg', raw=png)
ok(st == 200 and j['draft']['media']['kind'] == 'photo', 'фото загружено', j)
st, b = call('GET', j['draft']['media']['url'])
ok(st == 200 and b == png, 'загруженное фото отдаётся обратно целиком')
st, j2 = call('PUT', '/api/upload?name=virus.exe', raw=b'MZ')
ok(st == 400 and 'картинка' in j2['error'].lower(), 'неподходящий файл отклоняется')
big = os.urandom(5 * 1024 * 1024 + 7)
st, j = call('PUT', '/api/upload?name=boss.mp4', raw=big)
ok(st == 200 and j['draft']['media']['kind'] == 'video', 'видео 5 МБ загружено')
vurl = j['draft']['media']['url']
ok(open(server.DRAFT['media']['path'], 'rb').read() == big, 'видео на диске совпадает с загруженным')
st, hh, b = net.request('GET', 'http://127.0.0.1:%d%s' % (PORT, vurl), {'X-Token': server.TOKEN, 'Range': 'bytes=10-19'}, None, 10)
ok(st == 206 and b == big[10:20], 'видео отдаётся кусками (для перемотки)')
r = api('/api/media/meta', {'w': 1080, 'h': 1920, 'dur': 25.4})
m = r['draft']['media']
ok(m['w'] == 1080 and m['dur'] == 25, 'размеры видео запомнены', m)
st, j = call('PUT', '/api/upload?role=thumb&name=t.jpg', raw=jpg(320, 180))
ok(st == 200 and state()['draft']['has_thumb'], 'кадр-превью видео загружен')

print('\n[6] Генерация')
r = api('/api/draft', {'threads': True, 'yt': False})
st0 = len(ST.anthropic_reqs)
r = api('/api/generate', {})
req = ST.anthropic_reqs[-1][1]['messages'][0]['content']
ok(r['ok'] and r['draft']['texts']['telegram'].startswith('Тугар'), 'ИИ написал тексты')
ok(req[0]['type'] == 'image', 'для видео ИИ получил кадр-превью')
ok('Пустош' in req[-1]['text'] and 'start=tg' in req[-1]['text'], 'ИИ получил описание игры и ссылки с метками')
ok(r['draft']['card_url'] == '', 'для видео картинка с надписью не делается')
# фото
st, j = call('PUT', '/api/upload?name=shot.jpg', raw=png)
api('/api/draft', {'note': 'показываю босса Тугара'})
r = api('/api/generate', {})
d = r['draft']
ok(d['card_url'].startswith('/media/card_'), 'для фото сделана картинка с надписью')
st, b = call('GET', d['card_url'])
im = Image.open(io.BytesIO(b))
ok(im.size == (1080, 1350), 'размер картинки 1080×1350', im.size)
im.save(os.path.join(HERE, 'card_preview.jpg'))
ok('Тугара' in ST.anthropic_reqs[-1][1]['messages'][0]['content'][-1]['text'], 'заметка ушла ИИ')
r = api('/api/draft', {'card_title': 'Совсем другой заголовок', 'card_sub': 'Подпись 2'})
ok(r['draft']['card_title'] == 'Совсем другой заголовок', 'заголовок картинки можно править')
r = api('/api/draft', {'card_on': False})
ok(r['draft']['card_url'] == '', 'картинку с надписью можно выключить')
api('/api/draft', {'card_on': True})
r = api('/api/draft', {'texts': {'telegram': 'Мой текст\nвторая строка', 'threads': 'короткий'}})
ok(r['draft']['texts']['telegram'].startswith('Мой текст'), 'тексты можно править руками')
api('/api/settings', {'ANTHROPIC_API_KEY': 'wrong'})
r = api('/api/generate', {})
ok(r['ok'] and 'ключ Claude не подошёл' in r['warn'].lower() or 'не подошёл' in r['warn'], 'неверный ключ: понятное предупреждение', r.get('warn'))
ok(r['draft']['texts']['telegram'], 'при ошибке ИИ всё равно есть простой вариант текста')
api('/api/settings', {'ANTHROPIC_API_KEY': 'good-key'})
api('/api/generate', {})

print('\n[6б] Ещё дополнительно сгенерировать (GPT / OpenAI)')
x = state()['extra']
ok(not state()['conn']['gpt'] and x['state'] == 'idle' and x['items'] == [], 'до ввода ключа OpenAI: картинок нет, подключения нет')
r = api('/api/extra/start', {})
ok(r['ok'] is False and 'ключ openai' in r['error'].lower(), 'без ключа OpenAI кнопка просит ключ', r)
api('/api/settings', {'OPENAI_API_KEY': 'bad-openai'})
ok(state()['conn']['gpt'], 'ключ OpenAI виден в подключениях')
r = api('/api/extra/start', {'n': 2})
x = wait_extra()
ok(r['ok'] and x['state'] == 'error' and 'ключ openai не подошёл' in x['msg'].lower(), 'неверный ключ OpenAI: понятная ошибка', x)
api('/api/settings', {'OPENAI_API_KEY': 'good-openai'})
n0 = len(ST.openai_reqs)
r = api('/api/extra/start', {'idea': 'Ногай с саблей на закате', 'n': 3, 'size': 'square', 'quality': 'high'})
ok(r['ok'] and r['extra']['state'] == 'running', 'рисование запущено в фоне', r)
x = wait_extra()
ok(x['state'] == 'done' and len(x['items']) == 3, 'GPT нарисовал 3 картинки', x)
auth, f = ST.openai_reqs[-1]
ok(auth == 'Bearer good-openai' and f['model'] == 'gpt-image-2' and f['n'] == '3' and f['size'] == '1024x1024' and f['quality'] == 'high', 'в OpenAI ушли модель, число, формат и качество', f)
ok(f['image[]'].startswith('FILE:reference.jpg:') and 'Ногай с саблей на закате' in f['prompt'] and 'no text' in f['prompt'].lower(), 'фото ушло как образец, идея автора в описании', f['prompt'][:200])
ok(f['output_format'] == 'jpeg' and 'input_fidelity' not in f and 'response_format' not in f, 'лишних параметров нет')
ok(len(ST.openai_reqs) - n0 == 1, 'один запрос на все картинки')
ok(not [g for g in gen_files() if g.startswith('ref_')], 'временная копия фото удалена')
it = x['items'][0]
st, b = call('GET', it['url'])
im = Image.open(io.BytesIO(b))
ok(st == 200 and im.size == (128, 128), 'картинка GPT открывается и отдаётся окну', (st, im.size))
# «ещё» — добавляется к уже нарисованным; образец — всегда исходное фото
api('/api/extra/start', {'n': 1, 'idea': ''})
x = wait_extra()
ok(len(x['items']) == 4 and x['base'] and x['base']['name'] == 'shot.jpg', 'повторное нажатие добавляет ещё картинку', x)
ok('показываю босса Тугара' in ST.openai_reqs[-1][1]['prompt'], 'без идеи берётся заметка автора')
# нельзя запускать второй раз, пока рисует
ST.openai_delay = 0.8
api('/api/extra/start', {'n': 1})
r2 = api('/api/extra/start', {'n': 1})
ok(r2['ok'] is False and 'уже рисует' in r2['error'], 'пока GPT рисует, второй запуск не стартует')
ok(state()['extra']['state'] == 'running', 'состояние «рисует» видно окну')
x = wait_extra()
ST.openai_delay = 0
ok(len(x['items']) == 5, 'после ожидания картинка добавилась', len(x['items']))
# ошибки OpenAI
ST.openai_fail = [(404, {'error': {'message': 'The model `gpt-image-2` does not exist or you do not have access to it.', 'code': 'model_not_found'}})]
api('/api/extra/start', {'n': 1})
x = wait_extra()
ok(x['state'] == 'done' and x['model'] == 'gpt-image-1.5' and [q[1]['model'] for q in ST.openai_reqs[-2:]] == ['gpt-image-2', 'gpt-image-1.5'], 'нет доступа к новой модели: пробуется следующая', (x['state'], x['model']))
ST.openai_fail = [(429, {'error': {'message': 'You exceeded your current quota, please check your plan and billing details.', 'code': 'insufficient_quota'}})]
api('/api/extra/start', {'n': 1})
x = wait_extra()
ok(x['state'] == 'error' and 'нет денег' in x['msg'] and 'Billing' in x['msg'], 'закончились деньги на OpenAI: понятный совет', x['msg'])
ST.openai_fail = [(400, {'error': {'message': 'Your request was rejected by the safety system.', 'code': 'moderation_blocked'}})]
api('/api/extra/start', {'n': 1})
x = wait_extra()
ok(x['state'] == 'error' and 'фильтр' in x['msg'], 'фильтр безопасности OpenAI: понятный совет', x['msg'])
ST.openai_fail = [(403, {'error': {'message': 'Your organization must be verified to use the model `%s`.' % m, 'code': 'invalid_request_error'}}) for m in ('gpt-image-2', 'gpt-image-1.5', 'gpt-image-1')]
api('/api/extra/start', {'n': 1})
x = wait_extra()
ok(x['state'] == 'error' and 'подтвердить организацию' in x['msg'] and not ST.openai_fail, 'нужна проверка организации: пробует все модели и подсказывает', x['msg'])
ok(len(x['items']) == 6, 'после ошибок уже нарисованное не пропало', len(x['items']))
# своя модель из настроек
api('/api/settings', {'OPENAI_IMAGE_MODEL': 'gpt-image-1'})
api('/api/extra/start', {'n': 1})
x = wait_extra()
ok(ST.openai_reqs[-1][1]['model'] == 'gpt-image-1' and x['model'] == 'gpt-image-1', 'модель из настроек используется как есть')
api('/api/settings', {'clear': ['OPENAI_IMAGE_MODEL']})
# выбор картинки для поста
x = state()['extra']
first = x['items'][0]
r = api('/api/extra/use', {'id': first['id']})
m = r['draft']['media']
ok(m['kind'] == 'photo' and m['url'] == first['url'] and m['name'] == 'Картинка GPT' and r['extra']['used'] == first['id'], 'картинка GPT выбрана для поста')
ok(r['draft']['card_url'].startswith('/media/card_'), 'надпись на картинке пересобралась по новой картинке')
r = api('/api/extra/drop', {'id': first['id']})
ok(any(i['id'] == first['id'] for i in r['extra']['items']), 'выбранную для поста картинку из списка не убрать')
other = x['items'][1]
r = api('/api/extra/drop', {'id': other['id']})
ok(not any(i['id'] == other['id'] for i in r['extra']['items']) and not os.path.exists(os.path.join(cfg.MEDIA, os.path.basename(other['url']))), 'лишнюю картинку можно убрать, файл удаляется')
r = api('/api/extra/use', {'id': 'orig'})
ok(r['draft']['media']['name'] == 'shot.jpg' and r['extra']['used'] == 'orig', 'можно вернуть исходное фото')
r = api('/api/extra/use', {'id': 'nope'})
ok(r['ok'] is False and 'нет' in r['error'], 'несуществующая картинка отклоняется')
ok('good-openai' not in json.dumps(api('/api/settings', {})) and 'good-openai' not in api('/api/report')['text'], 'ключ OpenAI не светится в окне и отчёте')
# новый файл -> прошлые картинки GPT не нужны
files_before = gen_files()
ok(len(files_before) >= 4, 'картинки GPT лежат на диске', files_before)
st, j = call('PUT', '/api/upload?name=other.jpg', raw=png)
ok(state()['extra']['items'] == [] and state()['extra']['base'] is None and not gen_files(), 'при смене фото прошлые картинки GPT удаляются')
# пока рисует — убрали файл: результат выбрасывается
ST.openai_delay = 0.6
api('/api/extra/start', {'n': 2})
api('/api/media/clear', {})
time.sleep(1.4)
ST.openai_delay = 0
x = state()['extra']
ok(x['items'] == [] and not gen_files(), 'если фото убрали во время рисования, лишнего не остаётся', (x['state'], gen_files()))
r = api('/api/extra/start', {})
ok(r['ok'] is False and 'фото' in r['error'].lower(), 'без фото картинки не рисуются')
# видео: образец — кадр из ролика, «в пост» заменяет ролик
st, j = call('PUT', '/api/upload?name=v.mp4', raw=os.urandom(5000))
r = api('/api/extra/start', {})
ok(r['ok'] is False and 'кадр' in r['error'].lower(), 'у видео без кадра-превью просим фото')
call('PUT', '/api/upload?role=thumb&name=t.jpg', raw=jpg(320, 180))
vpath = server.DRAFT['media']['path']
api('/api/extra/start', {'n': 1})
x = wait_extra()
ok(x['state'] == 'done' and len(x['items']) == 1 and x['base'] is None, 'для видео образцом служит кадр из ролика', x)
r = api('/api/extra/use', {'id': x['items'][0]['id']})
ok(r['draft']['media']['kind'] == 'photo' and not r['draft']['has_thumb'] and not os.path.exists(vpath), 'картинка заменила ролик, ролик и кадр убраны')
api('/api/media/clear', {})
st, j = call('PUT', '/api/upload?name=shot.jpg', raw=png)
api('/api/draft', {'note': 'показываю босса Тугара'})
api('/api/generate', {})

print('\n[7] Подключение Threads и YouTube')
r = api('/api/threads/link')
ok('client_id=APP' in r['url'] and 'threads_content_publish' in r['url'] and 'redirect_uri=https%3A%2F%2Fexample.github.io' in r['url'], 'ссылка входа Threads', r['url'])
r = api('/api/threads/code', {'text': 'https://example.github.io/pustosh/?code=BADCODE0123456789#_'})
ok(r['ok'] is False, 'плохой код Threads отклонён')
r = api('/api/threads/code', {'text': 'https://example.github.io/pustosh/?code=GOODCODE0123456789#_'})
ok(r['who'] == 'kozak_dev', 'Threads подключён', r)
r = api('/api/yt/secret', {'text': 'not json'})
ok(r['ok'] is False, 'мусор вместо client_secret.json отклонён')
r = api('/api/yt/secret', {'text': json.dumps({'installed': {'client_id': 'CID', 'client_secret': 'CS'}})})
ok(r['ok'], 'client_secret.json сохранён')
import webbrowser


def fake_open(url):
    import urllib.parse
    q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))

    def go():
        time.sleep(0.3)
        urllib.request.urlopen(q['redirect_uri'] + '/?code=AUTHCODE', timeout=5).read()
    threading.Thread(target=go, daemon=True).start()


webbrowser.open = fake_open
r = api('/api/yt/login', {})
for _ in range(60):
    if state()['conn']['yt']['login']['state'] in ('ok', 'err'):
        break
    time.sleep(0.2)
ok(state()['conn']['yt']['connected'] and state()['conn']['yt']['login']['state'] == 'ok', 'YouTube подключён через браузер', state()['conn']['yt'])

print('\n[8] Публикация: видео -> YouTube + Threads + Telegram')
api('/api/draft', {'yt': True, 'threads': True})
st, j = call('PUT', '/api/upload?name=boss.mp4', raw=os.urandom(17 * 1024 * 1024 + 123))
api('/api/media/meta', {'w': 1080, 'h': 1920, 'dur': 25})
call('PUT', '/api/upload?role=thumb&name=t.jpg', raw=jpg(320, 180))
api('/api/generate', {})
api('/api/tg/bulk', {'ids': [k for k, c in {c['id']: c for c in state()['chats']}.items() if c['sel']], 'sel': False})
for cid in ('-1006', '-1001', '-1003'):
    api('/api/tg/chat', {'id': cid, 'sel': True})
TG.sent.clear()
ST.yt_ranges.clear()
r = api('/api/publish', {})
ok(r['ok'], 'публикация запущена', r)
r2 = api('/api/publish', {})
ok(r2['ok'] is False and 'уже идёт' in r2['error'], 'вторую публикацию одновременно запустить нельзя')
j = wait_job()
ok(j['state'] == 'done', 'публикация закончилась', j['state'])
ok(all(i['status'] == 'ok' for i in j['items']), 'все площадки ok', [(i['key'], i['status'], i['msg']) for i in j['items']])
ok(by(j, 'yt')['link'] == 'https://youtu.be/VID123', 'ссылка YouTube')
ok(len(ST.yt_ranges) == 3 and ST.yt_ranges[0][:2] == (0, 8388607) and ST.yt_ranges[-1][1] == 17 * 1024 * 1024 + 122, 'ролик ушёл в YouTube тремя кусками', ST.yt_ranges)
q, body, hdr = ST.yt_init
ok('Тугар' in body['snippet']['title'] and body['status']['privacyStatus'] == 'public', 'название и статус YouTube')
ok(by(j, 'threads')['link'].startswith('https://www.threads.com/'), 'ссылка Threads')
ok(ST.threads_created[-1]['media_type'] == 'VIDEO' and ST.threads_created[-1]['video_url'].endswith('.mp4'), 'в Threads ушло видео по публичной ссылке')
ok([x[0] for x in TG.sent] == [-1001, -1003, -1006] or sorted(x[0] for x in TG.sent) == [-1006, -1003, -1001] or len(TG.sent) == 3, 'в Telegram ушло в 3 чата', TG.sent)
ok(all(x[2] == 'video' or x[0] == -1003 for x in TG.sent), 'видео ушло как видео')
ok(by(j, 'tg:-1006')['link'].startswith('https://t.me/pustosh_news/'), 'ссылка на пост в канале')
ok(state()['tg_today']['sent'] == 3, 'счётчик «сегодня отправлено» = 3', state()['tg_today'])
api('/api/job/clear', {})

print('\n[9] Публикация: фото, ошибки по чатам, пауза после спам-ограничения')
st, jj = call('PUT', '/api/upload?name=shot.jpg', raw=png)
api('/api/draft', {'yt': False, 'threads': True, 'note': ''})
api('/api/generate', {})
api('/api/tg/bulk', {'ids': [c['id'] for c in state()['chats']], 'sel': False})
for cid in ('-1009', '-1011', '-1002', '-1007'):
    api('/api/tg/chat', {'id': cid, 'sel': True})
TG.sent.clear()
n0 = len(ST.gh_puts)
api('/api/publish', {})
j = wait_job()
order = [i['key'] for i in j['items']]
ok(by(j, 'threads')['status'] == 'ok' and ST.threads_created[-1]['media_type'] == 'IMAGE' and len(ST.gh_puts) == n0 + 1, 'Threads: картинка через GitHub')
ok(ST.gh_puts[-1][0].endswith('.jpg') and ST.gh_puts[-1][1] == 'Bearer ghp_test', 'GitHub получил картинку с ключом', ST.gh_puts[-1])
ok(by(j, 'tg:-1009')['status'] == 'ok' and 'только текст' in by(j, 'tg:-1009')['msg'], 'чат без картинок: ушёл только текст', by(j, 'tg:-1009'))
ok(by(j, 'tg:-1011')['status'] == 'err' and 'нельзя' in by(j, 'tg:-1011')['msg'], 'запрещённый чат: ошибка, но остальные идут')
ok(by(j, 'tg:-1002')['status'] == 'ok' and by(j, 'tg:-1007')['status'] == 'ok', 'после запрещённого чата остальные получили пост')
ok([x[2] for x in TG.sent if x[0] == -1002] == ['photo'], 'в обычный чат ушла картинка')
api('/api/job/clear', {})
# FloodWait: всё остальное останавливается
api('/api/tg/bulk', {'ids': [c['id'] for c in state()['chats']], 'sel': False})
for cid in ('-1002', '-1010', '-1012'):
    api('/api/tg/chat', {'id': cid, 'sel': True})
TG.sent.clear()
api('/api/draft', {'threads': False})
api('/api/publish', {})
j = wait_job()
f = by(j, 'tg:-1010')
ok(f['status'] == 'err' and 'просит подождать' in f['msg'], 'FloodWait: ошибка показана')
ok(by(j, 'tg:-1012')['status'] == 'skip' and 'остановлено' in by(j, 'tg:-1012')['msg'], 'после FloodWait остальные чаты не трогаются')
ok([x[0] for x in TG.sent] == [-1002], 'до FloodWait отправлено, после — нет', TG.sent)
api('/api/job/clear', {})

print('\n[10] Дневной лимит и отмена')
api('/api/settings', {'TG_DAILY_LIMIT': '4', 'TG_DELAY_MIN': '15', 'TG_DELAY_MAX': '15'})
cfg.S['tg_sent'] = {'date': cfg.today(), 'n': 2}
api('/api/tg/bulk', {'ids': [c['id'] for c in state()['chats']], 'sel': False})
for cid in ('-1001', '-1002', '-1005', '-1007'):
    api('/api/tg/chat', {'id': cid, 'sel': True})
api('/api/draft', {'threads': False})
TG.sent.clear()
api('/api/publish', {})
j = wait_job()
tgi = [i for i in j['items'] if i['key'].startswith('tg:')]
ok(sum(1 for i in tgi if i['status'] == 'ok') == 2, 'лимит 4 в день: при двух уже отправленных уходит только 2', [(i['key'], i['status']) for i in tgi])
ok(any('лимит' in i['msg'] for i in tgi), 'про лимит сказано понятно')
api('/api/job/clear', {})
cfg.S['tg_sent'] = {'date': '2000-01-01', 'n': 99}
ok(state()['tg_today']['sent'] == 0, 'вчерашний счётчик не мешает сегодня')
# отмена
jobs.random_pause = lambda a, b: 30
TG.sent.clear()
api('/api/settings', {'TG_DAILY_LIMIT': '50'})
api('/api/publish', {})
time.sleep(0.6)
api('/api/job/cancel', {})
j = wait_job(10)
ok(j['state'] == 'cancelled', 'публикацию можно остановить во время паузы', j['state'])
ok(len(TG.sent) == 1 and any(i['status'] == 'skip' and i['msg'] == 'отменено' for i in j['items']), 'после остановки остальное не уходит', TG.sent)
jobs.random_pause = lambda a, b: 0.05
api('/api/job/clear', {})

print('\n[11] Публикация без нужного')
api('/api/tg/bulk', {'ids': [c['id'] for c in state()['chats']], 'sel': False})
api('/api/draft', {'threads': False, 'yt': False})
r = api('/api/generate', {})
ok(r['ok'] is False and 'выбери, куда' in r['error'].lower(), 'без выбранных площадок генерация не стартует')
r = api('/api/publish', {})
ok(r['ok'] is False and 'выбери' in r['error'].lower(), 'без площадок публикация не стартует')
api('/api/media/clear', {})
api('/api/draft', {'yt': True, 'note': 'текст без видео'})
api('/api/generate', {})
r = api('/api/publish', {})
j = wait_job()
ok(by(j, 'yt')['status'] == 'err' and 'нужен видеоролик' in by(j, 'yt')['msg'], 'YouTube без видео: понятная ошибка')
api('/api/job/clear', {})
api('/api/draft', {'yt': False})

print('\n[12] Claude, обновления, отчёт')
r = api('/api/claude/test', {})
ok(r['ok'] and r['answer'], 'проверка связи с Claude')
r = api('/api/claude/ask', {'text': 'идеи для постов', 'history': []})
ok(r['ok'] and r['answer'], 'чат с Claude отвечает')
api('/api/settings', {'ANTHROPIC_API_KEY': 'wrong'})
r = api('/api/claude/test', {})
ok(r['ok'] is False and 'ключ' in r['error'].lower(), 'неверный ключ Claude: понятная ошибка', r)
api('/api/settings', {'ANTHROPIC_API_KEY': 'good-key'})
# обновление
def mkzip(ver):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as z:
        z.writestr('version.py', "VERSION = '%s'\n" % ver)
        z.writestr('ui/index.html', '<html>new</html>')
    return b.getvalue()
version.VERSION = '1.0.0'                  # тест обновления не должен зависеть от текущей версии программы
z = mkzip('1.0.1')
ST.upd_json = {'version': '1.0.1', 'zip': 'app-1.0.1.zip', 'sha256': hashlib.sha256(z).hexdigest(), 'notes': 'тест', 'deps_hash': 'deps-A'}
ST.upd_files = {'app-1.0.1.zip': z}
r = api('/api/update/check')
ok(r['update']['newer'] and r['update']['latest'] == '1.0.1' and not r['update']['need_installer'], 'найдено обновление 1.0.1', r)
server._restart = lambda: None
orig_restart = update.restart
update.restart = lambda: None
r = api('/api/update/install', {})
ok(r['ok'] and update.newest_dir() and update.newest_dir()[0] == '1.0.1', 'обновление скачано и распаковано')
ok(os.path.exists(os.path.join(HOME, 'updates', '1.0.1', 'ui', 'index.html')), 'файлы обновления лежат в папке данных')
ST.upd_json = dict(ST.upd_json, sha256='0' * 64)
version.VERSION = '1.0.0'
r = api('/api/update/install', {})
ok(r['ok'] is False and 'повреждён' in r['error'], 'испорченный архив отклоняется')
ST.upd_json = dict(ST.upd_json, sha256=hashlib.sha256(z).hexdigest(), deps_hash='deps-B')
r = api('/api/update/check')
ok(r['update']['need_installer'], 'если набор библиотек изменился — просим новый установщик')
r = api('/api/update/install', {})
ok(r['ok'] is False and 'установщик' in r['error'].lower(), 'такое обновление молча не ставится')
evil = io.BytesIO()
with zipfile.ZipFile(evil, 'w') as zz:
    zz.writestr('../evil.txt', 'x')
    zz.writestr('version.py', "VERSION='9'")
ST.upd_json = {'version': '1.0.2', 'zip': 'e.zip', 'sha256': hashlib.sha256(evil.getvalue()).hexdigest(), 'deps_hash': 'deps-A'}
ST.upd_files = {'e.zip': evil.getvalue()}
r = api('/api/update/install', {})
ok(r['ok'] is False and 'пути' in r['error'], 'архив с опасными путями отклоняется')
update.restart = orig_restart
r = api('/api/report')
txt = r['text']
ok('Пустошь Маркетинг v' in txt and 'good-key' not in txt and 'ghp_test' not in txt and 'LONG-' not in txt, 'отчёт для Claude без секретов')

print('\n[13] Выход из Telegram и данные на диске')
r = api('/api/tg/logout', {})
ok(r['tg']['state'] == 'need_phone', 'выход из Telegram')
r = api('/api/find/start', {'cats': ['fishing']})
ok(r['ok'] and wait_find()['state'] == 'done', 'поиск групп работает и без входа в Telegram (аккаунт ему не нужен)')
with open(os.path.join(HOME, 'data.json'), encoding='utf-8') as f:
    dj = json.load(f)
ok('-1001' in dj['chats'] and dj['threads'].get('user_id') == '777', 'чаты и ключ Threads сохранены на диск')

print('\nИТОГО: %d проверок пройдено, %d провалено' % (len(OKS), len(FAILS)))
for x in FAILS:
    print('  ПРОВАЛ:', x)
shutil.rmtree(HOME, ignore_errors=True)
sys.exit(1 if FAILS else 0)
