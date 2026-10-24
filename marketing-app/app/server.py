# -*- coding: utf-8 -*-
"""Окно программы: маленький локальный сервер (только для этого компьютера) + страница интерфейса."""
import json, mimetypes, os, platform, random, re, secrets, shutil, socket, subprocess, sys, threading, time, traceback, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cfg, net, gen, card, pubs, yt, cats, jobs, update, version, tgu, imggen
from cfg import env, S

UI_DIR = os.path.join(cfg.CODE, 'ui')
TOKEN = secrets.token_urlsafe(18)
RUN_FILE = os.path.join(cfg.BASE, 'run.json')
LOG_FILE = os.path.join(cfg.BASE, 'app.log')
IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp')
VIDEO_EXT = ('.mp4', '.mov', '.m4v', '.webm')
IDLE_EXIT = int(os.environ.get('MKT_IDLE_EXIT', '180'))      # секунд без сигнала от окна -> программа закрывается

LAST_PING = [time.time()]
UPD = {'info': None, 'error': ''}
YT_LOGIN = {'state': 'idle', 'url': '', 'msg': ''}
PORT = [0]


def log(*a):
    try:
        print(time.strftime('%H:%M:%S'), *a, flush=True)
    except Exception:
        pass


def make_tg():
    spec = os.environ.get('MKT_TG_IMPL')                # для тестов: "модуль:Класс"
    if spec:
        mod, _, cls = spec.partition(':')
        import importlib
        return getattr(importlib.import_module(mod), cls)()
    return tgu.TgUser()


TG = make_tg()


class ApiError(Exception):
    pass


def err(msg):
    raise ApiError(msg)


# ======================================================================= черновик
def new_draft():
    return {'media': None, 'thumb': None, 'note': '', 'texts': None, 'card_on': True, 'card_title': '', 'card_sub': '',
            'card_path': None, 'threads': False, 'yt': False}


DRAFT = new_draft()
DRAFT['threads'] = bool(S.get('t_threads'))
DRAFT['yt'] = bool(S.get('t_yt'))


def media_url(path):
    return '/media/' + urllib.parse.quote(os.path.basename(path)) if path else ''


def public_draft():
    d = DRAFT
    m = d['media']
    return {
        'media': ({'kind': m['kind'], 'url': media_url(m['path']), 'name': m.get('name', ''), 'w': m.get('w'), 'h': m.get('h'),
                   'dur': m.get('dur')} if m else None),
        'has_thumb': bool(d['thumb']), 'note': d['note'], 'texts': d['texts'], 'card_on': d['card_on'],
        'card_title': d['card_title'], 'card_sub': d['card_sub'], 'card_url': media_url(d['card_path']),
        'threads': d['threads'], 'yt': d['yt'], 'tg_ids': selected_tg(),
    }


def selected_tg():
    return [cid for cid, c in S['chats'].items() if c.get('sel') and c.get('can_write')]


def banner():
    l = env('GAME_BOT_LINK')
    if not l or 'ВАШ' in l:
        return 'Играть в Телеграме'
    return 'Играть: ' + re.sub(r'^https?://', '', l)


def drop_card():
    p = DRAFT.get('card_path')
    if p and os.path.exists(p):
        try:
            os.remove(p)
        except OSError:
            pass
    DRAFT['card_path'] = None


def make_card():
    drop_card()
    m = DRAFT['media']
    if m and m['kind'] == 'photo' and DRAFT['card_on'] and card.available() and DRAFT['texts']:
        out = os.path.join(cfg.MEDIA, 'card_%d.jpg' % int(time.time() * 1000))
        card.make_card(m['path'], DRAFT['card_title'], DRAFT['card_sub'], banner(), out)
        DRAFT['card_path'] = out


# ---------- дополнительные картинки от GPT ----------
EXTRA_LOCK = threading.RLock()
EXTRA = {'gen': 0, 'state': 'idle', 'msg': '', 'items': [], 'base': None, 'base_name': '', 'n': 0, 'started': 0, 'model': '', 'seq': 0}
EXTRA_MAX = 12


def _in_media(p):
    return bool(p) and os.path.dirname(os.path.abspath(p)) == os.path.abspath(cfg.MEDIA)


def _rm(p):
    if _in_media(p) and os.path.exists(p):
        try:
            os.remove(p)
        except OSError:
            pass


