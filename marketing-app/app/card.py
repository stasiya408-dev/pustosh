# -*- coding: utf-8 -*-
"""Карточка: скриншот игры + крупный заголовок + плашка «Играть в Телеграме»."""
import os, re

FONTS = [
    'C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/calibrib.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf',
    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
]


def available():
    try:
        import PIL  # noqa
        return True
    except Exception:
        return False


def _font(size):
    from PIL import ImageFont
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _clean(t):
    # эмодзи в шрифт карточки не попадают
    return re.sub(r'[\U00010000-\U0010ffff\u2600-\u27bf\ufe0f]', '', t or '').strip()


def _wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_card(src, title, sub, banner, out, size=(1080, 1350)):
    """Возвращает путь к готовой картинке (JPEG 4:5)."""
    from PIL import Image, ImageDraw
    W, H = size
    im = Image.open(src).convert('RGB')
    # обрезка «по центру» до нужной пропорции
    k = max(W / im.width, H / im.height)
    im = im.resize((max(W, round(im.width * k)), max(H, round(im.height * k))), Image.LANCZOS)
    x0, y0 = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x0, y0, x0 + W, y0 + H)).convert('RGBA')
    # затемнение снизу (градиент)
    grad = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    top = int(H * 0.42)
    for y in range(top, H):
        a = int(235 * ((y - top) / (H - top)) ** 1.4)
        gd.line([(0, y), (W, y)], fill=(12, 6, 3, a))
    im = Image.alpha_composite(im, grad)
    d = ImageDraw.Draw(im)
    m = 64
    title, sub, banner = _clean(title), _clean(sub), _clean(banner)
    # плашка внизу
    bh = 118
    if banner:
        d.rounded_rectangle([m, H - m - bh, W - m, H - m], radius=26, fill=(214, 148, 40, 255), outline=(255, 226, 150, 255), width=4)
        bf = _font(46)
        tw = d.textlength(banner, font=bf)
        d.text(((W - tw) / 2, H - m - bh + (bh - 46) / 2 - 6), banner, font=bf, fill=(40, 20, 6, 255))
    # заголовок: подбираем размер так, чтобы влез в 3 строки
    y_bottom = H - m - bh - 36 if banner else H - m
    size_t = 96
    while size_t > 44:
        tf = _font(size_t)
        lines = _wrap(d, title, tf, W - 2 * m)
        if len(lines) <= 3:
            break
        size_t -= 6
    tf = _font(size_t)
    lines = _wrap(d, title, tf, W - 2 * m)[:3]
    sf = _font(40)
    sub_h = 60 if sub else 0
    lh = int(size_t * 1.12)
    y = y_bottom - sub_h - lh * len(lines)
    for ln in lines:
        d.text((m + 3, y + 3), ln, font=tf, fill=(0, 0, 0, 255))
        d.text((m, y), ln, font=tf, fill=(255, 240, 205, 255))
        y += lh
    if sub:
        d.text((m + 2, y + 4), sub, font=sf, fill=(0, 0, 0, 255))
        d.text((m, y + 2), sub, font=sf, fill=(244, 190, 90, 255))
    im.convert('RGB').save(out, 'JPEG', quality=92)
    return out
