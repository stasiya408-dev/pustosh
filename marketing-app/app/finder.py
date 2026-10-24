# -*- coding: utf-8 -*-
"""Поиск НОВЫХ групп по всему Телеграму (по темам) и база найденных чатов.
Ищем только публичные группы с открытым чатом, где тебя ещё нет. Вступать в них программа не пытается."""
import csv, io, itertools, random, sys, threading, time, traceback
import cfg, cats, tgu
from cfg import S

LOCK = threading.RLock()
CANCEL = [False]
CANCEL_ON = [False]
PAUSE = (300.0, 900.0)     # секунд между запросами: от 5 до 15 минут, случайно (Телеграм жёстко ограничивает частый глобальный поиск)
MAX_QUERIES = 60           # за один запуск (при паузе 5–15 минут это около 10 часов)
ONLINE_PAUSE = (2.5, 5.0)  # секунд между проверками онлайна групп (обычный запрос, как при открытии группы в приложении)
MAX_ONLINE_QUERY = 40      # онлайн проверяется сразу для новых групп после каждого запроса, но не больше стольки за раз
MAX_ONLINE_JOB = 100       # кнопка «Обновить онлайн»: не больше стольки групп за раз
ST = {'state': 'idle', 'msg': '', 'warn': '', 'cats': [], 'done': 0, 'total': 0, 'new': 0, 'cur': '', 'errors': 0, 'started': 0, 'truncated': False,
      'wait_until': 0, 'next': '', 'raw': 0, 'kept': 0}
ON = {'state': 'idle', 'msg': '', 'warn': '', 'done': 0, 'total': 0, 'started': 0}


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


def online_running():
    return ON['state'] == 'running'


def busy():
    return running() or online_running()


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
                  started=cfg.now(), truncated=trunc, wait_until=0, next='', raw=0, kept=0)
    threading.Thread(target=_run, args=(tg, qs), daemon=True, name='find').start()
    return view()


def cancel():
    if running():
        CANCEL[0] = True


def _sleep(sec, stop=None):
    stop = stop or (lambda: CANCEL[0])
    end = time.time() + sec
    while time.time() < end:
        if stop():
            return False
        time.sleep(0.05 if sec < 2 else 0.25)
    return True


def _merge(found, cid, query, selected):
    """Кладёт найденное в базу. Возвращает список id новых чатов."""
    n = []
    b, own = base(), S['chats']
    for f in found:
        i = f['id']
        if i in own:                       # ты уже в этой группе
            continue
        old = b.get(i)
        if old:                            # уже знаем: обновим число участников и название
            for k in ('title', 'username', 'members', 'join_request', 'slow', 'forum', 'cid', 'hash'):
                if f.get(k) is not None:
                    old[k] = f[k]
            continue
        g = cats.guess(f['title'], f.get('username', ''))
        c = g if (g in selected and g != cats.OTHER) else cid       # тема по названию, если она среди выбранных
        item = {k: f.get(k) for k in ('id', 'title', 'username', 'kind', 'members', 'join_request', 'slow', 'forum', 'cid', 'hash')}
        item.update(cat=c, saved=False, found=cfg.now(), q=query, manual=False, online=None, online_at=0, about='', gone=False)
        b[i] = item
        n.append(i)
    return n


def _fetch_online(tg, ids, stop, step=None):
    """Спрашивает у Телеграма, сколько людей сейчас онлайн (и описание) у каждой группы, по очереди с паузами. Возвращает (проверено, предупреждение)."""
    done, warn = 0, ''
    for i, gid in enumerate(ids):
        if stop():
            break
        if i and not _sleep(random_pause(*ONLINE_PAUSE), stop):
            break
        x = base().get(gid)
        if not x:
            continue
        if step:
            step(i, len(ids))
        try:
            d = tg.full(gid, x.get('cid'), x.get('hash'))
        except tgu.TgError as e:
            if e.kind in ('flood', 'peerflood'):
                warn = 'Телеграм попросил подождать при проверке онлайна (%s). Онлайн можно обновить позже кнопкой «🟢 Обновить онлайн».' % e.msg
                break
            if e.kind == 'auth':
                warn = e.msg
                break
            if e.kind == 'forbidden':                         # группу закрыли или удалили
                x.update(gone=True, online=None, online_at=cfg.now())
            done += 1
            continue
        x['online'] = d.get('online')
        x['online_at'] = cfg.now()
        x['gone'] = False
        if d.get('members') is not None:
            x['members'] = d['members']
        if d.get('about') is not None:
            x['about'] = d['about']
        done += 1
    return done, warn


