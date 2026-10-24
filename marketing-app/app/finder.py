# -*- coding: utf-8 -*-
"""Поиск НОВЫХ групп Telegram в интернете (по темам) и база найденных чатов.
Аккаунт Telegram при поиске НЕ используется и ничего в Telegram не отправляется: слова ищутся в поисковиках,
а каждая найденная группа проверяется по публичной странице t.me/имя (название, участники, онлайн, описание).
Вступать в группы программа не пытается."""
import csv, io, itertools, random, sys, threading, time, traceback
import cfg, cats, net, websearch
from cfg import S

LOCK = threading.RLock()
CANCEL = [False]
CANCEL_ON = [False]
WEB_PAUSE = (1.2, 2.6)       # секунд между запросами к одному поисковику
VERIFY_PAUSE = (0.4, 0.9)    # секунд между проверками страниц t.me (проверяют два «потока» одновременно)
ONLINE_PAUSE = (0.5, 1.1)    # секунд между проверками онлайна кнопкой «Обновить онлайн»
MAX_QUERIES = 60             # слов за один запуск (по каждому слову идут запросы во все поисковики)
MAX_ONLINE_JOB = 200         # кнопка «Обновить онлайн»: не больше стольки групп за раз
SEEN_TTL = 14 * 86400        # каналы, люди и боты, которых уже проверили, две недели не проверяем снова
DROP_TTL = 90 * 86400        # группы, которые ты убрал из базы крестиком, три месяца не показываем снова
SEEN_MAX = 6000
ST = {'state': 'idle', 'msg': '', 'warn': '', 'cats': [], 'done': 0, 'total': 0, 'new': 0, 'cur': '', 'errors': 0, 'started': 0, 'truncated': False,
      'raw': 0, 'kept': 0, 'checked': 0, 'engines': []}
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


def start(cat_ids):
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
                  started=cfg.now(), truncated=trunc, raw=0, kept=0, checked=0, engines=[])
    threading.Thread(target=_run, args=(qs,), daemon=True, name='find').start()
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


# ---------- что уже знаем ----------
def seen():
    return S.setdefault('webseen', {})


def _remember(low, kind):
    d = seen()
    d[low] = [cfg.now(), kind]
    if len(d) > SEEN_MAX:
        for k in sorted(d, key=lambda k: d[k][0])[:500]:
            del d[k]


def _skip(low):
    v = seen().get(low)
    if not v:
        return False
    return cfg.now() - v[0] < (DROP_TTL if v[1] == 'dropped' else SEEN_TTL)


def _known():
    """(имена моих чатов, {имя группы в базе: ключ})."""
    own = {(c.get('username') or '').lower() for c in S['chats'].values() if c.get('username')}
    inbase = {(x.get('username') or '').lower(): k for k, x in base().items() if x.get('username')}
    return own, inbase


def _is_new(low):
    own, inbase = _known()
    return low not in own and low not in inbase and not _skip(low)


def _merge(groups, cid, query, selected):
    """Кладёт найденные группы в базу. groups: [(имя, описание страницы t.me, поисковик)]. Возвращает ключи новых."""
    n = []
    b = base()
    own, inbase = _known()
    for name, info, src in groups:
        low = name.lower()
        if low in own or low in inbase:
            continue
        k = 'w_' + low
        g = cats.guess(info.get('title', ''), name)
        c = g if (g in selected and g != cats.OTHER) else cid       # тема по названию, если она среди выбранных
        b[k] = {'id': k, 'title': info.get('title') or name, 'username': name, 'kind': 'group', 'members': info.get('members'),
                'join_request': bool(info.get('join_request')), 'slow': False, 'forum': False, 'cid': None, 'hash': None,
                'cat': c, 'saved': False, 'found': cfg.now(), 'q': query, 'manual': False,
                'online': info.get('online'), 'online_at': cfg.now(), 'about': info.get('about') or '', 'gone': False, 'src': src}
        inbase[low] = k
        n.append(k)
    return n


