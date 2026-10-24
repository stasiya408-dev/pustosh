# -*- coding: utf-8 -*-
"""Публикация поста по площадкам в фоне, с прогрессом и безопасными паузами для Телеграма."""
import random, threading, time, traceback
import cfg, net, pubs, yt, tgu
from cfg import env, S

LOCK = threading.Lock()
CURRENT = None


def tg_limits():
    def num(k, d, lo, hi):
        try:
            v = float(env(k, str(d)))
        except ValueError:
            v = d
        return max(lo, min(hi, v))
    dmin = num('TG_DELAY_MIN', 40, 15, 600)
    dmax = max(dmin, num('TG_DELAY_MAX', 90, 15, 900))
    return dmin, dmax, int(num('TG_DAILY_LIMIT', 20, 1, 100))


def sent_today():
    t = S.get('tg_sent') or {}
    return t.get('n', 0) if t.get('date') == cfg.today() else 0


def add_sent():
    S['tg_sent'] = {'date': cfg.today(), 'n': sent_today() + 1}
    cfg.save()


class Job:
    def __init__(self, items):
        self.id = 'j%d' % int(time.time() * 1000)
        self.items = items            # [{key,label,status,msg,link}]
        self.state = 'running'        # running | done | cancelled
        self.note = ''
        self.cancel = False
        self.t0 = time.time()

    def snap(self):
        return {'id': self.id, 'state': self.state, 'note': self.note, 'items': [dict(i) for i in self.items],
                'elapsed': int(time.time() - self.t0)}


def running():
    return CURRENT is not None and CURRENT.state == 'running'


def make_items(targets, chats):
    """targets: {'yt':bool,'threads':bool,'tg':[chat ids]}"""
    items = []

    def add(key, label):
        items.append({'key': key, 'label': label, 'status': 'wait', 'msg': '', 'link': ''})
    if targets.get('yt'):
        add('yt', 'YouTube Shorts')
    if targets.get('threads'):
        add('threads', 'Threads')
    for cid in targets.get('tg', []):
        c = chats.get(cid)
        if c:
            add('tg:' + cid, 'Telegram: ' + c.get('title', cid))
    return items


def _sleep(job, seconds, why):
    end = time.time() + seconds
    while time.time() < end:
        if job.cancel:
            return False
        job.note = '%s: ещё %d сек' % (why, int(end - time.time()) + 1)
        time.sleep(0.5)
    job.note = ''
    return True


def start(items, draft, tg):
    """draft: {'texts','media','card_path','thumb'}. Запускает фоновый поток."""
    global CURRENT
    with LOCK:
        if running():
            raise ValueError('Публикация уже идёт')
        job = Job(items)
        CURRENT = job
    threading.Thread(target=_run, args=(job, draft, tg), daemon=True, name='publish').start()
    return job


def _pick_media(draft):
    m = draft.get('media')
    if m and m['kind'] == 'photo' and draft.get('card_path'):
        return {'kind': 'photo', 'path': draft['card_path'], 'w': None, 'h': None, 'dur': None}
    return m


def _run(job, draft, tg):
    texts, m = draft['texts'], _pick_media(draft)
    tg_stop = ''
    dmin, dmax, limit = tg_limits()
    first_tg = True
    try:
        for it in job.items:
            if job.cancel:
                break
            k = it['key']
            if k.startswith('tg:') and tg_stop:
                it['status'], it['msg'] = 'skip', tg_stop
                continue
            it['status'] = 'run'
            try:
                if k == 'yt':
                    v = draft.get('media')
                    if not v or v['kind'] != 'video':
                        raise net.NetError('для YouTube Shorts нужен видеоролик (сейчас его нет)')
                    warn = ''
                    if v.get('w') and v.get('h') and v['w'] > v['h']:
                        warn = 'ролик горизонтальный: YouTube покажет его как обычное видео, не как Short'
                    elif v.get('dur') and v['dur'] > 180:
                        warn = 'ролик длиннее 3 минут: это уже не Short'
                    it['link'] = yt.upload(v['path'], texts['youtube_title'], texts['youtube_desc'], env('YT_PRIVACY', 'public'))
                    it['status'], it['msg'] = 'ok', warn
                elif k == 'threads':
                    link, warn = pubs.threads_publish(texts['threads'], m['path'] if m else None, m['kind'] if m else None)
                    it['link'], it['status'], it['msg'] = link, 'ok', warn
                else:
                    cid = k[3:]
                    c = cfg.S['chats'].get(cid, {})
                    if sent_today() >= limit:
                        tg_stop = 'дневной лимит отправки (%d) исчерпан, продолжишь завтра' % limit
                        it['status'], it['msg'] = 'skip', tg_stop
                        continue
                    if not first_tg:
                        if not _sleep(job, random_pause(dmin, dmax), 'Пауза перед следующим чатом'):
                            break
                    first_tg = False
                    it['status'] = 'run'
                    mm, note = m, ''
                    if m and ((m['kind'] == 'photo' and c.get('no_photo')) or (m['kind'] == 'video' and c.get('no_video'))):
                        mm, note = None, 'отправлен только текст: в чате нельзя слать картинки/видео'
                    try:
                        link = tg.send(cid, texts['telegram'], mm, c.get('username', ''))
                    except tgu.TgError as e:
                        if e.kind == 'nomedia' and mm:
                            link = tg.send(cid, texts['telegram'], None, c.get('username', ''))
                            note = 'отправлен только текст: ' + e.msg
                        else:
                            raise
                    add_sent()
                    it['link'], it['status'], it['msg'] = link, 'ok', note
            except tgu.TgError as e:
                it['status'], it['msg'] = 'err', e.msg
                if e.kind in ('flood', 'peerflood'):
                    tg_stop = 'остановлено: ' + e.msg
                elif e.kind == 'auth':
                    tg_stop = 'остановлено: ' + e.msg
            except net.NetError as e:
                it['status'], it['msg'] = 'err', e.msg
            except Exception as e:
                traceback.print_exc()
                it['status'], it['msg'] = 'err', 'ошибка программы: %s' % e
        if job.cancel:
            for it in job.items:
                if it['status'] in ('wait', 'run'):
                    it['status'], it['msg'] = 'skip', 'отменено'
    finally:
        job.note = ''
        job.state = 'cancelled' if job.cancel else 'done'
        try:
            S['last_targets'] = [i['key'] for i in job.items if i['status'] == 'ok']
            cfg.save()
        except Exception:
            pass


def random_pause(dmin, dmax):
    return random.uniform(dmin, dmax)
