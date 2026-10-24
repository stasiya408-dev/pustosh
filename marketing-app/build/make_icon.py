# -*- coding: utf-8 -*-
"""Рисует значок программы app.ico (запускается вручную: python build/make_icon.py)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 512
im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
# фон: скруглённый квадрат с тёплым градиентом
bg = Image.new('RGBA', (S, S))
px = bg.load()
for y in range(S):
    for x in range(S):
        t = (x * 0.4 + y * 0.9) / (S * 1.3)
        px[x, y] = (int(238 - 120 * t), int(168 - 110 * t), int(58 - 40 * t), 255)
mask = Image.new('L', (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([10, 10, S - 10, S - 10], radius=110, fill=255)
im.paste(bg, (0, 0), mask)
d = ImageDraw.Draw(im)
d.rounded_rectangle([10, 10, S - 10, S - 10], radius=110, outline=(255, 226, 150, 255), width=10)
font = None
for p in ['C:/Windows/Fonts/arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
    if os.path.exists(p):
        font = ImageFont.truetype(p, 330)
        break
txt = 'П'
w = d.textlength(txt, font=font)
sh = Image.new('RGBA', (S, S), (0, 0, 0, 0))
ImageDraw.Draw(sh).text(((S - w) / 2 + 8, 70 + 10), txt, font=font, fill=(40, 16, 4, 170))
im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(6)))
ImageDraw.Draw(im).text(((S - w) / 2, 70), txt, font=font, fill=(52, 24, 8, 255))
# маленькая сабля-полоска внизу
d = ImageDraw.Draw(im)
d.polygon([(110, 410), (400, 410), (420, 430), (110, 430)], fill=(255, 240, 200, 235))
d.rectangle([92, 400, 118, 440], fill=(120, 40, 20, 255))
here = os.path.dirname(os.path.abspath(__file__))
im.save(os.path.join(here, 'app.ico'), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
im.resize((256, 256), Image.LANCZOS).save(os.path.join(here, 'app_preview.png'))
print('готово')
