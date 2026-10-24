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


class FakeTg:

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
