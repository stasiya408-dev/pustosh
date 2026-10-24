# -*- coding: utf-8 -*-
"""Публикация: Телеграм-чаты, Threads (+ хостинг картинки на GitHub)."""
import base64, os, re, time, uuid
import net
import cfg
from cfg import env, S

TB = env('THREADS_BASE', 'https://graph.threads.com')
THREADS_AUTH = env('THREADS_AUTH_URL', 'https://threads.com/oauth/authorize')
GH_API = env('GITHUB_API', 'https://api.github.com')
POLL = float(env('THREADS_POLL', '3'))


# ======================= хостинг файла (для Threads) =======================
def host_ready():
    return bool(env('GITHUB_TOKEN')) and bool(env('GITHUB_MEDIA_REPO')) and '/' in env('GITHUB_MEDIA_REPO')


def host_file(path):
    """Кладёт файл в публичный GitHub-репозиторий и возвращает прямую ссылку."""
    if not host_ready():
        raise net.NetError('не настроен GITHUB_TOKEN / GITHUB_MEDIA_REPO')
    repo = env('GITHUB_MEDIA_REPO')
    name = 'p/%d_%s%s' % (cfg.now(), uuid.uuid4().hex[:6], os.path.splitext(path)[1].lower())
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    url = '%s/repos/%s/contents/%s' % (GH_API, repo, name)
    st, d, h = _gh_put(url, b64)
    if st not in (200, 201):
        raise net.NetError('GitHub: ' + net.api_err(d, st), st)
    return d['content']['download_url']


def _gh_put(url, b64):
    import json
    body = json.dumps({'message': 'media', 'content': b64}).encode()
    st, h, b = net.request('PUT', url, {
        'Authorization': 'Bearer ' + env('GITHUB_TOKEN'), 'Accept': 'application/vnd.github+json',
        'User-Agent': 'pustosh-marketing-bot', 'Content-Type': 'application/json'}, body, 300)
    return st, net.jload(b), h


# ======================= Threads =======================
def threads_ready():
    return bool(S.get('threads', {}).get('token')) and bool(S.get('threads', {}).get('user_id'))


def threads_status():
    t = S.get('threads', {})
    if not t.get('token'):
        return 'не подключён'
    left = (t.get('expires', 0) - cfg.now()) / 86400.0
    return 'подключён%s, ключ действует ещё ~%d дн.' % ((' как @' + t['username']) if t.get('username') else '', max(0, int(left)))


def threads_app_ready():
    return bool(env('THREADS_APP_ID')) and bool(env('THREADS_APP_SECRET'))


def threads_redirect():
    return env('THREADS_REDIRECT_URI', 'https://stasiya408-dev.github.io/pustosh/')


def threads_auth_link():
    import urllib.parse
    q = urllib.parse.urlencode({'client_id': env('THREADS_APP_ID'), 'redirect_uri': threads_redirect(),
                                'scope': 'threads_basic,threads_content_publish', 'response_type': 'code'})
    return THREADS_AUTH + '?' + q


def _save_threads(token, user_id, expires_in, username=None):
    t = S.setdefault('threads', {})
    t['token'] = token
    t['user_id'] = str(user_id)
    t['saved'] = cfg.now()
    t['expires'] = cfg.now() + int(expires_in or 60 * 86400)
    if username:
        t['username'] = username
    cfg.save()


def threads_login_code(text):
    """Принимает адрес из браузера (или сам код), подключает Threads. Возвращает @имя."""
    m = re.search(r'[?&]code=([^&#\s]+)', text)
    code = m.group(1) if m else text.strip().split('#')[0]
    if len(code) < 10:
        raise net.NetError('не нашёл код в сообщении')
    st, d = net.post_form(TB + '/oauth/access_token', {
        'client_id': env('THREADS_APP_ID'), 'client_secret': env('THREADS_APP_SECRET'),
        'code': code, 'grant_type': 'authorization_code', 'redirect_uri': threads_redirect()})
    if st != 200 or not d.get('access_token'):
        raise net.NetError('Threads: ' + (d.get('error_message') or net.api_err(d, st)), st)
    short, uid = d['access_token'], d.get('user_id')
    st, d = net.get_json(TB + '/access_token', {'grant_type': 'th_exchange_token',
                                                'client_secret': env('THREADS_APP_SECRET'), 'access_token': short})
    if st != 200 or not d.get('access_token'):
        raise net.NetError('Threads (долгий ключ): ' + net.api_err(d, st), st)
    return _finish_threads(d['access_token'], uid, d.get('expires_in'))


