# -*- coding: utf-8 -*-
"""Поддельные серверы: Телеграм, Anthropic, Threads, GitHub, YouTube/Google — всё на одном порту."""
import json, re, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = '123:TEST'


class State:
    def __init__(self):
        self.calls = []          # (метод, путь, разобранное тело)
        self.updates = []
        self.files = {}          # file_id -> bytes
        self.tg_msgs = 0
        self.yt_pos = 0
        self.yt_size = 0
        self.yt_ranges = []
        self.threads_created = []
        self.anthropic_reqs = []
        self.gh_puts = []
        self.fail = {}           # имя -> код ошибки, который надо вернуть один раз
        self.lock = threading.Lock()
        self.port = 0

    def find(self, path_part):
        return [c for c in self.calls if path_part in c[1]]


ST = State()


def parse_multipart(body, ctype):
    m = re.search(r'boundary=(.+)$', ctype)
    bd = ('--' + m.group(1)).encode()
    out = {}
    for part in body.split(bd):
        if b'Content-Disposition' not in part:
            continue
        head, _, data = part.partition(b'\r\n\r\n')
        data = data.rsplit(b'\r\n', 1)[0]
        nm = re.search(rb'name="([^"]+)"', head).group(1).decode()
        fn = re.search(rb'filename="([^"]+)"', head)
        out[nm] = ('FILE:%s:%d' % (fn.group(1).decode(), len(data))) if fn else data.decode('utf-8')
    return out


