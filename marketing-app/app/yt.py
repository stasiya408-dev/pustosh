# -*- coding: utf-8 -*-
"""YouTube Shorts: вход через браузер (один раз) и загрузка ролика."""
import json, os, threading, time, urllib.parse, urllib.error, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import net
import cfg
from cfg import env, BASE

AUTH = env('YT_AUTH_URL', 'https://accounts.google.com/o/oauth2/v2/auth')
TOKEN = env('YT_TOKEN_URL', 'https://oauth2.googleapis.com/token')
UP = env('YT_UPLOAD_URL', 'https://www.googleapis.com/upload/youtube/v3/videos')
SCOPE = 'https://www.googleapis.com/auth/youtube.upload'
SECRET_FILE = os.path.join(BASE, 'client_secret.json')
TOKEN_FILE = os.path.join(BASE, 'yt_token.json')
CHUNK = 8 * 1024 * 1024  # кратно 256 КБ


def client():
    with open(SECRET_FILE, encoding='utf-8') as f:
        j = json.load(f)
    c = j.get('installed') or j.get('web') or {}
    if not c.get('client_id'):
        raise net.NetError('в client_secret.json нет client_id')
    return c


def has_client():
    return os.path.exists(SECRET_FILE)


def connected():
    return os.path.exists(TOKEN_FILE)


def status():
    if not has_client():
        return 'нет файла client_secret.json'
    if not connected():
        return 'файл есть, но вход не выполнен'
    return 'подключён'


def _read_token():
    with open(TOKEN_FILE, encoding='utf-8') as f:
        return json.load(f)


def login(timeout=240, open_browser=True, on_url=None):
    """Открывает браузер на этом компьютере, ждёт разрешения, сохраняет ключ."""
    c = client()
    got = {}

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            got['code'] = (q.get('code') or [''])[0]
            got['err'] = (q.get('error') or [''])[0]
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write('<meta charset="utf-8"><h2>Готово! Можно закрыть эту вкладку и вернуться в Телеграм.</h2>'.encode('utf-8'))

        def log_message(self, *a):
            pass

    srv = HTTPServer(('127.0.0.1', 0), H)
    srv.timeout = 1
    redirect = 'http://127.0.0.1:%d' % srv.server_port
    url = AUTH + '?' + urllib.parse.urlencode({
        'client_id': c['client_id'], 'redirect_uri': redirect, 'response_type': 'code', 'scope': SCOPE,
        'access_type': 'offline', 'prompt': 'consent'})
    if on_url:
        on_url(url)
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    t0 = time.time()
    while not got and time.time() - t0 < timeout:
        srv.handle_request()
    srv.server_close()
    if not got.get('code'):
        raise net.NetError('вход не завершён' + (' (%s)' % got['err'] if got.get('err') else ''))
    st, d = net.post_form(TOKEN, {'client_id': c['client_id'], 'client_secret': c.get('client_secret', ''),
                                  'code': got['code'], 'redirect_uri': redirect, 'grant_type': 'authorization_code'})
    if st != 200 or not d.get('refresh_token'):
        raise net.NetError('Google: ' + net.api_err(d, st), st)
    d['expires_at'] = cfg.now() + int(d.get('expires_in', 3600)) - 60
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(d, f)
    return True


def access_token():
    if not connected():
        raise net.NetError('YouTube не подключён')
    t = _read_token()
    if t.get('access_token') and t.get('expires_at', 0) > cfg.now():
        return t['access_token']
    c = client()
    st, d = net.post_form(TOKEN, {'client_id': c['client_id'], 'client_secret': c.get('client_secret', ''),
                                  'refresh_token': t['refresh_token'], 'grant_type': 'refresh_token'})
    if st != 200 or not d.get('access_token'):
        raise net.NetError('вход в YouTube устарел, подключи заново кнопкой в «Подключениях» (%s)' % net.api_err(d, st), st)
    t['access_token'] = d['access_token']
    t['expires_at'] = cfg.now() + int(d.get('expires_in', 3600)) - 60
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(t, f)
    return t['access_token']


def _friendly(d, st):
    e = (d.get('error') or {}) if isinstance(d, dict) else {}
    reasons = [x.get('reason') for x in e.get('errors', []) if isinstance(x, dict)]
    if 'quotaExceeded' in reasons or 'uploadLimitExceeded' in reasons:
        return 'на сегодня лимит YouTube исчерпан, попробуй завтра'
    if 'youtubeSignupRequired' in reasons:
        return 'у этого Google-аккаунта нет канала YouTube'
    return net.api_err(d, st)


def upload(path, title, desc, privacy='public', tags=None, progress=None):
    """Загружает видео. Возвращает ссылку."""
    tok = access_token()
    size = os.path.getsize(path)
    if size <= 0:
        raise net.NetError('пустой файл')
    meta = {'snippet': {'title': (title or 'Пустошь')[:100], 'description': (desc or '')[:4900],
                        'tags': tags or [], 'categoryId': '20'},
            'status': {'privacyStatus': privacy if privacy in ('public', 'unlisted', 'private') else 'public',
                       'selfDeclaredMadeForKids': False}}
    mt = 'video/mp4' if path.lower().endswith('.mp4') else ('video/quicktime' if path.lower().endswith('.mov') else 'video/*')
    body = json.dumps(meta, ensure_ascii=False).encode('utf-8')
    st, h, b = net.request('POST', UP + '?uploadType=resumable&part=snippet,status', {
        'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
        'X-Upload-Content-Length': str(size), 'X-Upload-Content-Type': mt}, body, 60)
    if st != 200 or not h.get('Location'):
        raise net.NetError('YouTube: ' + _friendly(net.jload(b), st), st)
    loc = h['Location']
    pos = 0
    with open(path, 'rb') as f:
        while pos < size:
            f.seek(pos)
            chunk = f.read(CHUNK)
            end = pos + len(chunk) - 1
            for attempt in range(4):
                try:
                    st, h, b = net.request('PUT', loc, {
                        'Content-Length': str(len(chunk)), 'Content-Range': 'bytes %d-%d/%d' % (pos, end, size),
                        'Content-Type': mt}, chunk, 600)
                except net.NetError:
                    if attempt == 3:
                        raise
                    time.sleep(2 * (attempt + 1))
                    continue
                if st in (200, 201):
                    vid = net.jload(b).get('id')
                    if not vid:
                        raise net.NetError('YouTube не вернул номер ролика')
                    if progress:
                        progress(100)
                    return 'https://youtu.be/' + vid
                if st == 308:
                    rng = h.get('Range')
                    pos = int(rng.split('-')[1]) + 1 if rng else 0
                    if progress:
                        progress(int(pos * 100 / size))
                    break
                if st >= 500 and attempt < 3:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise net.NetError('YouTube: ' + _friendly(net.jload(b), st), st)
            else:
                raise net.NetError('YouTube не принял часть файла')
    raise net.NetError('загрузка не завершилась')
