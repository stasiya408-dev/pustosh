#!/usr/bin/env python3
"""«Козак 2»: пиксельная копия игры.

python3 tools/make_px.py            -> kozak2/index.html
Берёт ../index.html (основная игра), превращает ВСЕ встроенные картинки в крупные пиксели
с одной общей палитрой (ручная палитра из tools/px_palette.py + цвета из самих картинок),
подключает пиксельный шрифт, отдельное сохранение (kozak3px) и без облака Telegram.
Если для картинки есть нарисованная вручную замена (kozak2_art/<имя>.png), она подставляется
вместо автоматической (см. HAND в конце файла; пока пусто).
Размеры картинок НЕ меняются: игра рассчитана на координаты исходных картинок.
"""
import re, base64, io, sys, os, hashlib, json, time
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html')
OUT_DIR = os.environ.get('PX_OUT') or os.path.join(ROOT, 'kozak2')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px_palette import HAND

CAP_W = int(os.environ.get('PX_CAP', 224))      # сколько пикселей арта в ширину у картинки во весь экран
MIN_W = int(os.environ.get('PX_MIN', 48))       # минимум у мелких иконок
DIT = float(os.environ.get('PX_DIT', 5.0))   # сила упорядоченного дизеринга (9 был слишком «шашечный»)
DIT_ICON = 0.0   # мелкие картинки (иконки, значки) без дизеринга: так читаются лучше
SAT, CON = 1.14, 1.10
CORPUS = 96      # цветов из самих картинок

BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16.0 - 0.5
RX = re.compile(r'[A-Za-z0-9+/]{400,}={0,2}')
KINDS = (('UklGR', 'webp'), ('iVBOR', 'png'), ('/9j/', 'jpg'))


def kind_of(t):
    for p, k in KINDS:
        if t.startswith(p):
            return k
    return None


def small(args):
    """шаг 1: уменьшить картинку блоками -> маленькие RGB и альфа"""
    kind, b64 = args
    try:
        im = Image.open(io.BytesIO(base64.b64decode(b64)))
        if getattr(im, 'n_frames', 1) > 1:
            return None
        im.load()
        w, h = im.size
        if w * h < 400 or min(w, h) < 6:
            return None
        rgba = np.array(im.convert('RGBA'))
        a = rgba[..., 3]
        op = a > 8
        if not op.any():
            return None
        rgb = rgba[..., :3][op]
        # маски (каналы 0/255) не трогаем: игра считает по их цветам
        if ((rgb < 24) | (rgb > 231)).all(axis=1).mean() > 0.93:
            return ('skip', w, h)
        aw = min(CAP_W, max(MIN_W, w / 5.5))
        k = max(2, int(round(w / aw)))
        sw, sh = -(-w // k), -(-h // k)
        pad = np.pad(rgba.astype(np.float32), ((0, sh * k - h), (0, sw * k - w), (0, 0)), mode='edge')
        af = pad[..., 3] / 255.0

        def blk(x):
            return x.reshape(sh, k, sw, k).mean(axis=(1, 3))
        A = blk(af)
        RGB = np.stack([blk(pad[..., c] * af) for c in range(3)], -1) / np.maximum(A[..., None], 1e-4)
        g = RGB.mean(-1, keepdims=True)
        RGB = g + (RGB - g) * SAT
        RGB = (RGB - 128) * CON + 128
        RGB = np.clip(RGB, 0, 255)
        full = A.min() > 0.99
        if not full:
            v = A[A > 0.02]
            soft = len(v) > 0 and (((v > 0.1) & (v < 0.9)).mean() > 0.25)
            A = np.round(A * 3) / 3 if soft else (A >= 0.5).astype(np.float32)
        return ('ok', w, h, k, RGB.astype(np.float32), A.astype(np.float32), full)
    except Exception as e:
        return ('err', str(e))


PAL = None
TREE = None


def init(pal):
    global PAL, TREE
    PAL = pal
    TREE = cKDTree(pal.astype(np.float32))


def finish(args):
    """шаг 2: палитра + дизеринг + увеличение блоков + кодирование"""
    kind, s = args
    _, w, h, k, RGB, A, full = s
    sh, sw = RGB.shape[:2]
    yy, xx = np.mgrid[0:sh, 0:sw]
    d = BAY[yy % 4, xx % 4][..., None] * (DIT_ICON if (w <= 200 and h <= 200) else DIT)
    idx = TREE.query((RGB + d).reshape(-1, 3))[1].reshape(sh, sw)
    col = PAL[idx]
    col = np.repeat(np.repeat(col, k, 0), k, 1)[:h, :w]
    if full:
        im = Image.fromarray(col.astype(np.uint8), 'RGB')
    else:
        al = np.repeat(np.repeat(A, k, 0), k, 1)[:h, :w]
        out = np.dstack([col, (al * 255 + 0.5).astype(np.uint8)]).astype(np.uint8)
        out[out[..., 3] == 0, :3] = 0
        im = Image.fromarray(out, 'RGBA')
    bio = io.BytesIO()
    if kind == 'jpg' and full:
        im.save(bio, 'JPEG', quality=95, subsampling=0)
    elif kind == 'png':
        im.save(bio, 'PNG', optimize=True)
    else:
        im.save(bio, 'WEBP', lossless=True, quality=100, method=4)
    return base64.b64encode(bio.getvalue()).decode()


def build_palette(smalls):
    rng = np.random.RandomState(7)
    pts = []
    for s in smalls:
        RGB, A = s[4], s[5]
        m = A.reshape(-1) > 0.5
        p = RGB.reshape(-1, 3)[m]
        if len(p) == 0:
            continue
        n = min(len(p), 2500)
        pts.append(p[rng.choice(len(p), n, replace=False)])
    pts = np.concatenate(pts).astype(np.uint8)
    cols = 1000
    rows = len(pts) // cols
    tile = Image.fromarray(pts[:rows * cols].reshape(rows, cols, 3), 'RGB')
    q = tile.quantize(colors=CORPUS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:CORPUS * 3], np.uint8).reshape(-1, 3)
    hand = np.array(HAND, np.uint8)
    keep = [p for p in pal if np.sqrt(((hand.astype(int) - p.astype(int)) ** 2).sum(1)).min() > 16]
    full = np.concatenate([hand, np.array(keep, np.uint8)]) if keep else hand
    return full