def threads_login_token(token):
    """Если у тебя уже есть готовый ключ Threads."""
    token = token.strip()
    exp = None
    if env('THREADS_APP_SECRET'):
        st, d = net.get_json(TB + '/access_token', {'grant_type': 'th_exchange_token',
                                                    'client_secret': env('THREADS_APP_SECRET'), 'access_token': token})
        if st == 200 and d.get('access_token'):
            token, exp = d['access_token'], d.get('expires_in')
    return _finish_threads(token, None, exp)


def _finish_threads(token, uid, exp):
    st, d = net.get_json(TB + '/v1.0/me', {'fields': 'id,username', 'access_token': token})
    if st != 200:
        raise net.NetError('Threads не принял ключ: ' + net.api_err(d, st), st)
    _save_threads(token, d.get('id') or uid, exp or 59 * 86400, d.get('username'))
    return d.get('username') or str(d.get('id'))


def threads_refresh_if_needed():
    """Раз в сутки: если ключ скоро кончится, продлеваем на 60 дней."""
    t = S.get('threads', {})
    if not t.get('token'):
        return
    now = cfg.now()
    if t.get('expires', 0) - now > 20 * 86400 or now - t.get('saved', 0) < 86400:
        return
    st, d = net.get_json(TB + '/refresh_access_token', {'grant_type': 'th_refresh_token', 'access_token': t['token']})
    if st == 200 and d.get('access_token'):
        _save_threads(d['access_token'], t['user_id'], d.get('expires_in'), t.get('username'))


def threads_publish(text, media_path=None, media_kind=None):
    """Публикует пост. Возвращает (ссылка, предупреждение)."""
    t = S.get('threads', {})
    if not t.get('token'):
        raise net.NetError('Threads не подключён')
    tok, uid = t['token'], t['user_id']
    warn = ''
    p = {'access_token': tok, 'text': text[:500], 'media_type': 'TEXT'}
    if media_path:
        if host_ready():
            url = host_file(media_path)
            if media_kind == 'video':
                p.update(media_type='VIDEO', video_url=url)
            else:
                p.update(media_type='IMAGE', image_url=url)
        else:
            warn = 'без картинки: не настроен GitHub-хостинг (см. инструкцию)'
    st, d = net.post_form('%s/v1.0/%s/threads' % (TB, uid), p)
    if st != 200 or not d.get('id'):
        raise net.NetError('Threads: ' + net.api_err(d, st), st)
    cid = d['id']
    for i in range(80):
        st, d = net.get_json('%s/v1.0/%s' % (TB, cid), {'fields': 'status,error_message', 'access_token': tok})
        s = d.get('status')
        if s in ('FINISHED', 'PUBLISHED') or (st == 200 and not s):
            break
        if s in ('ERROR', 'EXPIRED'):
            raise net.NetError('Threads не принял файл: ' + str(d.get('error_message') or s))
        time.sleep(POLL)
    st, d = net.post_form('%s/v1.0/%s/threads_publish' % (TB, uid), {'creation_id': cid, 'access_token': tok})
    if st != 200 or not d.get('id'):
        raise net.NetError('Threads: ' + net.api_err(d, st), st)
    pid = d['id']
    link = ''
    try:
        st, d = net.get_json('%s/v1.0/%s' % (TB, pid), {'fields': 'permalink', 'access_token': tok})
        link = d.get('permalink', '')
    except Exception:
        pass
    return link, warn
