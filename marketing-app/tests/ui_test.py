# -*- coding: utf-8 -*-
"""Прогон окна программы в настоящем браузере (Chromium) + скриншоты в tests/shots."""
import io, json, os, shutil, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(os.path.dirname(HERE), 'app')
sys.path.insert(0, APP); sys.path.insert(0, HERE)
import fake
srv_fake, ST = fake.start()
BASE = 'http://127.0.0.1:%d' % ST.port
HOME = tempfile.mkdtemp(prefix='mkt_ui_')
os.environ.update({'MKT_HOME': HOME, 'MKT_TG_IMPL': 'fake_tgu:FakeTg', 'MKT_IDLE_EXIT': '0', 'MKT_ANTHROPIC_URL': BASE, 'MKT_OPENAI_URL': BASE,
                   'MKT_THREADS_BASE': BASE, 'MKT_THREADS_POLL': '0.02', 'MKT_GITHUB_API': BASE, 'MKT_UPDATE_URL': BASE + '/upd', 'MKT_BASE_DEPS': 'A'})
import cfg, server, jobs, net
from PIL import Image, ImageDraw
httpd = server.bind(0)
PORT = httpd.server_port
threading.Thread(target=httpd.serve_forever, daemon=True).start()
jobs.random_pause = lambda a, b: 0.3
SH = os.path.join(HERE, 'shots'); os.makedirs(SH, exist_ok=True)
cfg.set_settings({'ANTHROPIC_API_KEY': 'good-key', 'GAME_BOT_LINK': 'https://t.me/pustosh_bot', 'GITHUB_TOKEN': 'x', 'GITHUB_MEDIA_REPO': 'a/b',
                  'THREADS_APP_ID': 'A', 'THREADS_APP_SECRET': 'B', 'TG_API_ID': '1234567', 'TG_API_HASH': 'a' * 32})
cfg.S['threads'] = {'token': 'T', 'user_id': '777', 'username': 'kozak_dev', 'expires': cfg.now() + 50 * 86400, 'saved': cfg.now()}
cfg.save()
ST.upd_json = {'version': '1.2.0', 'zip': 'a.zip', 'notes': 'новые категории чатов', 'deps_hash': 'A'}

im = Image.new('RGB', (1280, 720), (40, 30, 20)); d = ImageDraw.Draw(im)
d.rectangle([0, 420, 1280, 720], fill=(90, 60, 30)); d.ellipse([500, 120, 780, 520], fill=(180, 90, 40)); d.text((40, 40), 'BOSS', fill=(255, 255, 255))
PIC = os.path.join(HOME, 'boss.jpg'); im.save(PIC)