FONT_CSS = ''


def font_css():
    """Пиксельный шрифт: Tiny5 (латиница, кириллица, укр. буквы) + Press Start 2P как запасной."""
    base = os.path.join(ROOT, 'tools', 'fonts')
    out = ''
    for name, fam, adj in (('Tiny5.ttf', 'PXA', 122), ('PressStart2P.ttf', 'PXB', 70)):
        p = os.path.join(base, name)
        if os.path.exists(p):
            out += "@font-face{font-family:'%s';src:url(data:font/ttf;base64,%s) format('truetype');font-display:block;size-adjust:%d%%}" % (
                fam, base64.b64encode(open(p, 'rb').read()).decode(), adj)
    return out


HEAD = r'''<script>/* kozak2: отдельные сохранения и пиксели */
try{if(!localStorage.getItem("kozak3px")&&localStorage.getItem("kozak3"))localStorage.setItem("kozak3px",localStorage.getItem("kozak3"))}catch(e){}
(function(){var g=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(t,o){var c=g.call(this,t,o);try{if(c&&t==="2d")c.imageSmoothingEnabled=false}catch(e){}return c}})();
</script>
<style id="pxcss">%s
*{image-rendering:pixelated;font-synthesis:none}
html.pxbig .pxh{font-family:'PXA','PXB',monospace!important}
</style>
<script>/* kozak2: пиксельный шрифт только для КРУПНЫХ надписей (>=PXMIN px на экране), мелкий текст остаётся обычным: так его можно читать */
(function(){var PXMIN=20,off=false;try{off=localStorage.getItem("pxfont")==="0"}catch(e){}
function chk(e){try{if(e.nodeType!==1||e.closest("canvas"))return;var own=0,n=e.firstChild;while(n){if(n.nodeType===3&&n.nodeValue.trim()){own=1;break}n=n.nextSibling}
if(!own){if(e.classList.contains("pxh"))e.classList.remove("pxh");return}
var h=e.offsetHeight;if(!h){return}var r=e.getBoundingClientRect(),sc=r.height/h;if(!isFinite(sc)||sc<=0)sc=1;
var fs=parseFloat(getComputedStyle(e).fontSize)*sc;var big=fs>=PXMIN;if(big!==e.classList.contains("pxh"))e.classList.toggle("pxh",big)}catch(x){}}
function scan(root){var l=(root||document.body).querySelectorAll("*");for(var i=0;i<l.length;i++)chk(l[i])}
function go(){if(off)return;document.documentElement.classList.add("pxbig");scan();
new MutationObserver(function(ms){for(var i=0;i<ms.length;i++)for(var j=0;j<ms[i].addedNodes.length;j++){var a=ms[i].addedNodes[j];if(a.nodeType===1){chk(a);if(a.querySelectorAll)scan(a)}}}).observe(document.body,{childList:true,subtree:true});
setInterval(function(){if(!document.hidden)scan()},2500)}
window.pxFont=function(on){try{localStorage.setItem("pxfont",on?"1":"0")}catch(e){}location.reload()};
if(document.readyState!=="loading")go();else document.addEventListener("DOMContentLoaded",go)})();
</script>
'''