def extra_reset():
    """Новый файл (или файл убрали): картинки GPT от прошлого фото больше не нужны."""
    with EXTRA_LOCK:
        for it in EXTRA['items']:
            _rm(it['path'])
        _rm(EXTRA['base'])
        EXTRA.update(gen=EXTRA['gen'] + 1, state='idle', msg='', items=[], base=None, base_name='', n=0, started=0, model='')


def extra_view():
    with EXTRA_LOCK:
        EXTRA['items'] = [i for i in EXTRA['items'] if os.path.exists(i['path'])]
        m = DRAFT['media']
        cur = m['path'] if m else None
        used = None
        if cur and EXTRA['base'] and cur == EXTRA['base']:
            used = 'orig'
        for i in EXTRA['items']:
            if cur and i['path'] == cur:
                used = i['id']
        return {'state': EXTRA['state'], 'msg': EXTRA['msg'], 'n': EXTRA['n'], 'started': EXTRA['started'], 'model': EXTRA['model'],
                'ready': imggen.ready(),
                'base': ({'url': media_url(EXTRA['base']), 'name': EXTRA['base_name']} if EXTRA['base'] and os.path.exists(EXTRA['base']) else None),
                'items': [{'id': i['id'], 'url': media_url(i['path']), 'w': i['w'], 'h': i['h']} for i in EXTRA['items']],
                'used': used}


def clear_media():
    extra_reset()
    for k in ('media', 'thumb'):
        v = DRAFT[k]
        p = v['path'] if isinstance(v, dict) else v
        if p and os.path.exists(p) and os.path.dirname(os.path.abspath(p)) == os.path.abspath(cfg.MEDIA):
            try:
                os.remove(p)
            except OSError:
                pass
        DRAFT[k] = None
    drop_card()
    DRAFT['texts'] = None


# ======================================================================= состояние
def chat_list():
    out = []
    for cid, c in S['chats'].items():
        d = dict(c)
        d['id'] = cid
        out.append(d)
    out.sort(key=lambda c: (c.get('title') or '').lower())
    return out


def settings_view():
    v = {}
    for k in cfg.SETTING_KEYS:
        if k in cfg.SECRET_KEYS:
            v[k] = {'set': bool(env(k)), 'hint': cfg.masked(k)}
        else:
            v[k] = env(k)
    return v


def state():
    dmin, dmax, limit = jobs.tg_limits()
    cur = jobs.CURRENT
    return {
        'version': version.VERSION,
        'update': UPD['info'], 'update_error': UPD['error'],
        'conn': {
            'ai': gen.ai_ready(), 'card': card.available(), 'tg': TG.status(),
            'threads': {'ready': pubs.threads_ready(), 'text': pubs.threads_status(), 'app': pubs.threads_app_ready(),
                        'redirect': pubs.threads_redirect()},
            'yt': {'client': yt.has_client(), 'connected': yt.connected(), 'text': yt.status(), 'login': dict(YT_LOGIN)},
            'host': pubs.host_ready(), 'gpt': imggen.ready(),
        },
        'settings': settings_view(),
        'cats': cats.categories(),
        'chats': chat_list(),
        'tg_today': {'sent': jobs.sent_today(), 'limit': limit, 'dmin': dmin, 'dmax': dmax},
        'draft': public_draft(),
        'extra': extra_view(),
        'job': cur.snap() if cur else None,
    }


# ======================================================================= маршруты API
def api_state(q, b):
    return state()


def api_ping(q, b):
    LAST_PING[0] = time.time()
    return {'ok': True, 'version': version.VERSION}


def api_settings(q, b):
    cfg.set_settings({k: v for k, v in b.items() if k in cfg.SETTING_KEYS and not (k in cfg.SECRET_KEYS and v == '')})
    for k in b.get('clear', []):
        if k in cfg.SETTING_KEYS:
            cfg.S['settings'].pop(k, None)
    cfg.save()
    return state()


def api_draft(q, b):
    d = DRAFT
    redo_card = False
    if 'note' in b:
        d['note'] = str(b['note'])[:2000]
    if 'texts' in b and isinstance(b['texts'], dict) and d['texts']:
        for k in ('telegram', 'threads', 'youtube_title', 'youtube_desc'):
            if isinstance(b['texts'].get(k), str):
                d['texts'][k] = b['texts'][k]
    for k, flag in (('threads', 't_threads'), ('yt', 't_yt')):
        if k in b:
            d[k] = bool(b[k])
            S[flag] = d[k]
    if 'card_on' in b:
        d['card_on'] = bool(b['card_on'])
        redo_card = True
    for k in ('card_title', 'card_sub'):
        if k in b and isinstance(b[k], str):
            d[k] = b[k][:80]
            redo_card = True
    if redo_card or b.get('redo_card'):
        make_card()
    cfg.save()
    return {'draft': public_draft()}


