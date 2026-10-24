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
import cfg, server, jobs, net, finder, websearch
import fake_web
fake_web.install(); websearch.BLOCK_MIN = 0.05
from fake_tgu import FakeTg
from PIL import Image, ImageDraw
httpd = server.bind(0)
PORT = httpd.server_port
threading.Thread(target=httpd.serve_forever, daemon=True).start()
jobs.random_pause = lambda a, b: 0.3
finder.random_pause = lambda a, b: 0.25
SH = os.path.join(HERE, 'shots'); os.makedirs(SH, exist_ok=True)
cfg.set_settings({'ANTHROPIC_API_KEY': 'good-key', 'GAME_BOT_LINK': 'https://t.me/pustosh_bot', 'GITHUB_TOKEN': 'x', 'GITHUB_MEDIA_REPO': 'a/b',
                  'THREADS_APP_ID': 'A', 'THREADS_APP_SECRET': 'B', 'TG_API_ID': '1234567', 'TG_API_HASH': 'a' * 32})
cfg.S['threads'] = {'token': 'T', 'user_id': '777', 'username': 'kozak_dev', 'expires': cfg.now() + 50 * 86400, 'saved': cfg.now()}
cfg.save()
ST.upd_json = {'version': '1.9.0', 'zip': 'a.zip', 'notes': 'новые категории чатов', 'deps_hash': 'A'}

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
    try:
        pg.wait_for_selector('#banner', state='visible', timeout=8000)      # проверка обновления идёт в фоне, баннер появляется чуть позже
    except Exception:
        pass
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
    # --- поиск новых групп по всему Telegram + база ---
    check(pg.locator('[data-fcat]').count() == 18, 'у 18 тем слева есть галочки для поиска (у «Другое» нет)')
    cats_rail = pg.locator('#cats .cat').all_inner_texts()
    check('Взаимопиар' in cats_rail[1] and 'Делимся' in cats_rail[2] and 'Разработчики' in cats_rail[3], 'новые темы для игры стоят в самом верху списка')
    check('Для твоей игры' in pg.inner_text('#cats') and 'Другие темы' in pg.inner_text('#cats'), 'в списке есть подписи «Для твоей игры» и «Другие темы»')
    check(pg.locator('.chip').count() == 5 and pg.is_checked('[data-fcat=promo]') and not pg.is_checked('[data-fcat=games]'), 'темы для игры отмечены для поиска сразу')
    pg.screenshot(path=SH + '/4a0_hot_default.png')
    check(pg.is_visible('[data-act=findstart]') and pg.is_visible('[data-act=basesave]') and pg.is_visible('[data-act=tgload]'),
          'видны кнопки: «Найти новые чаты», «Сохранить базу» и «Загрузить чаты»')
    pg.screenshot(path=SH + '/4a_find_ui.png')
    bb = [pg.locator(x).bounding_box() for x in ('[data-act=basesave]', '[data-act=findstart]', '[data-act=tgload]')]
    check(all(x['height'] < 46 for x in bb), 'три кнопки сверху компактные (высота %s px)' % [round(x['height']) for x in bb])
    check(max(x['y'] for x in bb) - min(x['y'] for x in bb) < 6, 'три кнопки стоят в один ряд')
    gl = pg.locator('#tgleft').bounding_box(); ch = pg.locator('#chats').bounding_box()
    check(ch['x'] > gl['x'] + gl['width'] - 2 and ch['width'] > 500, 'справа отдельная панель, слева колонка с темами')
    pg.click('[data-act=fcatnone]'); pg.wait_for_timeout(200)
    pg.click('[data-act=findstart]'); pg.wait_for_timeout(300)
    check('галочки' in pg.inner_text('#toast') and pg.locator('#mo').count() == 0, 'без галочек поиск просит их поставить')
    pg.check('[data-fcat=fishing]'); pg.check('[data-fcat=games]'); pg.wait_for_timeout(200)
    check(pg.locator('.chip').count() == 2, 'выбранные темы показаны плашками сверху')
    pg.screenshot(path=SH + '/4b_find_checked.png')
    pg.click('[data-act=findstart]'); pg.wait_for_selector('#mo')
    check('23' in pg.inner_text('#mbox') and 'Рыбалка' in pg.inner_text('#mbox'), 'перед поиском показано, сколько запросов и по каким темам')
    mt = pg.inner_text('#mbox')
    check('в интернете' in mt and 'Telegram и твой аккаунт для поиска не используются' in mt and 'минут' not in mt.split('Займёт')[0], 'перед поиском сказано: ищем в интернете, Telegram и аккаунт не используются')
    check('Займёт примерно' in mt and 'Вступать в группы программа не будет' in mt, 'перед поиском написано, сколько это займёт и что программа в группы не вступает')
    pg.screenshot(path=SH + '/4b2_find_confirm.png')
    pg.click('#mo')
    pg.wait_for_selector('#findbox .bar', timeout=10000)
    pg.screenshot(path=SH + '/4c_find_running.png')
    check(pg.is_visible('[data-act=findcancel]'), 'во время поиска есть кнопка «Остановить»')
    pg.wait_for_function("document.querySelector('#findbox').innerText.includes('Слов проверено')", timeout=15000)
    ft = pg.inner_text('#findbox')
    check('Осталось примерно' in ft and 'страниц t.me проверено' in ft and 'Поисковики' in ft, 'в окне видно: сколько слов проверено, сколько страниц t.me открыто, какие поисковики работают, сколько осталось')
    check('Следующий запрос через' not in ft and 'паузa' not in ft, 'никаких долгих пауз между запросами больше нет')
    pg.screenshot(path=SH + '/4c2_find_wait.png')
    pg.wait_for_selector('[data-act=basedrop]', timeout=40000)
    check('Найденные группы' in pg.inner_text('#chats'), 'во время поиска найденные группы уже видны в правой панели')
    pg.wait_for_function("document.querySelector('#findbox').innerText.includes('Поиск закончен')", timeout=60000); pg.wait_for_timeout(700)
    pg.screenshot(path=SH + '/4d_find_base.png')
    check(pg.locator('.frow').count() == 7, 'после поиска в панели справа все найденные: 7 групп')
    check('https://t.me/ryba_ua' in pg.inner_html('#chats'), 'у групп из базы есть кнопка «Открыть» со ссылкой')
    gl0 = pg.locator('a.gl').first
    check((gl0.get_attribute('href') or '').startswith('https://t.me/') and gl0.get_attribute('target') == '_blank', 'название группы — ссылка t.me в новой вкладке')
    check(pg.locator('.onl.on').count() >= 5 and 'онлайн' in pg.inner_text('.onl.on >> nth=0'), 'у групп видно, сколько человек онлайн')
    nums = [int(x) for x in pg.locator('.onl.on b').all_inner_texts() and [t.replace('🟢', '').strip() for t in pg.locator('.onl.on b').all_inner_texts()]]
    check(nums == sorted(nums, reverse=True), 'по умолчанию сверху те, где больше онлайн: %s' % nums)
    ft = pg.inner_text('#findbox')
    check('Ссылок на t.me найдено' in ft and 'страниц проверено: 11' in ft and 'из них групп: 7' in ft, 'в итоге поиска написано: сколько ссылок найдено, сколько страниц проверено и сколько групп подошло ' + ft.replace(chr(10), ' | ')[:300])
    check(pg.inner_text('[data-act=basesave] .cnt').strip() == '7', 'кнопка «Сохранить базу» показывает, сколько новых')
    pg.select_option('#sortb', 'members'); pg.wait_for_timeout(500)
    mem = [int(x.replace('👥', '').strip()) for x in pg.locator('.frow .tag[title="Участников в группе"]').all_inner_texts()]
    check(mem == sorted(mem, reverse=True) and len(mem) == 7, 'сортировка «по участникам»: %s' % mem)
    pg.select_option('#sortb', 'online'); pg.wait_for_timeout(400)
    pg.context.grant_permissions(['clipboard-read', 'clipboard-write'])
    pg.click('[data-act=copylinks]'); pg.wait_for_function("document.querySelector('#toast').innerText.includes('Скопировано')", timeout=5000)
    try:
        clip = pg.evaluate('navigator.clipboard.readText()')
    except Exception:
        clip = ''
    check('Скопировано ссылок: 7' in pg.inner_text('#toast') and (not clip or (clip.count('https://t.me/') == 7 and 'ryba_ua' in clip)), 'кнопка «Скопировать ссылки» копирует названия и ссылки всех 7 групп')
    fake_web.reset(); n0 = len(fake_web.TME)
    pg.click('[data-act=onlrun]'); pg.wait_for_selector('#mo')
    check('Telegram и твой аккаунт для этого не используются' in pg.inner_text('#mbox'), 'перед обновлением онлайна сказано, что Telegram не используется')
    pg.click('#mo')
    pg.wait_for_function("document.querySelector('#toast').innerText.includes('Онлайн обновлён')", timeout=60000)
    check(len(fake_web.TME) - n0 >= 6 and not fake_web.SEARCHES, 'кнопка «Обновить онлайн» открыла страницы групп на t.me (%d) и не ходила в поисковики' % (len(fake_web.TME) - n0))
    nf1 = len(fake_web.TME)
    pg.click('[data-act=onlone] >> nth=0'); pg.wait_for_function("document.querySelector('#toast').innerText.includes('Онлайн обновлён')", timeout=30000)
    check(len(fake_web.TME) - nf1 == 1, 'кнопка ↻ у строки проверяет одну группу')
    pg.screenshot(path=SH + '/4d2_find_online.png')
    pg.click('[data-act=basesave]'); pg.wait_for_timeout(600)
    check(all(x['saved'] for x in cfg.S['base'].values()) and len(cfg.S['base']) == 7, 'база сохранена')
    check(pg.is_disabled('[data-act=basesave]'), 'после сохранения кнопка гаснет')
    pg.click('[data-cat=fishing]'); pg.wait_for_timeout(400)
    check(pg.locator('.frow').count() == 4, 'в базе можно смотреть по темам: «Рыбалка и охота» = 4')
    pg.screenshot(path=SH + '/4e_find_cat.png')
    pg.select_option('[data-fcatsel="w_ryba_ua"]', 'humor'); pg.wait_for_timeout(500)
    check(cfg.S['base']['w_ryba_ua']['cat'] == 'humor' and pg.locator('.frow').count() == 3, 'тему группы в базе можно поменять')
    pg.click('[data-cat=all]'); pg.wait_for_timeout(300)
    pg.select_option('#minm', '1000'); pg.wait_for_timeout(500)
    check(pg.locator('.frow').count() == 5, 'фильтр «от 1000 участников»')
    pg.select_option('#minm', '0'); pg.wait_for_timeout(400)
    pg.click('[data-act=basedrop][data-id="w_gamers_ua"]'); pg.wait_for_timeout(500)
    check('w_gamers_ua' not in cfg.S['base'], 'группу можно убрать из базы')
    pg.click('[data-act=viewmine]'); pg.wait_for_selector('[data-sel]')
    check(pg.locator('.chrow').count() == 11, 'кнопка «Мои чаты» возвращает мои 11 чатов')
    pg.click('[data-cat=all]')
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
