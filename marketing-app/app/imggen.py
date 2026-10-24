# -*- coding: utf-8 -*-
"""Дополнительные картинки через GPT (OpenAI Images API): фото из игры идёт как образец стиля.
Только стандартная библиотека + Pillow (он уже есть в программе), поэтому новый установщик не нужен."""
import base64, os, secrets, time
import net
from cfg import env, MEDIA

SIZES = {'tall': '1024x1536', 'square': '1024x1024', 'wide': '1536x1024'}
QUALITY = ('low', 'medium', 'high')
MODELS = ('gpt-image-2', 'gpt-image-1.5', 'gpt-image-1')       # по очереди, если у ключа нет доступа к более новой

BASE_PROMPT = (
    "Use the attached picture from a mobile game as the reference for art style, characters, colours, lighting and mood. "
    "Create a NEW promotional illustration for a social-media post about the game «Пустошь» (a Ukrainian Cossack steppe adventure). "
    "Keep the same visual style and the same character and setting design as in the reference, but do not copy it: "
    "show a different moment, pose or camera angle. "
    "Absolutely no text, letters, numbers, logos, watermarks or interface elements anywhere in the image. "
    "Leave a little calm space at the top and at the bottom of the frame.")


def base_url():
    return env('OPENAI_URL', 'https://api.openai.com').rstrip('/')


def ready():
    k = env('OPENAI_API_KEY')
    return bool(k) and 'ВСТАВЬ' not in k


def make_prompt(idea='', note=''):
    wish = (idea or '').strip() or (note or '').strip()
    wish = wish[:600]
    if wish:
        return BASE_PROMPT + "\nWhat the picture should show (the author's idea, may be in Russian): " + wish
    return BASE_PROMPT + "\nChoose an eye-catching moment that suits the reference."


def _ref_file(path):
    """Уменьшенная копия фото для отправки (до 1536 px). Возвращает (путь, временный_ли)."""
    out = os.path.join(MEDIA, 'ref_%s.jpg' % secrets.token_hex(3))
    try:
        from PIL import Image
        im = Image.open(path).convert('RGB')
        im.thumbnail((1536, 1536))
        im.save(out, 'JPEG', quality=90)
        return out, True
    except Exception:
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png', '.webp') and os.path.getsize(path) < 40 * 1024 * 1024:
            return path, False
        raise net.NetError('Не получилось подготовить фото для GPT')


def explain(st, d):
    """Понятный текст ошибки OpenAI."""
    e = d.get('error') if isinstance(d, dict) else None
    code = str((e or {}).get('code') or '') if isinstance(e, dict) else ''
    msg = net.api_err(d, st)
    low = (msg + ' ' + code).lower()
    if st == 401:
        return 'ключ OpenAI не подошёл (проверь его во вкладке «Подключения»)'
    if 'insufficient_quota' in low or 'billing' in low or 'exceeded your current quota' in low:
        return 'на балансе OpenAI нет денег: пополни баланс на platform.openai.com → Settings → Billing'
    if 'verif' in low:
        return 'OpenAI просит подтвердить организацию для этой модели: platform.openai.com → Settings → Organization → Verify (займёт несколько минут)'
    if 'moderation' in low or 'safety' in low or 'content_policy' in low:
        return 'фильтр OpenAI не пропустил запрос: опиши картинку иначе (без насилия и крови)'
    if st == 429:
        return 'OpenAI просит подождать (слишком много запросов). Попробуй через минуту'
    return msg


def _model_problem(st, d):
    """Похоже ли, что дело в самой модели (нет доступа/нет такой) — тогда пробуем следующую."""
    msg = net.api_err(d, st).lower()
    e = d.get('error') if isinstance(d, dict) else None
    code = str((e or {}).get('code') or '').lower() if isinstance(e, dict) else ''
    if st == 404 or 'model_not_found' in code:
        return True
    if st in (400, 403) and ('model' in msg or 'verif' in msg) and any(w in msg for w in ('not found', 'does not exist', 'access', 'verif', 'not supported', 'unknown')):
        return True
    return False


def _ext(data):
    if data[:4] == b'\x89PNG':
        return '.png'
    if data[:4] == b'RIFF':
        return '.webp'
    return '.jpg'


def generate(ref_path, idea='', note='', n=2, size='tall', quality='medium', log=None):
    """Рисует n новых картинок по образцу. Возвращает ([{'path','w','h'}], использованная_модель).
    Бросает net.NetError с понятным текстом."""
    if not ready():
        raise net.NetError('Ключ OpenAI ещё не введён (вкладка «Подключения»)')
    n = max(1, min(4, int(n or 1)))
    size = size if size in SIZES else 'tall'
    quality = quality if quality in QUALITY else 'medium'
    own = env('OPENAI_IMAGE_MODEL')
    models = (own,) if own else MODELS
    ref, tmp = _ref_file(ref_path)
    try:
        first_err = None
        for model in models:
            fields = {'model': model, 'prompt': make_prompt(idea, note), 'n': n, 'size': SIZES[size], 'quality': quality,
                      'output_format': 'jpeg', 'output_compression': 90}
            body, ctype = net.multipart(fields, {'image[]': ('reference.jpg', ref)})
            if log:
                log('OpenAI: рисую %d шт., модель %s, %s, качество %s' % (n, model, SIZES[size], quality))
            st, h, raw = net.request('POST', base_url() + '/v1/images/edits',
                                     {'Authorization': 'Bearer ' + env('OPENAI_API_KEY'), 'Content-Type': ctype}, body, timeout=420)
            d = net.jload(raw)
            if st == 200 and isinstance(d, dict) and d.get('data'):
                return _save(d, size), model
            if st == 200:
                raise net.NetError('GPT не вернул картинку. Попробуй ещё раз или опиши идею иначе.')
            if first_err is None:
                first_err = explain(st, d)
            if len(models) > 1 and _model_problem(st, d):
                continue
            raise net.NetError('GPT: ' + explain(st, d), st)
        raise net.NetError('GPT: ' + (first_err or 'нет ответа'))
    finally:
        if tmp:
            try:
                os.remove(ref)
            except OSError:
                pass


def _save(d, size):
    w, h = (int(x) for x in SIZES[size].split('x'))
    out = []
    stamp = int(time.time() * 1000)
    for i, it in enumerate(d.get('data') or []):
        b = it.get('b64_json') if isinstance(it, dict) else None
        if not b:
            continue
        try:
            data = base64.b64decode(b)
        except Exception:
            continue
        p = os.path.join(MEDIA, 'gen_%d_%d%s' % (stamp, i, _ext(data)))
        with open(p, 'wb') as f:
            f.write(data)
        out.append({'path': p, 'w': w, 'h': h})
    if not out:
        raise net.NetError('GPT не вернул картинку. Попробуй ещё раз или опиши идею иначе.')
    return out
