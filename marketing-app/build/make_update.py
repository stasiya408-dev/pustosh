#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Служебный скрипт сборки.
  python build/make_update.py prepare     — пишет app/build_info.json и build/_deps_stub.py (до PyInstaller)
  python build/make_update.py pack OUTDIR — собирает app-<версия>.zip и latest.json (после проверок)
"""
import ast, hashlib, json, os, re, sys, time, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
# Эти модули кладём в сборку «про запас», чтобы мелкие обновления кода не требовали нового установщика
EXTRA = ['ssl', 'asyncio', 'concurrent.futures', 'sqlite3', 'zlib', 'bz2', 'lzma', 'ctypes', 'logging.handlers', 'email.mime.text',
         'email.mime.multipart', 'html.parser', 'xml.etree.ElementTree', 'csv', 'secrets', 'hmac', 'hashlib', 'base64', 'binascii',
         'struct', 'statistics', 'difflib', 'textwrap', 'unicodedata', 'string', 'itertools', 'functools', 'collections', 'datetime',
         'calendar', 'decimal', 'fractions', 'queue', 'sched', 'signal', 'select', 'selectors', 'ipaddress', 'getpass', 'shlex',
         'glob', 'fnmatch', 'tempfile', 'shutil', 'zipfile', 'tarfile', 'gzip', 'mimetypes', 'http.client', 'http.cookies',
         'urllib.request', 'urllib.parse', 'urllib.error', 'webbrowser', 'platform', 'locale', 'codecs', 'random', 'math', 'uuid',
         'configparser', 'pathlib', 'typing', 'dataclasses', 'enum', 'copy', 'pprint', 'traceback', 'warnings', 'weakref', 'inspect',
         'importlib', 'runpy', 'pkgutil', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont', 'PIL.ImageFilter', 'PIL.ImageOps',
         'telethon', 'telethon.sessions', 'telethon.tl.types', 'telethon.tl.functions', 'telethon.errors', 'telethon.utils']


def local_names():
    return {os.path.splitext(f)[0] for f in os.listdir(APP) if f.endswith('.py')}


def scan():
    loc = local_names()
    stmts, tops = set(), set()
    for f in sorted(os.listdir(APP)):
        if not f.endswith('.py'):
            continue
        with open(os.path.join(APP, f), encoding='utf-8') as fh:
            tree = ast.parse(fh.read())
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name.split('.')[0] not in loc:
                        stmts.add('import ' + a.name)
                        tops.add(a.name)
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                if n.module.split('.')[0] not in loc:
                    stmts.add(ast.unparse(n))
                    tops.add(n.module)
    for m in EXTRA:
        stmts.add('import ' + m)
        tops.add(m)
    return sorted(stmts), sorted(tops)


def version():
    with open(os.path.join(APP, 'version.py'), encoding='utf-8') as f:
        return re.search(r"VERSION\s*=\s*'([^']+)'", f.read()).group(1)


def deps_hash():
    return hashlib.sha1(','.join(scan()[1]).encode()).hexdigest()[:12]


def prepare():
    stmts, tops = scan()
    with open(os.path.join(ROOT, 'build', '_deps_stub.py'), 'w', encoding='utf-8') as f:
        f.write('# сгенерировано make_update.py: список библиотек для сборщика\n')
        for s in stmts:
            f.write('try:\n    %s\nexcept Exception:\n    pass\n' % s)
    with open(os.path.join(APP, 'build_info.json'), 'w', encoding='utf-8') as f:
        json.dump({'deps_hash': deps_hash(), 'version': version(), 'built': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}, f)
    print('версия', version(), 'deps', deps_hash(), 'модулей', len(tops))


def notes():
    try:
        with open(os.path.join(ROOT, 'NOTES.txt'), encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    return line.strip()
    except OSError:
        pass
    return ''


def pack(out):
    os.makedirs(out, exist_ok=True)
    ver = version()
    name = 'app-%s.zip' % ver
    path = os.path.join(out, name)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(APP):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for fn in files:
                if fn.endswith(('.pyc', '.log')):
                    continue
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, APP).replace(os.sep, '/'))
    with open(path, 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    info = {'version': ver, 'zip': name, 'sha256': sha, 'notes': notes(), 'deps_hash': deps_hash(),
            'source': os.environ.get('GITHUB_SHA', '')[:10], 'built': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
    with open(os.path.join(out, 'latest.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'prepare':
        prepare()
    elif cmd == 'pack':
        pack(sys.argv[2])
    else:
        print(__doc__)
