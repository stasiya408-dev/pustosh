# -*- coding: utf-8 -*-
"""Генерация текстов постов через Claude (Anthropic API) + запасной вариант без ИИ."""
import base64, io, json, os, re
import net
from cfg import env, CODE

URL = env('ANTHROPIC_URL', 'https://api.anthropic.com')
MODEL = env('ANTHROPIC_MODEL', 'claude-sonnet-5-5')
LANG = {'ru': 'русский', 'uk': 'украинский'}.get(env('POST_LANG', 'ru').lower(), 'русский')


def ai_ready():
    k = env('ANTHROPIC_API_KEY')
    return bool(k) and 'ВСТАВЬ' not in k


def game_info():
    own = env('GAME_INFO')
    if own:
        return own
    p = os.path.join(CODE, 'game_info.txt')
    try:
        with open(p, encoding='utf-8-sig') as f:
            return f.read().strip()
    except Exception:
        return 'Казацкая игра в Телеграме.'


def link(platform):
    base = env('GAME_BOT_LINK')
    if not base or 'ВАШ' in base:
        return ''
    return base + ('&' if '?' in base else '?') + 'start=' + platform


def _jpeg_b64(path):
    """Уменьшает картинку (дешевле и быстрее) и отдаёт base64 JPEG."""
    try:
        from PIL import Image
        im = Image.open(path).convert('RGB')
        im.thumbnail((1280, 1280))
        bio = io.BytesIO()
        im.save(bio, 'JPEG', quality=85)
        return base64.b64encode(bio.getvalue()).decode()
    except Exception:
        with open(path, 'rb') as f:
            data = f.read()
        if len(data) > 4500000:
            return None
        return base64.b64encode(data).decode()


SYSTEM = """Ты — SMM-копирайтер независимой мобильной игры. Твоя задача: писать посты, которые хочется открыть и попробовать игру.
Правила:
- Пиши только факты из описания игры. Ничего не выдумывай: если чего-то нет в описании, о нём не пиши. Не обещай донатов, призов и онлайна, которых нет.
- Крючок в первой строке (интрига, вопрос или яркая деталь). Без пустых лозунгов и штампов вроде «уникальная игра».
- Язык постов: %(lang)s. Тон живой, без канцелярита. Эмодзи — умеренно.
- Если приложена картинка, опирайся на то, что на ней реально видно.
Верни ТОЛЬКО JSON без пояснений и без ```, с ключами:
"telegram": пост для Телеграм-канала, 300–700 знаков, 2–4 коротких абзаца, в конце призыв и ссылка из поля links.telegram (если ссылка пустая — без ссылки);
"threads": пост для Threads до 450 знаков, разговорный тон, мысль или вопрос, который хочется обсудить; ссылка из links.threads отдельной строкой (если есть); в самом конце РОВНО ОДИН хештег-тема;
"youtube_title": название ролика до 80 знаков, интрига без обмана;
"youtube_desc": описание 2–3 строки, потом ссылка из links.youtube (если есть), потом 3–5 хештегов, среди них #Shorts;
"card_title": короткий заголовок для картинки до 38 знаков, без эмодзи и без точки в конце;
"card_sub": подпись под заголовком до 60 знаков."""


def _cut(t, n):
    t = (t or '').strip()
    if len(t) <= n:
        return t
    t = t[:n]
    sp = t.rfind(' ')
    return (t[:sp] if sp > n * 0.6 else t).rstrip(' ,;:-—')


def fallback(note):
    n = (note or '').strip() or 'Новая картинка из игры «Пустошь»'
    out = {
        'telegram': n + ('\n\n🎮 Играть в Телеграме: ' + link('tg') if link('tg') else ''),
        'threads': n + ('\n' + link('threads') if link('threads') else ''),
        'youtube_title': _cut(n.split('\n')[0], 80),
        'youtube_desc': n + ('\n' + link('yt') if link('yt') else '') + '\n#Shorts #игра #козаки',
        'card_title': _cut(n.split('\n')[0].rstrip('.!'), 38),
        'card_sub': 'Игра в Телеграме',
    }
    return out