def api_media_meta(q, b):
    m = DRAFT['media']
    if m:
        for k in ('w', 'h', 'dur'):
            if b.get(k):
                try:
                    m[k] = int(float(b[k]))
                except (TypeError, ValueError):
                    pass
    return {'draft': public_draft()}


def api_media_clear(q, b):
    clear_media()
    return {'draft': public_draft()}


def api_generate(q, b):
    d = DRAFT
    if not (selected_tg() or d['threads'] or d['yt']):
        err('Сначала выбери, куда публиковать (Telegram-чаты, Threads или YouTube)')
    if not d['media'] and not d['note'].strip():
        err('Добавь фото или видео из игры или напиши в заметке, о чём пост')
    warn = ''
    img = None
    if d['media'] and d['media']['kind'] == 'photo':
        img = d['media']['path']
    elif d['thumb']:
        img = d['thumb']
    try:
        t = gen.generate(d['note'], img, b.get('extra', ''))
        if not gen.ai_ready():
            warn = 'Ключ Claude не введён, поэтому текст простой. Введи ключ во вкладке «Подключения».'
    except net.NetError as e:
        t = gen.fallback(d['note'])
        warn = e.msg + '. Сделал простой вариант без ИИ.'
    d['texts'] = t
    d['card_title'], d['card_sub'] = t['card_title'], t['card_sub']
    try:
        make_card()
    except Exception as e:
        drop_card()
        warn = (warn + ' ' if warn else '') + 'Картинку с надписью сделать не вышло (%s). Пойдёт исходное фото.' % e
    return {'draft': public_draft(), 'warn': warn}


def _extra_worker(token, ref, idea, note, n, size, quality):
    try:
        res, model = imggen.generate(ref, idea, note, n, size, quality, log)
        err_msg = ''
    except net.NetError as e:
        res, model, err_msg = [], '', e.msg
    except Exception as e:
        traceback.print_exc()
        res, model, err_msg = [], '', 'Ошибка программы: %s' % e
    with EXTRA_LOCK:
        if EXTRA['gen'] != token:                     # пока рисовалось, файл заменили — результат не нужен
            for r in res:
                _rm(r['path'])
            return
        for r in res:
            EXTRA['seq'] += 1
            EXTRA['items'].append({'id': 'g%d' % EXTRA['seq'], 'path': r['path'], 'w': r['w'], 'h': r['h']})
        while len(EXTRA['items']) > EXTRA_MAX:       # слишком много — выбрасываем самые старые, кроме выбранной
            cur = DRAFT['media']['path'] if DRAFT['media'] else None
            victim = next((i for i in EXTRA['items'] if i['path'] != cur), None)
            if not victim:
                break
            EXTRA['items'].remove(victim)
            _rm(victim['path'])
        EXTRA['model'] = model
        EXTRA['state'] = 'error' if err_msg else 'done'
        EXTRA['msg'] = err_msg


def api_extra_start(q, b):
    d = DRAFT
    if not imggen.ready():
        err('Нужен ключ OpenAI (вкладка «Подключения»): через него GPT рисует картинки')
    m = d['media']
    if m and m['kind'] == 'photo':
        ref = EXTRA['base'] if (EXTRA['base'] and os.path.exists(EXTRA['base'])) else m['path']   # образец — всегда исходное фото
    elif m and d['thumb']:
        ref = d['thumb']
    elif m:
        err('Не получилось взять кадр из ролика. Загрузи фото из игры — GPT будет рисовать по нему.')
    else:
        err('Сначала добавь фото из игры — GPT нарисует новые картинки по его образцу')
    with EXTRA_LOCK:
        if EXTRA['state'] == 'running':
            err('GPT уже рисует, дождись окончания')
        if not EXTRA['base'] and m['kind'] == 'photo':
            EXTRA['base'], EXTRA['base_name'] = m['path'], m.get('name', '')
        try:
            n = max(1, min(4, int(b.get('n') or 2)))
        except (TypeError, ValueError):
            n = 2
        size = b.get('size') if b.get('size') in imggen.SIZES else 'tall'
        quality = b.get('quality') if b.get('quality') in imggen.QUALITY else 'medium'
        EXTRA.update(state='running', msg='', n=n, started=int(time.time()))
        token = EXTRA['gen']
    threading.Thread(target=_extra_worker, daemon=True,
                     args=(token, ref, str(b.get('idea') or '')[:600], d['note'], n, size, quality)).start()
    return {'extra': extra_view()}


