# -*- coding: utf-8 -*-
"""Настройки и хранилище. Ключи вводятся в самой программе (вкладка «Подключения»)."""
import os, sys, json, time, threading

CODE = os.path.dirname(os.path.abspath(__file__))


def _data_dir():
    if os.environ.get('MKT_HOME'):
        return os.environ['MKT_HOME']
    if os.environ.get('APPDATA'):                       # Windows: C:\Users\Имя\AppData\Roaming\PustoshMarketing
        return os.path.join(os.environ['APPDATA'], 'PustoshMarketing')
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.expanduser('~'), 'PustoshMarketing')
    return os.path.join(os.path.dirname(CODE), 'data')  # запуск из исходников


BASE = _data_dir()
MEDIA = os.path.join(BASE, 'media')
os.makedirs(MEDIA, exist_ok=True)

DATA = os.path.join(BASE, 'data.json')
_lock = threading.RLock()
S = {}

# Какие настройки можно менять из окна программы
SETTING_KEYS = (
    'ANTHROPIC_API_KEY', 'POST_LANG', 'GAME_BOT_LINK', 'GAME_INFO',
    'TG_API_ID', 'TG_API_HASH', 'TG_DELAY_MIN', 'TG_DELAY_MAX', 'TG_DAILY_LIMIT',
    'THREADS_APP_ID', 'THREADS_APP_SECRET', 'THREADS_REDIRECT_URI',
    'GITHUB_MEDIA_REPO', 'GITHUB_TOKEN', 'YT_PRIVACY', 'OPENAI_API_KEY', 'OPENAI_IMAGE_MODEL',
)
SECRET_KEYS = ('ANTHROPIC_API_KEY', 'TG_API_HASH', 'THREADS_APP_SECRET', 'GITHUB_TOKEN', 'OPENAI_API_KEY')


def load():
    try:
        with open(DATA, encoding='utf-8') as f:
            j = json.load(f)
    except Exception:
        j = {}
    S.clear()
    S.update(j)
    S.setdefault('chats', {})        # id -> данные чата из Телеграма
    S.setdefault('threads', {})
    S.setdefault('settings', {})
    S.setdefault('cats', None)       # пользовательские категории (None = стандартные)
    S.setdefault('tg_sent', {})      # {'date': 'YYYY-MM-DD', 'n': 0}
    return S


def save():
    with _lock:
        tmp = DATA + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(S, f, ensure_ascii=False, indent=1)
        os.replace(tmp, DATA)


load()


def env(k, d=''):
    """Сначала настройки из программы, потом (для тестов и служебных адресов) переменная MKT_<имя>."""
    v = S.get('settings', {}).get(k)
    if v is not None and str(v).strip():
        return str(v).strip()
    v = os.environ.get('MKT_' + k)
    if v and v.strip():
        return v.strip()
    return d


def set_settings(d):
    with _lock:
        for k, v in d.items():
            if k in SETTING_KEYS:
                S['settings'][k] = (v or '').strip() if isinstance(v, str) else v
        save()


def masked(k):
    v = env(k)
    if not v:
        return ''
    return '••••' + v[-4:] if len(v) > 8 else '••••'


def now():
    return int(time.time())


def today():
    return time.strftime('%Y-%m-%d')
