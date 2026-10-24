# -*- coding: utf-8 -*-
"""Категории чатов и автоматическое определение категории по названию чата."""
import re
import cfg

# (id, название, слова-подсказки). Слова ищутся как части слов; короткие — только как целые слова.
DEFAULT = [
    ('games', 'Игры', 'игр|game|gaming|геймер|gamer|steam|pubg|танки|world of tanks|wot|minecraft|майнкрафт|dota|дота|counter|cs2|cs:go|кс го|кс2|rpg|рпг|mmo|warzone|fortnite|gta|гта|playstation|xbox|консол|кіберспорт|киберспорт|esport|ігри|ігор'),
    ('tggames', 'Игры в Telegram', 'тапалк|tapalka|notcoin|hamster|хамстер|airdrop|эирдроп|аирдроп|миниапп|мини-апп|міні-апп|mini app|miniapp|p2e|play to earn|nft|\\bton\\b|тон |крипт|crypto|web3|токен'),
    ('cossacks', 'Казаки и история', 'козак|козац|казак|казач|історі|истори|history|сич|січ|гетьман|запорож|запоріж|середньовіч|средневеков|битв|битви|войн.* истории|археолог|реконструкц|рыцар|лицар|мечи|шабл|сабл|ветеран'),
    ('ukraine', 'Украина и города', 'україн|украин|ukrain|київ|киев|kyiv|kiev|харків|харьков|одес|львів|львов|дніпро|днепр|запоріж|житомир|вінниц|винниц|полтав|черкас|чернігів|чернигов|суми|сумы|херсон|миколаїв|николаев|рівне|ровно|тернопіл|луцьк|житель|жителів|мешканц|район|городск|міськ'),
    ('auto', 'Авто и мото', 'авто|auto|\\bcar\\b|cars|машин|mercedes|мерседес|\\bbmw\\b|бмв|audi|ауди|ауді|volkswagen|фольксваген|\\bvag\\b|ваг|мото|moto|байк|bike|автомех|\\bсто\\b|гараж|лада|\\bваз\\b|toyota|тойота|шин|\\bdrift|дрифт|тюнинг|тюнінг|двигател|двигун|водител|водій|водии|такси|таксі|дальнобой|фур|грузов|вантаж|ремонт авто|автозапчаст|запчаст|шиномонтаж|\\bобд\\b|obd|ecu|чип-тюнинг'),
    ('fishing', 'Рыбалка и охота', 'рыбал|рибал|fish|карп|спиннинг|спінінг|поплав|окун|щук|сазан|охот|мисливц|егер|охотник|охотничь|собаки охот|кемпинг|camp|туризм|поход|похід|выживани|виживан|bushcraft|бушкрафт|рыболов|рибалк'),
    ('weapons', 'Оружие и военное', 'оруж|зброя|зброї|страйкбол|airsoft|милитар|military|армия|армія|військ|воен|зсу|\\bвсу\\b|тактичес|тактичн|ножи|ножі|knife|пневматик|травматик|стрельб|стрільб|тир |мишень|снайпер|дрон|fpv|камуфляж|мультикам'),
    ('sport', 'Спорт и фитнес', 'футбол|football|soccer|спорт|sport|фитнес|фітнес|fitness|gym|качалк|тренаж|mma|бокс|борьб|боротьб|ufc|баскет|basket|хокей|хоккей|hockey|теннис|тенис|біг|бег |марафон|велосипед|вело|турник|воркаут|workout|кросфит|crossfit|плаван|штанг|бодибилд|ставки|ставок|беттинг|betting|букмекер'),
    ('tech', 'Техника и IT', 'айти|\\bit\\b|програм|program|python|питон|javascript|\\bjs\\b|linux|линукс|android|андроид|iphone|айфон|смартфон|гаджет|\\bпк\\b|\\bpc\\b|комп.?ютер|hardware|майнинг|mining|видеокарт|відеокарт|ноутбук|ремонт телефон|apple|xiaomi|samsung|самсунг|ai |нейросет|нейромереж|chatgpt|gpt|боти|боты|telegram|телеграм|дизайн|design|3d'),
    ('build', 'Ремонт и стройка', 'ремонт|строй|будів|будівн|электрик|електрик|сантех|дача|дачн|огород|город |сад |інструмент|инструмент|tools|строител|будівельн|отделк|оздоблен|плитк|сварк|зварюв|кровл|даховий|фундамент|теплиц|тепліц|мангал|шашлык|барбекю'),
    ('humor', 'Юмор и мемы', 'мем|meme|юмор|гумор|прикол|ржач|ржака|анекдот|fun|весел|смешн|смішн|угар|рофл|rofl|memes|мемес|pikabu|пикабу'),
    ('work', 'Работа и подработки', 'работа|робота|вакан|job|подработ|підробіт|фриланс|фрилан|freelance|заработ|заробіт|заработок|заробіток|бизнес|бізнес|business|стартап|startup|предприним|підприємц|маркетинг|marketing|продаж|sale|услуг|послуг|курьер|кур.єр|доставк'),
    ('talk', 'Общение', 'общен|спілкув|знакомств|знайомств|флирт|чат для|болтал|балака|мужск|чолові|мужчин|парн|хлопц|мужик|братв|друз|тусовк|вечеринк|клуб'),
    ('other', 'Другое', ''),
]
OTHER = 'other'
# города и «общение» встречаются почти в каждом названии, поэтому тема важнее
WEIGHT = {'ukraine': 0.5, 'talk': 0.5}

_cache = {}


def _re(cid, words):
    key = (cid, words)
    if key not in _cache:
        _cache[key] = re.compile(r'(?<!\w)(?:%s)' % words, re.I) if words else None
    return _cache[key]


def defaults():
    return [{'id': c[0], 'name': c[1], 'words': c[2]} for c in DEFAULT]


def categories():
    """Список категорий пользователя (или стандартные)."""
    c = cfg.S.get('cats')
    if not c:
        c = defaults()
        cfg.S['cats'] = c
        cfg.save()
    return c


def guess(title, username=''):
    """Возвращает id категории по названию чата."""
    t = ('%s %s' % (title or '', username or '')).lower()
    best, score = OTHER, 0
    for c in categories():
        rx = _re(c['id'], c.get('words', ''))
        if not rx:
            continue
        n = len(rx.findall(t)) * WEIGHT.get(c['id'], 1.0)
        if n > score:
            best, score = c['id'], n
    if not any(c['id'] == best for c in categories()):
        best = OTHER
    return best


def valid_id(cid):
    return any(c['id'] == cid for c in categories())


def add(name):
    name = (name or '').strip()[:40]
    if not name:
        raise ValueError('Введи название категории')
    cs = categories()
    if any(c['name'].lower() == name.lower() for c in cs):
        raise ValueError('Такая категория уже есть')
    cid = 'c%d' % cfg.now()
    cs.insert(max(0, len(cs) - 1), {'id': cid, 'name': name, 'words': ''})
    cfg.save()
    return cid


def rename(cid, name):
    name = (name or '').strip()[:40]
    if not name:
        raise ValueError('Введи название категории')
    for c in categories():
        if c['id'] == cid:
            c['name'] = name
            cfg.save()
            return
    raise ValueError('Нет такой категории')


def delete(cid):
    if cid == OTHER:
        raise ValueError('Категорию «Другое» удалить нельзя')
    cs = categories()
    cs[:] = [c for c in cs if c['id'] != cid]
    for ch in cfg.S['chats'].values():
        if ch.get('cat') == cid:
            ch['cat'] = OTHER
            ch['manual'] = False
    cfg.save()