def api_extra_use(q, b):
    d = DRAFT
    if jobs.running():
        err('Идёт публикация, дождись окончания')
    pid = str(b.get('id') or '')
    with EXTRA_LOCK:
        if pid == 'orig' and EXTRA['base'] and os.path.exists(EXTRA['base']):
            path, name, w, h = EXTRA['base'], EXTRA['base_name'] or 'Исходное фото', None, None
        else:
            it = next((i for i in EXTRA['items'] if i['id'] == pid and os.path.exists(i['path'])), None)
            if not it:
                err('Такой картинки уже нет')
            path, name, w, h = it['path'], 'Картинка GPT', it['w'], it['h']
        old = d['media']
        if old and old['path'] == path:
            return {'draft': public_draft(), 'extra': extra_view()}
        d['media'] = {'kind': 'photo', 'path': path, 'name': name, 'w': w, 'h': h, 'dur': None}
        if old and not any(old['path'] == x for x in [EXTRA['base']] + [i['path'] for i in EXTRA['items']]):
            _rm(old['path'])                           # заменили ролик или чужой файл — он больше не нужен
        if d['thumb'] and old and old['kind'] == 'video':
            _rm(d['thumb'])
            d['thumb'] = None
    try:
        make_card()
    except Exception as e:
        drop_card()
        log('картинка с надписью не вышла:', e)
    return {'draft': public_draft(), 'extra': extra_view()}


def api_extra_drop(q, b):
    pid = str(b.get('id') or '')
    with EXTRA_LOCK:
        cur = DRAFT['media']['path'] if DRAFT['media'] else None
        it = next((i for i in EXTRA['items'] if i['id'] == pid), None)
        if it and it['path'] != cur:
            EXTRA['items'].remove(it)
            _rm(it['path'])
    return {'extra': extra_view()}


def api_publish(q, b):
    d = DRAFT
    if jobs.running():
        err('Публикация уже идёт, дождись окончания')
    if b.get('texts'):
        api_draft({}, {'texts': b['texts']})
    if not d['texts']:
        err('Сначала нажми «Сгенерировать пост»')
    targets = {'yt': d['yt'], 'threads': d['threads'], 'tg': selected_tg()}
    if not (targets['yt'] or targets['threads'] or targets['tg']):
        err('Выбери, куда публиковать')
    if targets['threads'] and not pubs.threads_ready():
        err('Threads не подключён (вкладка «Подключения»)')
    if targets['yt'] and not yt.connected():
        err('YouTube не подключён (вкладка «Подключения»)')
    if targets['tg'] and TG.status()['state'] != 'ready':
        err('Вход в Telegram не выполнен (вкладка «Подключения»)')
    items = jobs.make_items(targets, S['chats'])
    job = jobs.start(items, {'texts': d['texts'], 'media': d['media'], 'card_path': d['card_path'], 'thumb': d['thumb']}, TG)
    return {'job': job.snap()}


def api_job_cancel(q, b):
    if jobs.CURRENT:
        jobs.CURRENT.cancel = True
    return {'job': jobs.CURRENT.snap() if jobs.CURRENT else None}


def api_job_clear(q, b):
    if jobs.running():
        err('Публикация ещё идёт')
    jobs.CURRENT = None
    return {'ok': True}


# ---------- Telegram ----------
def api_tg_phone(q, b):
    try:
        TG.login_phone(b.get('phone', ''))
    except tgu.TgError as e:
        err(e.msg)
    return {'tg': TG.status()}


def api_tg_code(q, b):
    try:
        TG.login_code(b.get('code', ''))
    except tgu.TgError as e:
        err(e.msg)
    return {'tg': TG.status()}


def api_tg_password(q, b):
    try:
        TG.login_password(b.get('password', ''))
    except tgu.TgError as e:
        err(e.msg)
    return {'tg': TG.status()}


def api_tg_logout(q, b):
    TG.logout()
    return {'tg': TG.status()}