from playwright.sync_api import sync_playwright
errors = []
FAIL = []
def check(c, label):
    print(('  ✔ ' if c else '  ✘ ') + label)
    if not c: FAIL.append(label)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1240, 'height': 860})
    pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto('http://127.0.0.1:%d/' % PORT)
    pg.wait_for_selector('h1')
    pg.screenshot(path=SH + '/1_post_empty.png')
    check('Новый пост' in pg.inner_text('h1'), 'открывается вкладка «Новый пост»')
    check(pg.is_visible('#banner'), 'виден баннер об обновлении')

    pg.click('[data-tab=tg]'); pg.wait_for_selector('#s_TG_API_ID')
    pg.screenshot(path=SH + '/2_tg_login.png')
    pg.fill('#tg_phone', '+380501234567'); pg.click('[data-act=tgphone]'); pg.wait_for_selector('#tg_code')
    pg.fill('#tg_code', '12345'); pg.click('[data-act=tgcode]'); pg.wait_for_selector('[data-act=tgload]')
    check('Вошёл как' in pg.inner_text('#main'), 'вход в Telegram через окно')
    pg.screenshot(path=SH + '/3_tg_empty.png')
    pg.click('[data-act=tgload]'); pg.wait_for_selector('.chrow')
    pg.screenshot(path=SH + '/4_tg_loaded.png')
    check(pg.locator('.chrow').count() == 11, 'показаны 11 чатов, куда можно писать')
    pg.click('[data-cat=fishing]')
    check(pg.locator('.chrow').count() == 2, 'категория «Рыбалка и охота»: 2 чата')
    pg.screenshot(path=SH + '/5_tg_fishing.png')
    pg.click('[data-sel="-1001"]'); pg.wait_for_timeout(300)
    check(cfg.S['chats']['-1001']['sel'], 'галочка выбирает чат')
    pg.click('[data-cat=all]'); pg.check('#blk'); pg.wait_for_timeout(200)
    check(pg.locator('.chrow').count() == 13, 'с галочкой «показывать недоступные» видны все 13')
    pg.uncheck('#blk')
    for cid in ('-1002', '-1006'):
        pg.click('[data-sel="%s"]' % cid); pg.wait_for_timeout(250)
    pg.fill('#q', 'авто'); pg.wait_for_timeout(200)
    check(pg.locator('.chrow').count() >= 1, 'поиск по названию')
    pg.fill('#q', '')
    pg.once('dialog', lambda d: d.accept())
    pg.click('[data-act=catadd]'); pg.wait_for_selector('#mi'); pg.fill('#mi', 'Мотоциклисты'); pg.click('#mo'); pg.wait_for_timeout(400)
    check(pg.locator('.cat', has_text='Мотоциклисты').count() == 1, 'своя категория появилась слева')

    pg.click('[data-tab=conn]'); pg.wait_for_selector('#s_ANTHROPIC_API_KEY')
    pg.screenshot(path=SH + '/6_conn.png', full_page=False)
    pg.click('[data-tab=claude]'); pg.wait_for_selector('[data-act=cltest]')
    pg.click('[data-act=cltest]'); pg.wait_for_selector('#cltres .ok')
    pg.screenshot(path=SH + '/7_claude.png')
    check(True, 'проверка связи с Claude прошла')

    pg.click('[data-tab=post]'); pg.wait_for_selector('#drop')
    pg.set_input_files('#file', PIC); pg.wait_for_selector('#prev img')
    pg.fill('#note', 'новый босс Ногай нависает над экраном')
    # --- «Ещё дополнительно сгенерировать» ---
    check(pg.is_visible('[data-act=extragen]'), 'под фото есть кнопка «Ещё дополнительно сгенерировать»')
    pg.screenshot(path=SH + '/8a_extra_button.png')
    pg.click('[data-act=extragen]'); pg.wait_for_selector('#mo')
    check('ключ OpenAI' in pg.inner_text('#mbox'), 'без ключа OpenAI кнопка объясняет, что нужен ключ')
    pg.click('#mo'); pg.wait_for_selector('#s_OPENAI_API_KEY')
    pg.screenshot(path=SH + '/8b_conn_openai.png')
    pg.fill('#s_OPENAI_API_KEY', 'good-openai')
    pg.click('[data-keys^="OPENAI_API_KEY"]'); pg.wait_for_timeout(500)
    check(cfg.env('OPENAI_API_KEY') == 'good-openai', 'ключ OpenAI сохраняется из окна')
    pg.click('[data-tab=post]'); pg.wait_for_selector('[data-act=extragen]')
    pg.click('#x_det summary'); pg.fill('#x_idea', 'Ногай нависает над экраном, закат')
    pg.select_option('#x_n', '2')
    pg.click('[data-act=extragen]')
    pg.wait_for_selector('.gtile', timeout=30000)
    pg.wait_for_timeout(500)
    pg.screenshot(path=SH + '/8c_extra_done.png', full_page=True)
    check(pg.locator('.gtile').count() == 3, 'в списке исходное фото и 2 новые картинки GPT')
    check('Ногай нависает над экраном, закат' in ST.openai_reqs[-1][1]['prompt'], 'идея из окна дошла до GPT')
    pg.locator('[data-act=extrause]:not([disabled])').first.click(); pg.wait_for_timeout(700)
    check('gen_' in (pg.get_attribute('#prev img', 'src') or ''), 'после «В пост» вверху показана картинка GPT')
    pg.screenshot(path=SH + '/8d_extra_used.png', full_page=True)
    pg.check('#t_threads'); pg.wait_for_timeout(300)
    pg.click('[data-act=generate]'); pg.wait_for_selector('#x_tg'); pg.wait_for_selector('.card img[src*="card_"]')
    pg.wait_for_timeout(500)
    pg.screenshot(path=SH + '/8_post_generated.png', full_page=True)
    check('Тугар' in pg.input_value('#x_tg'), 'сгенерированный текст в редакторе')
    pg.fill('#x_tg', 'Мой правленый текст'); pg.wait_for_timeout(700)
    check(server.DRAFT['texts']['telegram'] == 'Мой правленый текст', 'правка текста доходит до программы')
    pg.click('[data-act=publish]'); pg.wait_for_selector('#mo')
    pg.screenshot(path=SH + '/9_confirm.png')
    pg.click('#mo'); pg.wait_for_selector('.job'); pg.wait_for_timeout(500)
    pg.screenshot(path=SH + '/10_job_running.png', full_page=True)
    pg.wait_for_selector('text=Готово', timeout=30000)
    pg.screenshot(path=SH + '/11_job_done.png', full_page=True)
    check(pg.locator('.job .ic', has_text='✅').count() >= 3, 'в итоге галочки ✅ у площадок')
    pg.set_viewport_size({'width': 760, 'height': 700}); pg.wait_for_timeout(200)
    pg.click('[data-tab=tg]'); pg.wait_for_selector('.chrow'); pg.screenshot(path=SH + '/12_narrow.png')
    b.close()
real = [e for e in errors if 'favicon' not in e]
check(not real, 'в консоли браузера нет ошибок ' + str(real[:3]))
shutil.rmtree(HOME, ignore_errors=True)
print('ИТОГО провалов:', len(FAIL))
sys.exit(1 if FAIL else 0)