def generate(note, image_path=None, extra=''):
    """Возвращает словарь с текстами. Бросает net.NetError при проблемах с ключом/сетью."""
    if not ai_ready():
        return fallback(note)
    content = []
    if image_path and os.path.exists(image_path):
        b64 = _jpeg_b64(image_path)
        if b64:
            content.append({'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': b64}})
    ask = 'Описание игры:\n%s\n\nСсылки: %s\n\nО чём пост (заметка автора): %s\n%s\nСделай посты.' % (
        game_info(),
        json.dumps({'telegram': link('tg'), 'threads': link('threads'), 'youtube': link('yt')}, ensure_ascii=False),
        (note or '— (автор ничего не добавил, опирайся на картинку и описание)'),
        ('Пожелание к переделке: ' + extra) if extra else '')
    content.append({'type': 'text', 'text': ask})
    body = {'model': MODEL, 'max_tokens': 1500, 'system': SYSTEM % {'lang': LANG},
            'messages': [{'role': 'user', 'content': content}]}
    st, d, h = net.post_json(URL + '/v1/messages', body, {
        'x-api-key': env('ANTHROPIC_API_KEY'), 'anthropic-version': '2023-06-01'}, timeout=120)
    if st != 200:
        msg = net.api_err(d, st)
        if st == 401:
            msg = 'ключ Anthropic не подошёл (проверь ANTHROPIC_API_KEY)'
        raise net.NetError('ИИ: ' + msg, st)
    txt = ''.join(b.get('text', '') for b in d.get('content', []) if b.get('type') == 'text')
    m = re.search(r'\{.*\}', txt, re.S)
    try:
        j = json.loads(m.group(0)) if m else {}
    except Exception:
        j = {}
    fb = fallback(note)
    out = {}
    for k in fb:
        v = j.get(k)
        out[k] = v.strip() if isinstance(v, str) and v.strip() else fb[k]
    if not j:
        out['telegram'] = out['threads'] = txt.strip() or fb['telegram']
    out['threads'] = _cut(out['threads'], 500)
    out['youtube_title'] = _cut(out['youtube_title'], 95)
    out['card_title'] = _cut(out['card_title'], 44)
    out['card_sub'] = _cut(out['card_sub'], 70)
    return out


def from_custom(text, old=None):
    """Свой текст автора: раскладывает его по площадкам."""
    t = (text or '').strip()
    first = t.split('\n')[0]
    out = dict(old or fallback(t))
    out.update({'telegram': t, 'threads': _cut(t, 500), 'youtube_title': _cut(first, 95),
                'youtube_desc': t + ('\n#Shorts' if '#shorts' not in t.lower() else '')})
    if not old:
        out['card_title'] = _cut(first.rstrip('.!'), 44)
    return out


def ask(text, history=None):
    """Простой чат с Claude (вкладка «Claude»). Возвращает ответ текстом."""
    if not ai_ready():
        raise net.NetError('Ключ Claude ещё не введён (вкладка «Подключения»)')
    msgs = list(history or []) + [{'role': 'user', 'content': text}]
    body = {'model': MODEL, 'max_tokens': 1200,
            'system': 'Ты помощник маркетолога казацкой игры «Пустошь». Отвечай по-русски, коротко и по делу.',
            'messages': msgs[-12:]}
    st, d, h = net.post_json(URL + '/v1/messages', body, {
        'x-api-key': env('ANTHROPIC_API_KEY'), 'anthropic-version': '2023-06-01'}, timeout=120)
    if st != 200:
        msg = net.api_err(d, st)
        if st == 401:
            msg = 'ключ Claude не подошёл (проверь его во вкладке «Подключения»)'
        raise net.NetError('Claude: ' + msg, st)
    return ''.join(b.get('text', '') for b in d.get('content', []) if b.get('type') == 'text').strip()