def api_tg_load(q, b):
    try:
        found = TG.load_chats()
    except tgu.TgError as e:
        err(e.msg)
    old = S['chats']
    new = {}
    for c in found:
        cid = c['id']
        prev = old.get(cid, {})
        c = dict(c)
        c['sel'] = bool(prev.get('sel')) and c['can_write']
        c['manual'] = bool(prev.get('manual'))
        c['cat'] = prev.get('cat') if (c['manual'] and cats.valid_id(prev.get('cat'))) else cats.guess(c['title'], c.get('username', ''))
        new[cid] = c
    S['chats'] = new
    cfg.save()
    total = len(new)
    can = sum(1 for c in new.values() if c['can_write'])
    return {'total': total, 'can_write': can, 'state': state()}


def api_tg_chat(q, b):
    c = S['chats'].get(str(b.get('id')))
    if not c:
        err('Этого чата нет в списке. Нажми «Загрузить чаты».')
    if 'sel' in b:
        if b['sel'] and not c.get('can_write'):
            err('В этот чат писать нельзя')
        c['sel'] = bool(b['sel'])
    if 'cat' in b:
        if not cats.valid_id(b['cat']):
            err('Нет такой категории')
        c['cat'], c['manual'] = b['cat'], True
    cfg.save()
    return {'ok': True}


def api_tg_bulk(q, b):
    sel = bool(b.get('sel'))
    n = 0
    for cid in b.get('ids', []):
        c = S['chats'].get(str(cid))
        if c and (c.get('can_write') or not sel):
            c['sel'] = sel
            n += 1
    cfg.save()
    return {'changed': n}


def api_tg_recat(q, b):
    n = 0
    for c in S['chats'].values():
        if b.get('all') or not c.get('manual'):
            g = cats.guess(c.get('title'), c.get('username', ''))
            if g != c.get('cat'):
                c['cat'] = g
                n += 1
            if b.get('all'):
                c['manual'] = False
    cfg.save()
    return {'changed': n}


def api_cats(q, b):
    op = b.get('op')
    try:
        if op == 'add':
            cats.add(b.get('name'))
        elif op == 'rename':
            cats.rename(b.get('id'), b.get('name'))
        elif op == 'delete':
            cats.delete(b.get('id'))
        else:
            err('Неизвестное действие')
    except ValueError as e:
        err(str(e))
    return {'cats': cats.categories(), 'chats': chat_list()}


# ---------- Threads ----------
def api_threads_link(q, b):
    if not pubs.threads_app_ready():
        err('Сначала впиши THREADS App ID и App Secret и нажми «Сохранить»')
    return {'url': pubs.threads_auth_link()}


def api_threads_code(q, b):
    try:
        who = pubs.threads_login_code(b.get('text', ''))
    except net.NetError as e:
        err(e.msg)
    return {'who': who}


def api_threads_token(q, b):
    try:
        who = pubs.threads_login_token(b.get('token', ''))
    except net.NetError as e:
        err(e.msg)
    return {'who': who}


def api_threads_logout(q, b):
    S['threads'] = {}
    DRAFT['threads'] = False
    cfg.save()
    return {'ok': True}


# ---------- YouTube ----------
def api_yt_secret(q, b):
    text = (b.get('text') or '').strip()
    try:
        j = json.loads(text)
        c = j.get('installed') or j.get('web') or {}
        assert c.get('client_id')
    except Exception:
        err('Это не похоже на файл client_secret.json. Открой файл Блокнотом, скопируй всё содержимое и вставь сюда.')
    with open(yt.SECRET_FILE, 'w', encoding='utf-8') as f:
        f.write(text)
    return {'ok': True}


def api_yt_login(q, b):
    if not yt.has_client():
        err('Сначала вставь содержимое client_secret.json и нажми «Сохранить файл»')
    if YT_LOGIN['state'] == 'wait':
        err('Вход уже идёт — смотри окно браузера')

    def go():
        YT_LOGIN.update(state='wait', url='', msg='')
        try:
            yt.login(on_url=lambda u: YT_LOGIN.update(url=u))
            YT_LOGIN.update(state='ok', msg='YouTube подключён')
        except net.NetError as e:
            YT_LOGIN.update(state='err', msg=e.msg)
        except Exception as e:
            traceback.print_exc()
            YT_LOGIN.update(state='err', msg=str(e))
    YT_LOGIN.update(state='wait', url='', msg='')
    threading.Thread(target=go, daemon=True).start()
    return {'ok': True}


def api_yt_logout(q, b):
    try:
        os.remove(yt.TOKEN_FILE)
    except OSError:
        pass
    DRAFT['yt'] = False
    YT_LOGIN.update(state='idle', url='', msg='')
    return {'ok': True}


