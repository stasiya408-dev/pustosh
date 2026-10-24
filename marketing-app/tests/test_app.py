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
    'MKT_ANTHROPIC_URL': BASE, 'MKT_THREADS_BASE': BASE, 'MKT_THREADS_AUTH_URL': BASE + '/oauth/authorize', 'MKT_THREADS_POLL': '0.02',
    'MKT_GITHUB_API': BASE, 'MKT_YT_AUTH_URL': BASE + '/auth', 'MKT_YT_TOKEN_URL': BASE + '/token', 'MKT_YT_UPLOAD_URL': BASE + '/upload/youtube/v3/videos',
    'MKT_UPDATE_URL': BASE + '/upd', 'MKT_BASE_DEPS': 'deps-A',
})
import cfg, net, server, jobs, update, version, tgu, cats, yt, gen, card  # noqa
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
with open(os.path.join(HOME, 'data.json'), encoding='utf-8') as f:
    dj = json.load(f)
ok('-1001' in dj['chats'] and dj['threads'].get('user_id') == '777', 'чаты и ключ Threads сохранены на диск')

print('\nИТОГО: %d проверок пройдено, %d провалено' % (len(OKS), len(FAILS)))
for x in FAILS:
    print('  ПРОВАЛ:', x)
shutil.rmtree(HOME, ignore_errors=True)
sys.exit(1 if FAILS else 0)
