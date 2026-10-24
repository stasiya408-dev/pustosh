# -*- coding: utf-8 -*-
"""Автообновление программы: проверка новой версии и установка (скачивается небольшой архив с кодом)."""
import hashlib, json, os, re, shutil, subprocess, sys, zipfile
import cfg, net, version
from cfg import env

URL = env('UPDATE_URL', 'https://raw.githubusercontent.com/stasiya408-dev/pustosh/mkt-build').rstrip('/')
UPD_DIR = os.path.join(cfg.BASE, 'updates')
SETUP_NAME = 'PustoshMarketing-Setup.exe'


def vtuple(v):
    return tuple(int(x) for x in re.findall(r'\d+', str(v))[:4]) or (0,)


def bundled_deps():
    """Метка набора библиотек, зашитых в установленную программу (ставит launcher)."""
    return os.environ.get('MKT_BASE_DEPS', '')


def check():
    st, d = net.get_json('%s/latest.json?t=%d' % (URL, cfg.now()), timeout=20)
    if st != 200 or not d.get('version'):
        raise net.NetError('Не удалось проверить обновления (ответ %s). Попробуй позже.' % st, st)
    newer = vtuple(d['version']) > vtuple(version.VERSION)
    need_full = bool(newer and d.get('deps_hash') and bundled_deps() and d['deps_hash'] != bundled_deps())
    return {'current': version.VERSION, 'latest': d['version'], 'newer': newer, 'notes': d.get('notes', ''),
            'need_installer': need_full, 'installer_url': '%s/%s' % (URL, SETUP_NAME)}


def install():
    """Скачивает и распаковывает новую версию кода. Возвращает номер версии."""
    st, d = net.get_json('%s/latest.json?t=%d' % (URL, cfg.now()), timeout=20)
    if st != 200 or not d.get('zip'):
        raise net.NetError('Не удалось получить данные об обновлении (ответ %s)' % st, st)
    if vtuple(d['version']) <= vtuple(version.VERSION):
        raise net.NetError('У тебя уже последняя версия')
    if d.get('deps_hash') and bundled_deps() and d['deps_hash'] != bundled_deps():
        raise net.NetError('Это обновление требует новой установки: скачай свежий установщик')
    st, h, b = net.request('GET', '%s/%s' % (URL, d['zip']), None, None, 180)
    if st != 200 or not b:
        raise net.NetError('Не удалось скачать обновление (ответ %s)' % st, st)
    if d.get('sha256') and hashlib.sha256(b).hexdigest() != d['sha256']:
        raise net.NetError('Файл обновления повреждён при скачивании. Попробуй ещё раз.')
    ver = str(d['version'])
    target = os.path.join(UPD_DIR, ver)
    tmp = target + '.tmp'
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    zpath = os.path.join(UPD_DIR, ver + '.zip')
    with open(zpath, 'wb') as f:
        f.write(b)
    with zipfile.ZipFile(zpath) as z:
        for n in z.namelist():
            if n.startswith('/') or '..' in n.replace('\\', '/').split('/'):
                raise net.NetError('В архиве обновления неправильные пути')
        z.extractall(tmp)
    if not os.path.exists(os.path.join(tmp, 'version.py')):
        raise net.NetError('В архиве обновления нет программы')
    shutil.rmtree(target, ignore_errors=True)
    os.replace(tmp, target)
    with open(os.path.join(target, '.ok'), 'w') as f:
        f.write(ver)
    os.remove(zpath)
    # оставляем две последние версии
    olds = sorted([x for x in os.listdir(UPD_DIR) if os.path.isdir(os.path.join(UPD_DIR, x))], key=vtuple)
    for x in olds[:-2]:
        shutil.rmtree(os.path.join(UPD_DIR, x), ignore_errors=True)
    return ver


def newest_dir():
    """(версия, папка) самой новой готовой версии из обновлений или None."""
    best = None
    if os.path.isdir(UPD_DIR):
        for x in os.listdir(UPD_DIR):
            p = os.path.join(UPD_DIR, x)
            if os.path.exists(os.path.join(p, '.ok')) and os.path.exists(os.path.join(p, 'version.py')):
                if best is None or vtuple(x) > vtuple(best[0]):
                    best = (x, p)
    return best


def restart():
    """Запускает новую копию программы и закрывает эту."""
    if getattr(sys, 'frozen', False):
        args = [sys.executable, '--after-update']
    else:
        args = [sys.executable, os.path.join(os.path.dirname(cfg.CODE), 'launcher.py'), '--after-update']
    flags = 0
    if os.name == 'nt':
        flags = 0x00000008 | 0x00000200       # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(args, creationflags=flags, close_fds=True)