# ---------- Claude, обновления, отчёт ----------
def api_claude_ask(q, b):
    text = (b.get('text') or '').strip()
    if not text:
        err('Напиши вопрос')
    hist = [m for m in (b.get('history') or []) if isinstance(m, dict) and m.get('role') in ('user', 'assistant') and isinstance(m.get('content'), str)]
    try:
        return {'answer': gen.ask(text, hist)}
    except net.NetError as e:
        err(e.msg)


def api_claude_test(q, b):
    try:
        a = gen.ask('Ответь одним коротким предложением: связь с программой «Пустошь Маркетинг» работает?')
    except net.NetError as e:
        err(e.msg)
    return {'answer': a}


def api_update_check(q, b):
    try:
        UPD['info'] = update.check()
        UPD['error'] = ''
    except net.NetError as e:
        UPD['error'] = e.msg
        err(e.msg)
    return {'update': UPD['info']}


def api_update_install(q, b):
    if jobs.running():
        err('Сейчас идёт публикация. Обнови после неё.')
    try:
        ver = update.install()
    except net.NetError as e:
        err(e.msg)
    threading.Timer(1.0, _restart).start()
    return {'ok': True, 'version': ver}


def _restart():
    try:
        TG.close()
    except Exception:
        pass
    try:
        os.remove(RUN_FILE)
    except OSError:
        pass
    update.restart()
    os._exit(0)


def mask(text):
    for k in cfg.SECRET_KEYS:
        v = env(k)
        if v and len(v) > 5:
            text = text.replace(v, '***')
    t = S.get('threads', {}).get('token')
    if t:
        text = text.replace(t, '***')
    return text


def api_report(q, b):
    ch = S['chats'].values()
    lines = ['Пустошь Маркетинг v%s' % version.VERSION, 'Система: %s, Python %s' % (platform.platform(), platform.python_version()),
             'Claude: %s | GPT-картинки: %s | картинки с надписью: %s | GitHub-хостинг: %s' % ('ключ есть' if gen.ai_ready() else 'нет ключа', 'ключ есть' if imggen.ready() else 'нет ключа', 'да' if card.available() else 'нет', 'да' if pubs.host_ready() else 'нет'),
             'Telegram: %s' % TG.status()['state'], 'Threads: %s' % pubs.threads_status(), 'YouTube: %s' % yt.status(),
             'Чатов: %d, можно писать: %d, выбрано: %d' % (len(S['chats']), sum(1 for c in ch if c.get('can_write')), len(selected_tg())),
             '--- журнал ---']
    try:
        with open(LOG_FILE, encoding='utf-8', errors='replace') as f:
            lines += f.read().splitlines()[-120:]
    except OSError:
        lines.append('(журнала пока нет)')
    return {'text': mask('\n'.join(lines))}


def api_quit(q, b):
    threading.Timer(0.5, _quit).start()
    return {'ok': True}


def _quit():
    try:
        TG.close()
    except Exception:
        pass
    try:
        os.remove(RUN_FILE)
    except OSError:
        pass
    os._exit(0)


ROUTES = {
    ('GET', '/api/state'): api_state, ('GET', '/api/ping'): api_ping, ('POST', '/api/settings'): api_settings,
    ('POST', '/api/draft'): api_draft, ('POST', '/api/media/meta'): api_media_meta, ('POST', '/api/media/clear'): api_media_clear,
    ('POST', '/api/generate'): api_generate, ('POST', '/api/extra/start'): api_extra_start, ('POST', '/api/extra/use'): api_extra_use,
    ('POST', '/api/extra/drop'): api_extra_drop, ('POST', '/api/publish'): api_publish, ('POST', '/api/job/cancel'): api_job_cancel,
    ('POST', '/api/job/clear'): api_job_clear,
    ('POST', '/api/tg/phone'): api_tg_phone, ('POST', '/api/tg/code'): api_tg_code, ('POST', '/api/tg/password'): api_tg_password,
    ('POST', '/api/tg/logout'): api_tg_logout, ('POST', '/api/tg/load'): api_tg_load, ('POST', '/api/tg/chat'): api_tg_chat,
    ('POST', '/api/tg/bulk'): api_tg_bulk, ('POST', '/api/tg/recat'): api_tg_recat, ('POST', '/api/cats'): api_cats,
    ('GET', '/api/threads/link'): api_threads_link, ('POST', '/api/threads/code'): api_threads_code,
    ('POST', '/api/threads/token'): api_threads_token, ('POST', '/api/threads/logout'): api_threads_logout,
    ('POST', '/api/yt/secret'): api_yt_secret, ('POST', '/api/yt/login'): api_yt_login, ('POST', '/api/yt/logout'): api_yt_logout,
    ('POST', '/api/claude/ask'): api_claude_ask, ('POST', '/api/claude/test'): api_claude_test,
    ('GET', '/api/update/check'): api_update_check, ('POST', '/api/update/install'): api_update_install,
    ('GET', '/api/report'): api_report, ('POST', '/api/quit'): api_quit,
}