def _run(qs):
    selected = {c for c, _ in qs}
    stop_msg, warn = '', ''
    names = {c['id']: c['name'] for c in cats.categories()}
    engines = websearch.make_engines()
    ST['engines'] = [e.report() for e in engines]
    dead = 0
    _keep_awake(True)
    try:
        for i, (cid, q) in enumerate(qs):
            if CANCEL[0]:
                break
            label = '%s: «%s»' % (names.get(cid, cid), q)
            ST['cur'] = 'ищу в интернете · ' + label
            cands = websearch.search_word(q, engines, lambda: random_pause(*WEB_PAUSE), lambda: CANCEL[0])
            ST['engines'] = [e.report() for e in engines]
            if CANCEL[0]:
                break
            with LOCK:
                ST['raw'] += len(cands)
            todo = [v[0] for low, v in cands.items() if _is_new(low)]
            groups, blocked, neterr = [], False, ''
            if todo:
                def prog(k, n, label=label):
                    ST['cur'] = 'проверяю страницы t.me: %d из %d · %s' % (k, n, label)
                infos, blocked, neterr = websearch.verify_many(todo, lambda: CANCEL[0], lambda: random_pause(*VERIFY_PAUSE), prog)
                dead = dead + 1 if (not infos and not blocked) else 0
                with LOCK:
                    ST['checked'] += len(infos)
                    for n in todo:
                        info = infos.get(n)
                        if not info:
                            continue
                        if info['kind'] == 'group' and (info['members'] or 0) >= websearch.MIN_MEMBERS:
                            groups.append((n, info, cands[n.lower()][1]))
                        else:
                            _remember(n.lower(), info['kind'])
            with LOCK:
                fresh = _merge(groups, cid, q, selected)
                ST['kept'] += len(groups)
                ST['new'] += len(fresh)
                ST['done'] = i + 1
                cfg.save()
            if blocked:
                warn = 't.me просит подождать (слишком частые запросы с этого компьютера). Найденное сохранено, повтори поиск через несколько минут.'
                break
            if neterr or dead >= 3:
                stop_msg = 'Поиск остановлен: страницы t.me не открываются (%s). Проверь интернет или VPN и повтори.' % (neterr or 'нет ответа')
                break
            if all(e.off for e in engines):
                why = '; '.join('%s: %s' % (e.name, e.err or 'не отвечает') for e in engines)
                if ST['raw'] == 0:
                    stop_msg = 'Не получилось найти ничего: поисковики не отвечают (%s). Проверь интернет или повтори позже.' % why
                else:
                    warn = 'Поисковики перестали отвечать (%s), поэтому поиск остановлен. Найденное сохранено.' % why
                break
    except Exception as e:
        traceback.print_exc()
        stop_msg = 'Ошибка программы: %s' % e
    finally:
        with LOCK:
            if stop_msg:
                ST.update(state='error', msg=stop_msg)
            else:
                ST.update(state='cancelled' if CANCEL[0] else 'done', warn=warn)
            ST.update(cur='', engines=[e.report() for e in engines])
            _keep_awake(False)
            try:
                cfg.save()
            except Exception:
                pass


# ---------- онлайн ----------
def _check_retry(username, stop):
    """Страница t.me/имя; если просят подождать — ждём один раз и пробуем снова."""
    try:
        return websearch.check(username)
    except websearch.Blocked as b:
        if not _sleep(min(60, max(websearch.BLOCK_MIN, b.wait)), stop):
            return None
        return websearch.check(username)


def _fetch_online(ids, stop, step=None):
    """Открывает страницу t.me каждой группы и берёт оттуда онлайн, участников и описание. Возвращает (проверено, предупреждение)."""
    done, warn, bad = 0, '', 0
    for i, gid in enumerate(ids):
        if stop():
            break
        if i and not _sleep(random_pause(*ONLINE_PAUSE), stop):
            break
        x = base().get(gid)
        if not x or not x.get('username'):
            continue
        if step:
            step(i, len(ids))
        try:
            d = _check_retry(x['username'], stop)
        except websearch.Blocked:
            warn = 't.me просит подождать (слишком частые запросы). Онлайн можно обновить позже кнопкой «🟢 Обновить онлайн».'
            break
        except net.NetError as e:
            bad += 1
            if bad >= 3:
                warn = 'Нет связи с интернетом: %s' % e.msg
                break
            continue
        if d is None:
            break
        bad = 0
        if d['kind'] != 'group':                              # страницы нет, группу закрыли, удалили или она стала каналом
            x.update(gone=True, online=None, online_at=cfg.now())
            done += 1
            continue
        x['online'] = d.get('online')
        x['online_at'] = cfg.now()
        x['gone'] = False
        if d.get('members') is not None:
            x['members'] = d['members']
        if d.get('about'):
            x['about'] = d['about']
        done += 1
    return done, warn


def start_online(ids):
    """Обновляет онлайн у выбранных групп (не больше MAX_ONLINE_JOB за раз)."""
    with LOCK:
        if online_running():
            raise ValueError('Онлайн уже обновляется')
        b = base()
        ids = [i for i in dict.fromkeys(ids) if i in b and i not in S['chats'] and b[i].get('username')][:MAX_ONLINE_JOB]
        if not ids:
            raise ValueError('Нет групп для проверки')
        CANCEL_ON[0] = False
        ON.update(state='running', msg='', warn='', done=0, total=len(ids), started=cfg.now())
    threading.Thread(target=_run_online, args=(ids,), daemon=True, name='online').start()
    return view()


def cancel_online():
    if online_running():
        CANCEL_ON[0] = True


def _run_online(ids):
    stop_msg, warn = '', ''
    _keep_awake(True)
    try:
        def step(i, n):
            ON['done'] = i
        done, warn = _fetch_online(ids, lambda: CANCEL_ON[0], step)
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


# ---------- база ----------
def _live():
    with LOCK:
        own = S['chats']
        own_names = {(c.get('username') or '').lower() for c in own.values() if c.get('username')}
        return [x for k, x in list(base().items()) if k not in own and (x.get('username') or '\0').lower() not in own_names]


def view():
    with LOCK:
        v = _live()
        d = dict(ST)
        d['total_base'] = len(v)
        d['unsaved'] = sum(1 for x in v if not x.get('saved'))
        d['queries'] = {c['id']: len(cats.queries(c['id'])) for c in cats.categories()}
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
                u = (b[i].get('username') or '').lower()
                if u:
                    _remember(u, 'dropped')           # убрал крестиком: этот чат больше не предлагаем
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
