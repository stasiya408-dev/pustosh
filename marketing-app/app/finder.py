# -*- coding: utf-8 -*-
"""Поиск НОВЫХ групп по всему Телеграму (по темам) и база найденных чатов.
Ищем только публичные группы с открытым чатом, где тебя ещё нет. Вступать в них программа не пытается."""
import csv, io, itertools, random, sys, threading, time, traceback
import cfg, cats, tgu
from cfg import S

LOCK = threading.RLock()
CANCEL = [False]
PAUSE = (300.0, 900.0)     # секунд между запросами: от 5 до 15 минут, случайно (Телеграм жёстко ограничивает частый глобальный поиск)
MAX_QUERIES = 60           # за один запуск (при паузе 5–15 минут это около 10 часов)
ST = {'state': 'idle', 'msg': '', 'warn': '', 'cats': [], 'done': 0, 'total': 0, 'new': 0, 'cur': '', 'errors': 0, 'started': 0, 'truncated': False,
      'wait_until': 0, 'next': ''}


def random_pause(a, b):
    return random.uniform(a, b)


def _keep_awake(on):
    """Пока идёт долгий поиск, Windows не должен уходить в сон (экран может гаснуть). Вне Windows ничего не делает."""
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | (0x00000001 if on else 0))      # ES_CONTINUOUS [| ES_SYSTEM_REQUIRED]
    except Exception:
        pass


def base():
    return S.setdefault('base', {})


def running():
    return ST['state'] == 'running'


def plan(cat_ids):
    """[(id темы, слово)] — темы по очереди, чтобы лимит на запуск делился между ними поровну."""
    per = []
    for cid in cat_ids:
        if cats.valid_id(cid):
            per.append([(cid, q) for q in cats.queries(cid)])
    mixed = [x for x in itertools.chain.from_iterable(itertools.zip_longest(*per)) if x]
    return mixed


def start(tg, cat_ids):
    with LOCK:
        if running():
            raise ValueError('Поиск уже идёт')
        qs = plan(list(dict.fromkeys(cat_ids)))
        if not qs:
            raise ValueError('Поставь галочки у тем слева. Для «Другое» поиска нет.')
        trunc = len(qs) > MAX_QUERIES
        qs = qs[:MAX_QUERIES]
        CANCEL[0] = False
        ST.update(state='running', msg='', warn='', cats=sorted({c for c, _ in qs}), done=0, total=len(qs), new=0, cur='', errors=0,
                  started=cfg.now(), truncated=trunc, wait_until=0, next='')
    threading.Thread(target=_run, args=(tg, qs), daemon=True, name='find').start()
    return view()


def cancel():
    if running():
        CANCEL[0] = True


def _sleep(sec):
    end = time.time() + sec
    while time.time() < end:
        if CANCEL[0]:
            return False
        time.sleep(0.05 if sec < 2 else 0.25)
    return True


def _merge(found, cid, query, selected):
    """Кладёт найденное в базу. Возвращает число новых чатов."""
    n = 0
    b, own = base(), S['chats']
    for f in found:
        i = f['id']
        if i in own:                       # ты уже в этой группе
            continue
        old = b.get(i)
        if old:                            # уже знаем: обновим число участников и название
            for k in ('title', 'username', 'members', 'join_request', 'slow', 'forum'):
                if f.get(k) is not None:
                    old[k] = f[k]
            continue
        g = cats.guess(f['title'], f.get('username', ''))
        c = g if (g in selected and g != cats.OTHER) else cid       # тема по названию, если она среди выбранных
        item = {k: f.get(k) for k in ('id', 'title', 'username', 'kind', 'members', 'join_request', 'slow', 'forum')}
        item.update(cat=c, saved=False, found=cfg.now(), q=query, manual=False)
        b[i] = item
        n += 1
    return n