def start_online(tg, ids):
    """Обновляет онлайн у выбранных групп (не больше MAX_ONLINE_JOB за раз)."""
    with LOCK:
        if online_running():
            raise ValueError('Онлайн уже обновляется')
        b = base()
        ids = [i for i in dict.fromkeys(ids) if i in b and i not in S['chats']][:MAX_ONLINE_JOB]
        if not ids:
            raise ValueError('Нет групп для проверки')
        CANCEL_ON[0] = False
        ON.update(state='running', msg='', warn='', done=0, total=len(ids), started=cfg.now())
    threading.Thread(target=_run_online, args=(tg, ids), daemon=True, name='online').start()
    return view()


def cancel_online():
    if online_running():
        CANCEL_ON[0] = True


def _run_online(tg, ids):
    stop_msg, warn = '', ''
    _keep_awake(True)
    try:
        def step(i, n):
            ON['done'] = i
        done, warn = _fetch_online(tg, ids, lambda: CANCEL_ON[0], step)
        ON['done'] = ON['total'] if not CANCEL_ON[0] and not warn else ON['done']
    except Exception as e:
        traceback.print_exc()
        stop_msg = 'Ошибка программы: %s' % e
    finally:
        with LOCK:
            if stop_msg:
                ON.update(state='error', msg=stop_msg)
            else:
                ON.update(state='cancelled' if CANCEL_ON[0] else 'done', warn=warn)
            _keep_awake(False)
            try:
                cfg.save()
            except Exception:
                pass


def _run(tg, qs):
    selected = {c for c, _ in qs}
    bad = 0
    stop_msg, warn = '', ''
    names = {c['id']: c['name'] for c in cats.categories()}
    online_off, online_warn = False, ''
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
                raw = getattr(tg, 'last_raw', None)
                with LOCK:
                    ST['raw'] += raw if isinstance(raw, int) else len(found)
                    ST['kept'] += len(found)
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
                fresh = _merge(found, cid, q, selected)
                ST['new'] += len(fresh)
                ST['done'] = i + 1
                cfg.save()
            if fresh and not online_off and not CANCEL[0]:        # сразу узнаём онлайн и описание новых групп
                ids = fresh[:MAX_ONLINE_QUERY]
                _, w = _fetch_online(tg, ids, lambda: CANCEL[0],
                                     lambda k, n: ST.update(cur='проверяю онлайн новых групп: %d из %d' % (k + 1, n)))
                ST['cur'] = label
                with LOCK:
                    cfg.save()
                if w:
                    online_off, online_warn = True, w
    except Exception as e:
        traceback.print_exc()
        stop_msg = 'Ошибка программы: %s' % e
    finally:
        with LOCK:
            if stop_msg:
                ST.update(state='error', msg=stop_msg)
            else:
                ST.update(state='cancelled' if CANCEL[0] else 'done', warn=warn or online_warn)
            ST.update(cur='', wait_until=0, next='')
            _keep_awake(False)
            try:
                cfg.save()
            except Exception:
                pass


# ---------- база ----------
def _live():
    with LOCK:
        own = S['chats']
        return [x for k, x in list(base().items()) if k not in own]


def view():
    with LOCK:
        v = _live()
        d = dict(ST)
        d['total_base'] = len(v)
        d['unsaved'] = sum(1 for x in v if not x.get('saved'))
        d['queries'] = {c['id']: len(cats.queries(c['id'])) for c in cats.categories()}
        d['pause'] = list(PAUSE)
        d['max_queries'] = MAX_QUERIES
        d['online_job'] = dict(ON)
        d['online_known'] = sum(1 for x in v if x.get('online_at') and not x.get('gone'))
        d['max_online'] = MAX_ONLINE_JOB
        return d


def _online_key(x):
    o = x.get('online')
    return (0 if o is not None else 1, -(o or 0), -(x.get('members') or 0))


def listing(cat='', q='', minm=0, sort='online', limit=500):
    """Список базы для окна: с фильтрами и сортировкой (online | members | new). Число чатов по темам считается без выбора темы."""
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
    if sort == 'new':
        out.sort(key=lambda x: (-(x.get('found') or 0), -(x.get('members') or 0)))
    elif sort == 'members':
        out.sort(key=lambda x: -(x.get('members') or 0))
    else:
        out.sort(key=_online_key)
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
    with LOCK:
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
    w.writerow(['Название', 'Ссылка', 'Участников', 'Онлайн', 'Тема', 'Вступление', 'В базе сохранён', 'Описание'])
    for x in sorted(_live(), key=lambda x: (names.get(x['cat'], ''), -(x.get('members') or 0))):
        w.writerow([x.get('title', ''), 'https://t.me/' + (x.get('username') or ''), x.get('members') or '', x['online'] if x.get('online') is not None else '',
                    names.get(x['cat'], 'Другое'), 'по заявке' if x.get('join_request') else 'свободное', 'да' if x.get('saved') else 'нет',
                    (x.get('about') or '').replace('\n', ' ')])
    return bio.getvalue()
