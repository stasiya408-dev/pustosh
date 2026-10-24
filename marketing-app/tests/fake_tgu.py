# -*- coding: utf-8 -*-
"""Подставной «Телеграм-аккаунт» для тестов (та же форма, что у app/tgu.TgUser)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))
import tgu
from cfg import env


def C(id, title, kind='group', can=True, user='', members=100, slow=False, forum=False, no_photo=False, no_video=False, archived=False):
    return {'id': str(id), 'title': title, 'kind': kind, 'can_write': can, 'username': user, 'members': members, 'slow': slow,
            'forum': forum, 'no_photo': no_photo, 'no_video': no_video, 'archived': archived}


CHATS = [
    C(-1001, 'Рыбалка Киев — клуб'), C(-1002, 'Автомеханики Украины', user='autoua'), C(-1003, 'Танки онлайн WoT', no_photo=True),
    C(-1004, 'Новости игр', 'channel', can=False), C(-1005, 'Козацька історія', slow=True), C(-1006, 'Пустошь — новости', 'channel', user='pustosh_news'),
    C(-1007, 'Мемы и приколы'), C(-1008, 'Закрытая группа', can=False), C(-1009, 'Футбол УПЛ'), C(-1010, 'Флуд-чат'),
    C(-1011, 'Запрещённый чат'), C(-1012, 'Охота и рыбалка'), C(-1013, 'Разное общение'),
]


def F(id, title, user, members=500, join_request=False, slow=False, forum=False):
    return {'id': str(id), 'title': title, 'username': user, 'kind': 'group', 'members': members, 'join_request': join_request, 'slow': slow, 'forum': forum,
            'cid': abs(int(id)), 'hash': 7000 + abs(int(id)) % 1000}


# что «находит» поддельный глобальный поиск по слову (-1001 и -1002 уже есть у пользователя, их в базу попадать не должно)
FOUND = {
    'рыбалка': [F(-100500001, 'Рыбалка Украина', 'ryba_ua', 5400), F(-1001, 'Рыбалка Киев — клуб', 'ryba_kiev', 900), F(-100500002, 'Спиннинг для всех', 'spin_all', 1200, slow=True)],
    'рибалка': [F(-100500001, 'Рыбалка Украина', 'ryba_ua', 5500), F(-100500003, 'Рибалки Львова', 'lviv_fish', 80, join_request=True)],
    'охота': [F(-100500004, 'Охота и егеря', 'hunt_chat', 2300)],
    'игры': [F(-100500005, 'Танки и не только', 'tanks_chat', 15000), F(-100500006, 'Мемы про игры', 'memes_games', 700)],
    'геймеры': [F(-100500007, 'Геймеры Украины', 'gamers_ua', 3000, forum=True)],
    'автомеханики': [F(-1002, 'Автомеханики Украины', 'autoua', 4000)],
}


class FakeTg:
    searches = []           # общий журнал запросов поиска (по всем экземплярам)
    search_flood_at = 0     # с какого по счёту запроса бросать FloodWait (0 = никогда)
    search_fail = ()        # слова, на которые поиск отвечает ошибкой
    fulls = []              # id групп, для которых спрашивали онлайн
    full_flood_at = 0       # с какого по счёту запроса онлайна бросать FloodWait (0 = никогда)
    last_raw = 0

    def __init__(self):
        self.state = 'need_phone'
        self.me = ''
        self.phone = ''
        self.sent = []          # (chat_id, text, media_kind)
        self.loads = 0

    def status(self):
        return {'state': self.state, 'me': self.me, 'phone': self.phone, 'creds': bool(env('TG_API_ID')) and bool(env('TG_API_HASH'))}

    def start(self):
        pass

    def login_phone(self, phone):
        if phone.startswith('+000'):
            raise tgu.TgError('Неверный номер телефона. Пиши с кодом страны, например +380501234567.', 'auth')
        self.phone, self.state = phone, 'need_code'

    def login_code(self, code):
        if code == '00000':
            raise tgu.TgError('Неверный код. Проверь цифры из Телеграма.', 'auth')
        self.state = 'need_password' if code == '99999' else 'ready'
        if self.state == 'ready':
            self.me = 'Тест Тестович @tester'

    def login_password(self, pw):
        if pw != 'secret':
            raise tgu.TgError('Неверный пароль двухэтапной защиты', 'auth')
        self.state, self.me = 'ready', 'Тест Тестович @tester'

    def logout(self):
        self.state, self.me = 'need_phone', ''

    def load_chats(self):
        self.loads += 1
        return [dict(c) for c in CHATS]

    def search(self, query, limit=100):
        if self.state != 'ready':
            raise tgu.TgError('Сначала войди в Телеграм', 'auth')
        FakeTg.searches.append(query)
        if FakeTg.search_flood_at and len(FakeTg.searches) >= FakeTg.search_flood_at:
            raise tgu.TgError('Телеграм просит подождать 5 мин (защита от частых запросов)', 'flood', 300)
        if query in FakeTg.search_fail:
            raise tgu.TgError('Не получилось выполнить запрос', 'error')
        found = [dict(x) for x in FOUND.get(query, [])]
        self.last_raw = len(found) + 3           # плюс несколько каналов и чужих чатов, которые отбросились
        return found

    def full(self, chat_id, cid=None, access_hash=None):
        if self.state != 'ready':
            raise tgu.TgError('Сначала войди в Телеграм', 'auth')
        FakeTg.fulls.append(str(chat_id))
        if FakeTg.full_flood_at and len(FakeTg.fulls) >= FakeTg.full_flood_at:
            raise tgu.TgError('Телеграм просит подождать 1 мин (защита от частых запросов)', 'flood', 60)
        if str(chat_id) == '-100500007':
            raise tgu.TgError('Группа недоступна (удалена или закрыта)', 'forbidden')
        for lst in FOUND.values():
            for x in lst:
                if x['id'] == str(chat_id):
                    n = len(FakeTg.fulls)
                    return {'online': x['members'] // 25 + n % 3, 'members': x['members'] + 1, 'about': 'Описание: ' + x['title']}
        return {'online': None, 'members': None, 'about': ''}

    def send(self, chat_id, text, media=None, username=''):
        cid = int(chat_id)
        if cid == -1010:
            raise tgu.TgError('Телеграм просит подождать 5 мин (защита от частых запросов)', 'flood', 300)
        if cid == -1011:
            raise tgu.TgError('В этот чат писать нельзя', 'forbidden')
        if cid == -1009 and media and not getattr(self, 'nomedia_done', False):
            self.nomedia_done = True
            raise tgu.TgError('В чате запрещены картинки и видео', 'nomedia')
        self.sent.append((cid, text, media['kind'] if media else None))
        return ('https://t.me/%s/%d' % (username, 100 + len(self.sent))) if username else ''

    def close(self):
        pass