def _run(tg, qs):
    selected = {c for c, _ in qs}
    bad = 0
    stop_msg, warn = '', ''
    names = {c['id']: c['name'] for c in cats.categories()}
    _keep_awake(True)
    try:
        for i, (cid, q) in enumerate(qs):
            if CANCEL[0]:
                break
            label = '%s: «%s»' % (names.get(cid, cid), q)
            if i:
                pause = random_pause(*PAUSE)
                ST.update(wait_until=time.time() + pause, next=label)
                ok = _sleep(pause)
                ST.update(wait_until=0, next='')
                if not ok:
                    break
            ST['cur'] = label
            try:
                found = tg.search(q)
                bad = 0
            except tgu.TgError as e:
                if e.kind in ('flood', 'peerflood'):
                    warn = '%s. Найденное сохранено — продолжи позже.' % e.msg
                    break
                if e.kind == 'auth':
                    stop_msg = e.msg
                    break
                bad += 1
                ST['errors'] += 1
                if bad >= 3:
                    stop_msg = 'Поиск остановлен: три запроса подряд не прошли. Последняя ошибка: ' + e.msg
                    break
                found = []
            with LOCK:
                ST['new'] += _merge(found, cid, q, selected)
                ST['done'] = i + 1
                cfg.save()
    except Exception as e:
        traceback.print_exc()
        stop_msg = 'Ошибка программы: %s' % e
    finally:
        with LOCK:
            if stop_msg:
                ST.update(state='error', msg=stop_msg)
            else:
                ST.update(state='cancelled' if CANCEL[0] else 'done', warn=warn)
            ST.update(cur='', wait_until=0, next='')
            _keep_awake(False)
            try:
                cfg.save()
            except Exception:
                pass


# ---------- база ----------
def _live():
    own = S['chats']
    return [x for k, x in base().items() if k not in own]


def view():
    with LOCK:
        v = _live()
        d = dict(ST)
        d['total_base'] = len(v)
        d['unsaved'] = sum(1 for x in v if not x.get('saved'))
        d['queries'] = {c['id']: len(cats.queries(c['id'])) for c in cats.categories()}
        d['pause'] = list(PAUSE)
        d['max_queries'] = MAX_QUERIES
        return d


def listing(cat='', q='', minm=0, limit=500):
    """Список базы для окна: с фильтрами. Число чатов по темам считается без выбора темы."""
    q = (q or '').strip().lower()
    out, counts = [], {}
    for x in _live():
        if (x.get('members') or 0) < minm:
            continue
        if q and q not in ('%s %s' % (x.get('title', ''), x.get('username', ''))).lower():
            continue
        counts[x['cat']] = counts.get(x['cat'], 0) + 1
        if not cat or cat == 'all' or x['cat'] == cat:
            out.append(x)
    out.sort(key=lambda x: -(x.get('members') or 0))
    return {'items': out[:limit], 'counts': counts, 'shown': min(len(out), limit), 'matched': len(out)}


def save_all():
    n = 0
    for x in _live():
        if not x.get('saved'):
            x['saved'] = True
            n += 1
    cfg.save()
    return n, len(_live())


def drop(ids=None, unsaved=False):
    b = base()
    n = 0
    if unsaved:
        for k in [k for k, x in b.items() if not x.get('saved')]:
            del b[k]
            n += 1
    for i in ids or []:
        if i in b:
            del b[i]
            n += 1
    cfg.save()
    return n


def set_cat(cid, cat):
    x = base().get(cid)
    if not x:
        raise ValueError('Этого чата нет в базе')
    if not cats.valid_id(cat):
        raise ValueError('Нет такой категории')
    x['cat'], x['manual'] = cat, True
    cfg.save()


def export_csv():
    names = {c['id']: c['name'] for c in cats.categories()}
    bio = io.StringIO()
    w = csv.writer(bio, delimiter=';')
    w.writerow(['Название', 'Ссылка', 'Участников', 'Тема', 'Вступление', 'В базе сохранён'])
    for x in sorted(_live(), key=lambda x: (names.get(x['cat'], ''), -(x.get('members') or 0))):
        w.writerow([x.get('title', ''), 'https://t.me/' + (x.get('username') or ''), x.get('members') or '', names.get(x['cat'], 'Другое'),
                    'по заявке' if x.get('join_request') else 'свободное', 'да' if x.get('saved') else 'нет'])
    return bio.getvalue()
