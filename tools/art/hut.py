# Нарисованный вручную фон хаты «Козак 2» (пиксель как в образце). Выход: PNG 600x893 (блоки 4x4)
import numpy as np, sys
from PIL import Image, ImageDraw
W, H = 150, 224
img = np.zeros((H, W, 3), np.uint8)
YY, XX = np.mgrid[0:H, 0:W]
BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
B = BAY[YY % 4, XX % 4]
def C(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
def R(*hs): return np.array([C(h) for h in hs], np.uint8)
def _m(f):
    m = Image.new('L', (W, H), 0); f(ImageDraw.Draw(m)); return np.array(m) > 0
def poly(p): return _m(lambda d: d.polygon([tuple(q) for q in p], fill=255))
def ell(a, b, c, d_): return _m(lambda d: d.ellipse([a, b, c, d_], fill=255))
def rect(a, b, c, d_):
    m = np.zeros((H, W), bool); m[b:d_+1, a:c+1] = True; return m
def paint(mask, ramp, light, amp=0.7):
    n = len(ramp); v = light*(n-1) + (B-0.5)*amp
    idx = np.clip(np.floor(v+0.5), 0, n-1).astype(int); img[mask] = ramp[idx[mask]]
def flat(mask, col): img[mask] = C(col)
def lin(x0, y0, x1, y1, a=0., b=1.):
    dx, dy = x1-x0, y1-y0; t = ((XX-x0)*dx + (YY-y0)*dy)/(dx*dx+dy*dy)
    return a + (b-a)*np.clip(t, 0, 1)
def outline(mask, col='#24130a'):
    d = np.zeros_like(mask)
    d[1:] |= mask[:-1]; d[:-1] |= mask[1:]; d[:, 1:] |= mask[:, :-1]; d[:, :-1] |= mask[:, 1:]
    e = d & ~mask; img[e] = C(col)
def px(x, y, col):
    if 0 <= x < W and 0 <= y < H: img[y, x] = C(col)
def line(p0, p1, col, w=1):
    img[_m(lambda d: d.line([p0, p1], fill=255, width=w))] = C(col)

WALL = R('#5a4228', '#7a5c38', '#9c7a4a', '#c0a06a', '#dcc590', '#efdcaa')
WOOD = R('#24130a', '#3e2210', '#5e3a1a', '#82522a', '#a8743c')
CARP = R('#2a0a08', '#4a1210', '#6e1c14', '#942c1c', '#bc4426')
CLOTH = R('#84746c', '#a8988a', '#cdbfae', '#e8dcc8', '#f8f0df')
STEEL = R('#24130a', '#4a4440', '#84746c', '#b8b0a4', '#e8e0d0')
CLAY = R('#3e2210', '#5e3a1a', '#82522a', '#a8743c', '#c0884a')
rng = np.random.RandomState(7)

# --- стена: тёплая штукатурка, светлее у окна, темнее к углам
wl = lin(0, 0, W, 150, 0.82, 0.42) - 0.18*np.clip((XX-100)/50, 0, 1)
paint(np.ones((H, W), bool), WALL, wl, 0.22)
n = rng.rand(H, W)
img[(n > 0.986)] = WALL[2]; img[(n < 0.010)] = WALL[4]
# угол комнаты (тёмная вертикаль у окна)
paint(rect(61, 0, 63, 150), WALL, np.full((H, W), 0.2), 0.3)
# --- пол
FLY = 150
paint(rect(0, FLY, W-1, H-1), WOOD, lin(0, FLY, 0, H, 0.8, 0.42), 0.25)
for i, y in enumerate(range(FLY, H, 10)):                       # длинные доски вдоль, разный тон
    img[y:y+10, :] = (img[y:y+10, :]*(0.9+0.1*((i*7) % 3)/2)).astype(np.uint8)
    img[y, :] = WOOD[1]
    for x in range((i*37) % 70, W, 70+((i*13) % 25)): img[y:y+10, x] = WOOD[1]
paint(rect(0, FLY-5, W-1, FLY), WALL, np.full((H, W), 0.16), 0.3)      # плинтус-тень
paint(rect(0, FLY-1, W-1, FLY+1), WOOD, np.full((H, W), 0.15), 0.2)

# --- окно слева (рама и небо)
wx0, wy0, wx1, wy1 = 14, 16, 54, 92
paint(rect(wx0, wy0, wx1, wy1), R('#7cb0d8', '#a4cee8', '#d0eaf4', '#f6f2c6', '#fff6d0'), lin(0, wy0, 0, wy1, 0.1, 1.0), 0.6)
paint(rect(wx0, 64, wx1, wy1), R('#6a8a3a', '#8aa84a', '#c8c050', '#e8d060'), lin(0, 64, 0, wy1, 0.2, 0.9), 0.7)
for fx, fy in [(20, 74), (29, 80), (39, 72), (47, 82), (24, 86), (35, 88)]:   # подсолнухи
    flat(ell(fx-3, fy-3, fx+3, fy+3), '#f2c226'); flat(ell(fx-1, fy-1, fx+1, fy+1), '#5a3410')
    px(fx, fy+4, '#3a6a1a'); px(fx, fy+5, '#3a6a1a'); px(fx-1, fy+6, '#3a6a1a')
frame = rect(wx0-2, wy0-2, wx1+2, wy1+2) & ~rect(wx0, wy0, wx1, wy1)
paint(frame, WOOD, lin(0, wy0, 40, wy1, 0.9, 0.5), 0.5)
paint(rect(33, wy0, 34, wy1) | rect(wx0, 52, wx1, 53), WOOD, np.full((H, W), 0.8), 0.3)
paint(rect(8, wy1+3, 60, wy1+6), WOOD, lin(0, wy1+3, 0, wy1+7, 0.95, 0.55), 0.4)  # подоконник
paint(rect(10, wy1+7, 58, wy1+8), WOOD, np.full((H, W), 0.2), 0.2)
# --- луч света от окна (стена + пол)
shaft = poly([(56, 18), (56, 92), (104, 168), (70, 168)]) | poly([(70, 168), (104, 168), (118, 214), (62, 214)])
ww = shaft & (YY < FLY)
img[ww & (B < 0.38)] = WALL[5]; img[ww & (B >= 0.38) & (B < 0.64)] = WALL[4]
ff = shaft & (YY >= FLY)
img[ff & (B < 0.42)] = WOOD[4]; img[ff & (B >= 0.42) & (B < 0.7)] = WOOD[3]

# --- рушник на стене (справа-посередине)
tx0, tx1, ty0, ty1 = 88, 116, 0, 98
tw = poly([(tx0, ty0), (tx1, ty0), (tx1+1, ty1-4), ((tx0+tx1)//2+3, ty1), (tx0+2, ty1-6)])
paint(tw, CLOTH, lin(tx0, 0, tx1, 0, 0.85, 0.45), 0.45)
RED2 = R('#3c0808', '#6e1010', '#a01a1a', '#cc2c28')
for by in range(10, ty1-8, 22):                     # красные ромбовые полосы
    for k in range(tx0+3, tx1-2, 6):  # узор
        cx = k+1
        for dy in range(-3, 4):
            for dx in range(-(3-abs(dy)), 4-abs(dy)):
                if tw[by+dy, cx+dx]: img[by+dy, cx+dx] = RED2[3 if (dx+dy) % 2 == 0 else 2]
    img[by-5, tx0+1:tx1][tw[by-5, tx0+1:tx1]] = RED2[2]
    img[by+5, tx0+1:tx1][tw[by+5, tx0+1:tx1]] = RED2[2]
outline(tw, '#5a4228')
flat(rect(tx0+6, 0, tx1-6, 1), '#3e2210')
# --- сабля на стене (у правого края)
sx = 124
flat(rect(sx-2, 8, sx+4, 11), '#3e2210')                       # рукоять
paint(rect(sx-1, 11, sx+3, 14), STEEL, np.full((H, W), 0.15), 0.2)
paint(poly([(sx-3, 14), (sx+6, 14), (sx+6, 16), (sx-3, 16)]), STEEL, np.full((H, W), 0.3), 0.2)
paint(poly([(sx, 16), (sx+3, 16), (sx+6, 88), (sx+3, 90)]), STEEL, lin(sx, 0, sx+6, 0, 0.9, 0.3), 0.4)
outline(poly([(sx, 16), (sx+3, 16), (sx+6, 88), (sx+3, 90)]), '#24130a')
# --- полка и кувшин справа
paint(rect(110, 128, 149, 132), WOOD, lin(0, 126, 0, 131, 0.95, 0.45), 0.4)
paint(rect(112, 133, 149, 134), WOOD, np.full((H, W), 0.15), 0.2)
jug = ell(114, 103, 130, 128) | rect(119, 96, 125, 105)
paint(jug, CLAY, lin(114, 0, 130, 0, 0.95, 0.35), 0.5)
paint(rect(118, 94, 126, 97), CLAY, np.full((H, W), 0.7), 0.3)
outline(jug | rect(118, 94, 126, 97), '#24130a')
# --- ковёр на полу (красный с ромбами)
cy0 = 178
cp = poly([(0, cy0+4), (W, cy0-4), (W, H), (0, H)])
paint(cp, CARP, lin(0, cy0, 0, H, 0.55, 0.78), 0.55)
for k in range(0, 5):                                           # большие ромбы
    cx, cy = 18+k*34, cy0+34+(k % 2)*6
    for r_, c_ in [(14, 2), (10, 0), (6, 4), (3, 1)]:
        d = np.abs(XX-cx) + np.abs(YY-cy) <= r_
        img[d & cp] = CARP[c_]
for x in range(0, W, 3):                                        # кайма-зубчики
    px(x, cy0+2-(x*8//W)+(x % 2), '#d89868')
px(0, 0, '#5a4228')
# затемнение углов (виньетка), чтобы взгляд шёл к центру
vig = np.clip((np.abs(XX-W/2)/(W/2))**2*0.5 + np.clip((YY-170)/60, 0, 1)*0.35, 0, 0.6)
dark = (B < vig*1.1)
img[dark] = (img[dark]*0.62).astype(np.uint8)

out = Image.fromarray(img).resize((W*4, H*4), Image.NEAREST).crop((0, 0, 600, 893))
out.save(sys.argv[1] if len(sys.argv) > 1 else 'hut_art.png')
print('ok', out.size)