def patch(s):
    def rep(a, b, n=1):
        nonlocal s
        c = s.count(a)
        assert c == n, (a[:60], c)
        s = s.replace(a, b)
    rep('"kozak3"', '"kozak3px"', 8)
    rep('var ok=!!(cs&&cs.setItems&&cs.getItems&&(!tg.isVersionAtLeast||tg.isVersionAtLeast("6.9")));', 'var ok=false;')
    rep('if(cs&&cs.removeItems)', 'if(false)')
    rep('<head>', '<head>\n' + HEAD % font_css())
    s = re.sub(r'id="hver">v(\d+)<', r'id="hver">v\1·пікс<', s, count=1)
    s = s.replace('<title>', '<title>КОЗАК 2 · ', 1)
    return s


def main():
    t0 = time.time()
    s = open(SRC, encoding='utf8').read()
    items = []
    for m in RX.finditer(s):
        k = kind_of(m.group(0))
        if k:
            items.append((m.start(), m.end(), k, m.group(0)))
    print('картинок:', len(items))
    uniq = {}
    for it in items:
        uniq.setdefault(hashlib.md5(it[3].encode()).hexdigest(), (it[2], it[3]))
    keys = list(uniq)
    with Pool(8) as p:
        sm = p.map(small, [uniq[k] for k in keys], chunksize=4)
    okk = [(k, r) for k, r in zip(keys, sm) if r and r[0] == 'ok']
    skipped = [(k, r) for k, r in zip(keys, sm) if r and r[0] == 'skip']
    errs = [(k, r) for k, r in zip(keys, sm) if r and r[0] == 'err']
    print('уникальных', len(keys), 'пикселизовано', len(okk), 'пропущено масок', len(skipped), 'ошибок', len(errs), 'прочее', len(keys) - len(okk) - len(skipped) - len(errs))
    for k, r in errs[:5]:
        print('ERR', r)
    for k, r in skipped:
        print('  маска/как есть:', r[1], 'x', r[2])
    pal = build_palette([r for _, r in okk])
    print('палитра:', len(pal), 'цветов')
    json.dump([list(map(int, c)) for c in pal], open(os.path.join(ROOT, 'tools', 'px_palette_full.json'), 'w'))
    with Pool(8, initializer=init, initargs=(pal,)) as p:
        done = p.map(finish, [(uniq[k][0], r) for k, r in okk], chunksize=2)
    new = {k: d for (k, _), d in zip(okk, done)}
    # нарисованные вручную замены: kozak2_art/<имя>.png (сейчас: hut = фон хаты 600x893, tools/art/hut.py)
    art = os.path.join(ROOT, 'kozak2_art')
    mh = re.search(r'--hut:url\("data:image/jpeg;base64,([^"]+)"', s)
    if mh and os.path.exists(os.path.join(art, 'hut.png')):
        im = Image.open(os.path.join(art, 'hut.png')).convert('RGB')
        o = Image.open(io.BytesIO(base64.b64decode(mh.group(1))))
        if im.size != o.size:
            im = im.resize(o.size, Image.NEAREST)
        bio = io.BytesIO(); im.save(bio, 'JPEG', quality=95, subsampling=0)
        new[hashlib.md5(mh.group(1).encode()).hexdigest()] = base64.b64encode(bio.getvalue()).decode()
        print('hut: нарисованная замена')
    res = []
    last = 0
    for st, en, kd, txt in items:
        res.append(s[last:st])
        h = hashlib.md5(txt.encode()).hexdigest()
        res.append(new.get(h, txt))
        last = en
    res.append(s[last:])
    s2 = ''.join(res)
    s2 = patch(s2)
    os.makedirs(OUT_DIR, exist_ok=True)
    open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf8').write(s2)
    print('готово: %.1f МБ -> %.1f МБ, %.0f с' % (len(s) / 1e6, len(s2) / 1e6, time.time() - t0))


if __name__ == '__main__':
    main()