class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *a):
        pass

    def _body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return self.rfile.read(n) if n else b''

    def _send(self, code, obj=None, headers=None, raw=None):
        data = raw if raw is not None else json.dumps(obj if obj is not None else {}).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.route('GET')

    def do_POST(self):
        self.route('POST')

    def do_PUT(self):
        self.route('PUT')

    def route(self, method):
        u = urllib.parse.urlsplit(self.path)
        path, q = u.path, dict(urllib.parse.parse_qsl(u.query))
        body = self._body()
        ctype = self.headers.get('Content-Type', '')
        parsed = None
        if 'json' in ctype:
            try:
                parsed = json.loads(body.decode('utf-8'))
            except Exception:
                parsed = None
        elif 'multipart' in ctype:
            parsed = parse_multipart(body, ctype)
        elif 'x-www-form' in ctype:
            parsed = dict(urllib.parse.parse_qsl(body.decode()))
        with ST.lock:
            ST.calls.append((method, self.path, parsed))
        try:
            self.dispatch(method, path, q, body, parsed)
        except Exception as e:  # pragma: no cover
            import traceback
            traceback.print_exc()
            self._send(500, {'error': {'message': 'fake crashed: %s' % e}})

    # ----------------------------------------------------------------
    def dispatch(self, method, path, q, body, p):
        # ---- Telegram ----
        m = re.match(r'^/bot([^/]+)/(\w+)$', path)
        if m:
            return self.telegram(m.group(1), m.group(2), p)
        m = re.match(r'^/file/bot([^/]+)/(.+)$', path)
        if m:
            fid = m.group(2).split('/')[-1]
            return self._send(200, raw=ST.files.get(fid, b'x'))
        # ---- Anthropic ----
        if path == '/v1/messages':
            ST.anthropic_reqs.append((self.headers.get('x-api-key'), p))
            if self.headers.get('x-api-key') != 'good-key':
                return self._send(401, {'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}})
            txt = json.dumps({
                'telegram': 'Тугар вышел на тропу войны! 🔥\n\nПопробуй уложить его с первого выстрела.\n\nИграть: {L}',
                'threads': 'Кто бы мог подумать, что степной хан так боится одного самопала? #козаки',
                'youtube_title': 'Тугар против самопала: кто кого?',
                'youtube_desc': 'Бой с боссом в казацкой игре.\n#Shorts #игра',
                'card_title': 'Тугар вышел на тропу', 'card_sub': 'Попробуй уложить его'}, ensure_ascii=False)
            return self._send(200, {'content': [{'type': 'text', 'text': 'Вот посты:\n' + txt}]})
        # ---- Threads ----
        if path == '/oauth/access_token':
            if p.get('code') == 'BADCODE0123456789':
                return self._send(400, {'error_message': 'Invalid authorization code'})
            return self._send(200, {'access_token': 'SHORT', 'user_id': 777})
        if path == '/access_token':
            return self._send(200, {'access_token': 'LONG-' + q.get('access_token', ''), 'expires_in': 5184000})
        if path == '/refresh_access_token':
            return self._send(200, {'access_token': 'REFRESHED', 'expires_in': 5184000})
        if path == '/v1.0/me':
            return self._send(200, {'id': '777', 'username': 'kozak_dev'})
        if re.match(r'^/v1\.0/777/threads$', path):
            ST.threads_created.append(p)
            if ST.fail.pop('threads_create', None):
                return self._send(400, {'error': {'message': 'Unsupported image format'}})
            return self._send(200, {'id': 'C%d' % len(ST.threads_created)})
        if re.match(r'^/v1\.0/C\d+$', path):
            ST.threads_poll = getattr(ST, 'threads_poll', 0) + 1
            if ST.threads_poll % 2:
                return self._send(200, {'status': 'IN_PROGRESS', 'id': path[-2:]})
            return self._send(200, {'status': 'FINISHED', 'id': path[-2:]})
        if path == '/v1.0/777/threads_publish':
            return self._send(200, {'id': 'POST1'})
        if path == '/v1.0/POST1':
            return self._send(200, {'permalink': 'https://www.threads.com/@kozak_dev/post/POST1', 'id': 'POST1'})
        # ---- GitHub ----
        m = re.match(r'^/repos/([^/]+/[^/]+)/contents/(.+)$', path)
        if m and method == 'PUT':
            ST.gh_puts.append((m.group(2), self.headers.get('Authorization'), len(p.get('content', ''))))
            return self._send(201, {'content': {'download_url': 'http://127.0.0.1:%d/raw/%s' % (ST.port, m.group(2))}})
        # ---- Google / YouTube ----
        if path == '/token':
            if p.get('grant_type') == 'authorization_code':
                return self._send(200, {'access_token': 'YTACC', 'refresh_token': 'YTREF', 'expires_in': 3600})
            return self._send(200, {'access_token': 'YTACC2', 'expires_in': 3600})
        if path == '/upload/youtube/v3/videos':
            if method == 'POST':
                ST.yt_init = (q, p, dict(self.headers))
                ST.yt_size = int(self.headers.get('X-Upload-Content-Length') or 0)
                ST.yt_pos = 0
                return self._send(200, {}, {'Location': 'http://127.0.0.1:%d/upload/session/1' % ST.port})
        if path == '/upload/session/1' and method == 'PUT':
            cr = self.headers.get('Content-Range')
            mm = re.match(r'bytes (\d+)-(\d+)/(\d+)', cr)
            a, b, tot = map(int, mm.groups())
            ST.yt_ranges.append((a, b, tot, len(body)))
            if a != ST.yt_pos:
                return self._send(400, {'error': {'message': 'bad offset %d != %d' % (a, ST.yt_pos)}})
            ST.yt_pos = b + 1
            if ST.yt_pos >= tot:
                return self._send(200, {'id': 'VID123'})
            return self._send(308, {}, {'Range': 'bytes=0-%d' % b})
        if path.startswith('/upd/'):
            name = path[5:]
            if name == 'latest.json':
                return self._send(200, getattr(ST, 'upd_json', {}))
            if name in getattr(ST, 'upd_files', {}):
                return self._send(200, raw=ST.upd_files[name])
        self._send(404, {'error': {'message': 'fake: no route %s %s' % (method, path)}})

    # ----------------------------------------------------------------
    def telegram(self, token, method, p):
        if token != TOKEN:
            return self._send(401, {'ok': False, 'error_code': 401, 'description': 'Unauthorized'})
        p = p or {}
        ok = lambda r: self._send(200, {'ok': True, 'result': r})
        if method == 'getMe':
            return ok({'id': 1, 'username': 'mktbot', 'is_bot': True})
        if method == 'getUpdates':
            with ST.lock:
                ups, ST.updates = ST.updates, []
            return ok(ups)
        if method in ('sendMessage', 'sendPhoto', 'sendVideo'):
            if str(p.get('chat_id')) == '-100999':
                return self._send(403, {'ok': False, 'error_code': 403, 'description': 'Forbidden: bot is not a member of the channel chat'})
            ST.tg_msgs += 1
            r = {'message_id': 1000 + ST.tg_msgs, 'chat': {'id': int(p['chat_id']), 'type': 'channel', 'username': 'pustosh_news' if str(p['chat_id']) == '-100500' else None}}
            if not r['chat']['username']:
                del r['chat']['username']
            return ok(r)
        if method == 'editMessageText':
            return ok(True)
        if method in ('answerCallbackQuery', 'deleteMessage'):
            return ok(True)
        if method == 'getFile':
            fid = p['file_id']
            if fid == 'BIG':
                return self._send(400, {'ok': False, 'error_code': 400, 'description': 'Bad Request: file is too big'})
            return ok({'file_id': fid, 'file_path': 'documents/' + fid})
        if method == 'getChat':
            if str(p.get('chat_id')) == '@pustosh_news':
                return ok({'id': -100500, 'type': 'channel', 'title': 'Пустошь — новости', 'username': 'pustosh_news'})
            return self._send(400, {'ok': False, 'error_code': 400, 'description': 'Bad Request: chat not found'})
        self._send(404, {'ok': False, 'error_code': 404, 'description': 'no method ' + method})


def start():
    srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
    ST.port = srv.server_port
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, ST