# ======================================================================= HTTP
class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def _bytes(self, data, ctype, code=200, extra=None):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _host_ok(self):
        host = (self.headers.get('Host') or '').split(':')[0].lower()
        return host in ('127.0.0.1', 'localhost')

    def _token_ok(self, q):
        return secrets.compare_digest(self.headers.get('X-Token', '') or (q.get('t') or [''])[0], TOKEN)

    def handle_any(self, method):
        u = urllib.parse.urlsplit(self.path)
        q = urllib.parse.parse_qs(u.query)
        path = u.path
        try:
            if not self._host_ok():
                return self._json({'ok': False, 'error': 'forbidden'}, 403)
            if method == 'GET' and path == '/':
                with open(os.path.join(UI_DIR, 'index.html'), encoding='utf-8') as f:
                    html = f.read().replace('__TOKEN__', TOKEN).replace('__VERSION__', version.VERSION)
                return self._bytes(html.encode('utf-8'), 'text/html; charset=utf-8', extra={'Cache-Control': 'no-store'})
            if method == 'GET' and path == '/favicon.ico':
                return self._bytes(b'', 'image/x-icon', 204)
            if not self._token_ok(q):
                return self._json({'ok': False, 'error': 'Окно устарело — закрой его и открой программу заново (значок на рабочем столе).'}, 401)
            if path.startswith('/media/') and method == 'GET':
                return self.serve_media(path[7:])
            if path == '/api/upload' and method == 'PUT':
                return self._json(self.upload(q))
            fn = ROUTES.get((method, path))
            if not fn:
                return self._json({'ok': False, 'error': 'нет такой команды'}, 404)
            body = {}
            n = int(self.headers.get('Content-Length') or 0)
            if n:
                raw = self.rfile.read(n)
                try:
                    body = json.loads(raw.decode('utf-8'))
                except Exception:
                    body = {}
            res = fn(q, body if isinstance(body, dict) else {})
            res = dict(res)
            res.setdefault('ok', True)
            return self._json(res)
        except ApiError as e:
            return self._json({'ok': False, 'error': str(e)}, 400)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as e:
            traceback.print_exc()
            try:
                return self._json({'ok': False, 'error': 'Ошибка программы: %s' % e}, 500)
            except Exception:
                return

    def do_GET(self):
        self.handle_any('GET')

    def do_POST(self):
        self.handle_any('POST')

    def do_PUT(self):
        self.handle_any('PUT')

    # ---- загрузка файла из окна ----
    def upload(self, q):
        name = os.path.basename((q.get('name') or ['file'])[0])
        role = (q.get('role') or ['media'])[0]
        ext = os.path.splitext(name)[1].lower()
        n = int(self.headers.get('Content-Length') or 0)
        if n <= 0:
            err('Пустой файл')
        if role == 'thumb':
            ext = '.jpg'
        elif ext in IMG_EXT:
            kind = 'photo'
        elif ext in VIDEO_EXT:
            kind = 'video'
        else:
            for _ in range(0, n, 1 << 20):       # дочитать, чтобы соединение не зависло
                self.rfile.read(min(1 << 20, n))
            err('Нужна картинка (jpg, png, webp) или видео (mp4, mov, webm)')
        path = os.path.join(cfg.MEDIA, 'up_%d_%s%s' % (int(time.time()), secrets.token_hex(2), ext))
        left = n
        with open(path, 'wb') as f:
            while left > 0:
                chunk = self.rfile.read(min(1 << 20, left))
                if not chunk:
                    break
                f.write(chunk)
                left -= len(chunk)
        if left > 0:
            os.remove(path)
            err('Файл загрузился не до конца')
        if role == 'thumb':
            old = DRAFT.get('thumb')
            DRAFT['thumb'] = path
            if old and os.path.exists(old):
                os.remove(old)
            return {'ok': True}
        clear_media()
        DRAFT['media'] = {'kind': kind, 'path': path, 'name': name, 'w': None, 'h': None, 'dur': None}
        return {'ok': True, 'draft': public_draft()}

    def serve_media(self, name):
        name = os.path.basename(urllib.parse.unquote(name))
        p = os.path.join(cfg.MEDIA, name)
        if not os.path.isfile(p):
            return self._json({'ok': False, 'error': 'нет файла'}, 404)
        size = os.path.getsize(p)
        ctype = mimetypes.guess_type(p)[0] or 'application/octet-stream'
        rng = self.headers.get('Range')
        a, b = 0, size - 1
        code = 200
        if rng:
            m = re.match(r'bytes=(\d*)-(\d*)', rng)
            if m:
                if m.group(1):
                    a = int(m.group(1))
                    b = int(m.group(2)) if m.group(2) else size - 1
                elif m.group(2):
                    a = max(0, size - int(m.group(2)))
                b = min(b, size - 1)
                code = 206
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(b - a + 1))
        if code == 206:
            self.send_header('Content-Range', 'bytes %d-%d/%d' % (a, b, size))
        self.end_headers()
        with open(p, 'rb') as f:
            f.seek(a)
            left = b - a + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)


