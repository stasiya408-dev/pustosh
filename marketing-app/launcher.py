# -*- coding: utf-8 -*-
"""Точка входа программы «Пустошь Маркетинг» (её запускает значок на рабочем столе).
Выбирает самую новую версию кода (встроенную или скачанную обновлением) и запускает окно."""
import os, re, sys, traceback

try:                                   # сборщик увидит все нужные библиотеки через этот файл
    import _deps_stub                  # noqa: F401
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def data_dir():
    if os.environ.get('MKT_HOME'):
        return os.environ['MKT_HOME']
    if os.environ.get('APPDATA'):
        return os.path.join(os.environ['APPDATA'], 'PustoshMarketing')
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.expanduser('~'), 'PustoshMarketing')
    return os.path.join(HERE, 'data')


def bundled_dir():
    base = getattr(sys, '_MEIPASS', HERE) if getattr(sys, 'frozen', False) else HERE
    return os.path.join(base, 'app')


def vtuple(v):
    return tuple(int(x) for x in re.findall(r'\d+', str(v))[:4]) or (0,)


def read_version(d):
    try:
        with open(os.path.join(d, 'version.py'), encoding='utf-8') as f:
            m = re.search(r"VERSION\s*=\s*'([^']+)'", f.read())
        return m.group(1) if m else '0'
    except OSError:
        return '0'


def pick_app_dir():
    best = bundled_dir()
    bv = read_version(best)
    upd = os.path.join(data_dir(), 'updates')
    if os.path.isdir(upd):
        for x in os.listdir(upd):
            p = os.path.join(upd, x)
            if os.path.exists(os.path.join(p, '.ok')) and vtuple(read_version(p)) > vtuple(bv):
                best, bv = p, read_version(p)
    return best


def setup_log():
    d = data_dir()
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, 'app.log')
    try:
        if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
            os.replace(path, path + '.1')
    except OSError:
        pass
    f = open(path, 'a', encoding='utf-8', buffering=1)
    sys.stdout = sys.stderr = f
    return f


def message_box(text):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, 'Пустошь Маркетинг', 0x10)
    except Exception:
        pass


def bundled_deps():
    try:
        import json
        with open(os.path.join(bundled_dir(), 'build_info.json'), encoding='utf-8') as f:
            return json.load(f).get('deps_hash', '')
    except Exception:
        return ''


def main():
    argv = sys.argv[1:]
    if getattr(sys, 'frozen', False) or sys.stdout is None or sys.stderr is None:
        setup_log()
    os.environ.setdefault('MKT_BASE_DEPS', bundled_deps())
    app = bundled_dir() if '--selftest' in argv else pick_app_dir()
    sys.path.insert(0, app)
    try:
        if '--selftest' in argv:
            import selftest
            i = argv.index('--selftest')
            out = argv[i + 1] if len(argv) > i + 1 and not argv[i + 1].startswith('--') else 'selftest.txt'
            return selftest.run(out, live='--live' in argv)
        import server
        print('запуск из', app, flush=True)
        return server.main(argv)
    except SystemExit:
        raise
    except BaseException:
        tb = traceback.format_exc()
        print(tb, flush=True)
        message_box('Программа не смогла запуститься.\n\nПодробности записаны в файл:\n%s\n\nПришли его мне в чат.' % os.path.join(data_dir(), 'app.log'))
        return 1


if __name__ == '__main__':
    sys.exit(main() or 0)