# ======================================================================= запуск
def read_run():
    try:
        with open(RUN_FILE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def ping_other(run):
    if not run:
        return False
    try:
        st, h, b = net.request('GET', 'http://127.0.0.1:%d/api/ping' % run['port'], {'X-Token': run['token']}, None, 3)
        return st == 200
    except Exception:
        return False


def find_window():
    cands = []
    pf = [os.environ.get('ProgramFiles(x86)'), os.environ.get('ProgramFiles'), os.environ.get('LOCALAPPDATA')]
    for base in pf:
        if base:
            cands.append(os.path.join(base, 'Microsoft', 'Edge', 'Application', 'msedge.exe'))
            cands.append(os.path.join(base, 'Google', 'Chrome', 'Application', 'chrome.exe'))
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def open_window(url):
    exe = find_window()
    if exe:
        try:
            subprocess.Popen([exe, '--app=' + url, '--window-size=1240,860'])
            return
        except Exception:
            pass
    try:
        webbrowser.open(url)
    except Exception:
        pass


def watchdog():
    while True:
        time.sleep(5)
        if IDLE_EXIT and time.time() - LAST_PING[0] > IDLE_EXIT and not jobs.running() and YT_LOGIN['state'] != 'wait':
            log('нет окна — закрываюсь')
            _quit()


def background():
    try:
        TG.start()
    except Exception as e:
        log('Telegram: тихий вход не удался:', e)
    try:
        UPD['info'] = update.check()
    except Exception as e:
        UPD['error'] = getattr(e, 'msg', str(e))
    last = 0
    while True:
        if time.time() - last > 6 * 3600:
            last = time.time()
            try:
                pubs.threads_refresh_if_needed()
            except Exception as e:
                log('Threads: не удалось продлить ключ:', e)
        time.sleep(60)


def bind(port_hint):
    for p in (port_hint, 0):
        try:
            return ThreadingHTTPServer(('127.0.0.1', p), H)
        except OSError:
            continue
    raise OSError('не удалось занять порт')


def main(argv=None):
    argv = argv or []
    no_window = '--no-window' in argv
    after_update = '--after-update' in argv
    run = read_run()
    if run and ping_other(run):
        if after_update:                                  # ждём, пока старая копия закроется
            for _ in range(40):
                time.sleep(0.5)
                if not ping_other(run):
                    break
        if ping_other(run):
            log('программа уже запущена — открываю окно')
            if not no_window:
                open_window('http://127.0.0.1:%d/?t=%s' % (run['port'], run['token']))
            return 0
    srv = bind(int(os.environ.get('MKT_PORT', '8765')))
    PORT[0] = srv.server_port
    with open(RUN_FILE, 'w', encoding='utf-8') as f:
        json.dump({'port': PORT[0], 'token': TOKEN, 'pid': os.getpid()}, f)
    log('Пустошь Маркетинг v%s, порт %d' % (version.VERSION, PORT[0]))
    threading.Thread(target=background, daemon=True).start()
    if IDLE_EXIT:
        threading.Thread(target=watchdog, daemon=True).start()
    if not no_window:
        open_window('http://127.0.0.1:%d/?t=%s' % (PORT[0], TOKEN))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0
