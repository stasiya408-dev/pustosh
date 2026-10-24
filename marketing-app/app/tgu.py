# -*- coding: utf-8 -*-
"""Телеграм от имени твоего аккаунта (Telethon): вход по номеру, список чатов, отправка постов."""
import asyncio, os, threading
import cfg
from cfg import env

SESSION_FILE = os.path.join(cfg.BASE, 'tg_session.txt')


class TgError(Exception):
    """kind: error | flood | peerflood | slow | forbidden | nomedia | auth"""
    def __init__(self, msg, kind='error', wait=0):
        Exception.__init__(self, msg)
        self.msg, self.kind, self.wait = msg, kind, wait


def human(sec):
    sec = int(sec or 0)
    if sec >= 3600:
        return '%d ч %d мин' % (sec // 3600, (sec % 3600) // 60)
    if sec >= 60:
        return '%d мин' % (sec // 60 + (1 if sec % 60 else 0))
    return '%d сек' % sec


NAMES = {
    'FloodWaitError': ('flood', None),
    'SlowModeWaitError': ('slow', None),
    'PeerFloodError': ('peerflood', 'Телеграм включил ограничение на рассылку (спам-лимит). Остановись на сегодня и пиши только знакомым людям.'),
    'ChatWriteForbiddenError': ('forbidden', 'В этот чат писать нельзя'),
    'UserBannedInChannelError': ('forbidden', 'Тебя заблокировали в этом чате'),
    'ChatAdminRequiredError': ('forbidden', 'Писать здесь могут только админы'),
    'ChatSendPlainForbiddenError': ('forbidden', 'В чате запрещены текстовые сообщения'),
    'ChatSendMediaForbiddenError': ('nomedia', 'В чате запрещены картинки и видео'),
    'ChatSendPhotosForbiddenError': ('nomedia', 'В чате запрещены фото'),
    'ChatSendVideosForbiddenError': ('nomedia', 'В чате запрещены видео'),
    'ChannelPrivateError': ('forbidden', 'Чат закрыт, или ты из него вышел'),
    'ChannelBannedError': ('forbidden', 'Чат заблокирован Телеграмом'),
    'MessageTooLongError': ('error', 'Текст слишком длинный'),
    'ApiIdInvalidError': ('auth', 'Телеграм не принял api_id / api_hash. Проверь, что скопировал их без пробелов (вкладка «Подключения»).'),
    'PhoneNumberInvalidError': ('auth', 'Неверный номер телефона. Пиши с кодом страны, например +380501234567.'),
    'PhoneNumberBannedError': ('auth', 'Этот номер заблокирован в Телеграме'),
    'PhoneNumberFloodError': ('auth', 'Слишком много попыток входа. Подожди немного и попробуй снова.'),
    'PhoneCodeInvalidError': ('auth', 'Неверный код. Проверь цифры из Телеграма.'),
    'PhoneCodeExpiredError': ('auth', 'Код устарел. Нажми «Войти» ещё раз и введи новый.'),
    'PhoneCodeEmptyError': ('auth', 'Введи код из Телеграма'),
    'PasswordHashInvalidError': ('auth', 'Неверный пароль двухэтапной защиты'),
    'AuthKeyUnregisteredError': ('auth', 'Вход устарел. Войди в Телеграм заново.'),
    'SessionRevokedError': ('auth', 'Вход был отозван в настройках Телеграма. Войди заново.'),
    'UserDeactivatedBanError': ('auth', 'Аккаунт заблокирован Телеграмом'),
}


def translate(e):
    """Превращает любую ошибку Telethon в понятную TgError."""
    if isinstance(e, TgError):
        return e
    n = type(e).__name__
    if n in ('TimeoutError', 'CancelledError') or 'Timeout' in n:
        return TgError('Телеграм долго не отвечает. Проверь интернет и попробуй ещё раз.')
    if n in NAMES:
        kind, text = NAMES[n]
        sec = int(getattr(e, 'seconds', 0) or 0)
        if n == 'FloodWaitError':
            return TgError('Телеграм просит подождать %s (защита от частых запросов)' % human(sec), 'flood', sec)
        if n == 'SlowModeWaitError':
            return TgError('В чате медленный режим, осталось ждать %s' % human(sec), 'slow', sec)
        return TgError(text, kind)
    if isinstance(e, (ConnectionError, OSError)):
        return TgError('Нет связи с Телеграмом. Проверь интернет.')
    m = getattr(e, 'message', None) or str(e) or n
    return TgError('Телеграм: %s' % m)


# ---------- определение «можно ли писать» ----------
def _b(rights, name):
    return bool(rights is not None and getattr(rights, name, False))


def classify(e):
    """Данные чата или None, если это не группа/канал или в них нельзя быть/писать.
    Работает по именам классов, поэтому проверяется и без Telethon."""
    n = type(e).__name__
    if n == 'Chat':                                   # обычная группа
        if getattr(e, 'deactivated', False) or getattr(e, 'left', False) or getattr(e, 'migrated_to', None):
            return None
        adm = bool(getattr(e, 'creator', False) or getattr(e, 'admin_rights', None))
        d = getattr(e, 'default_banned_rights', None)
        can = adm or not _b(d, 'send_messages')
        return {'title': e.title, 'username': '', 'kind': 'group', 'members': getattr(e, 'participants_count', None),
                'can_write': bool(can), 'slow': False, 'forum': False,
                'no_photo': bool(not adm and (_b(d, 'send_media') or _b(d, 'send_photos'))),
                'no_video': bool(not adm and (_b(d, 'send_media') or _b(d, 'send_videos')))}
    if n == 'Channel':
        if getattr(e, 'left', False):
            return None
        adm_r = getattr(e, 'admin_rights', None)
        creator = bool(getattr(e, 'creator', False))
        if getattr(e, 'broadcast', False):             # канал: писать может только админ
            can = creator or _b(adm_r, 'post_messages')
            return {'title': e.title, 'username': getattr(e, 'username', '') or '', 'kind': 'channel',
                    'members': getattr(e, 'participants_count', None), 'can_write': bool(can), 'slow': False,
                    'forum': False, 'no_photo': False, 'no_video': False}
        adm = creator or adm_r is not None
        d = getattr(e, 'default_banned_rights', None)
        me = getattr(e, 'banned_rights', None)
        can = adm or not (_b(d, 'send_messages') or _b(me, 'send_messages'))
        return {'title': e.title, 'username': getattr(e, 'username', '') or '', 'kind': 'group',
                'members': getattr(e, 'participants_count', None), 'can_write': bool(can),
                'slow': bool(getattr(e, 'slowmode_enabled', False)), 'forum': bool(getattr(e, 'forum', False)),
                'no_photo': bool(not adm and (_b(d, 'send_media') or _b(d, 'send_photos') or _b(me, 'send_media') or _b(me, 'send_photos'))),
                'no_video': bool(not adm and (_b(d, 'send_media') or _b(d, 'send_videos') or _b(me, 'send_media') or _b(me, 'send_videos')))}
    return None


def msg_link(peer_id, username, mid):
    if username:
        return 'https://t.me/%s/%s' % (username, mid)
    s = str(peer_id)
    if s.startswith('-100'):
        return 'https://t.me/c/%s/%s' % (s[4:], mid)
    return ''


class TgUser:
    """Один аккаунт Телеграма. Все вызовы Telethon идут в отдельном потоке с event loop."""

    def __init__(self):
        self.state = 'off'          # off | need_phone | need_code | need_password | ready
        self.me = ''
        self.phone = ''
        self._hash = ''
        self._client = None
        self._loop = None
        self._warm = False
        self._lock = threading.RLock()

    # ---------- служебное ----------
    def _loop_start(self):
        with self._lock:
            if self._loop is None:
                self._loop = asyncio.new_event_loop()
                threading.Thread(target=self._loop.run_forever, daemon=True, name='tg-loop').start()

    def _run(self, coro, timeout=120):
        self._loop_start()
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return fut.result(timeout)
        except Exception as e:
            raise translate(e)

    @staticmethod
    def _creds():
        api_id, api_hash = env('TG_API_ID'), env('TG_API_HASH')
        if not api_id.isdigit() or len(api_hash) < 20:
            raise TgError('Сначала впиши api_id и api_hash (вкладка «Подключения», блок Telegram)', 'auth')
        return int(api_id), api_hash

    async def _amake(self, session=''):
        try:
            from telethon import TelegramClient
            from telethon.sessions import StringSession
        except ImportError:
            raise TgError('В этой сборке нет модуля Телеграма. Скачай свежий установщик.')
        api_id, api_hash = self._creds()
        c = TelegramClient(StringSession(session), api_id, api_hash, device_model='PC', system_version='Windows',
                           app_version='1.0', lang_code='ru', system_lang_code='ru',
                           flood_sleep_threshold=0, connection_retries=3, retry_delay=2)
        c.parse_mode = None     # текст постов отправляем как есть, без разметки
        return c

    def _save_session(self):
        try:
            s = self._client.session.save()
            if s:
                with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                    f.write(s)
        except Exception:
            pass

    async def _afinish(self):
        me = await self._client.get_me()
        name = ' '.join(x for x in (getattr(me, 'first_name', ''), getattr(me, 'last_name', '')) if x)
        un = getattr(me, 'username', '')
        self.me = (name + (' @' + un if un else '')).strip() or str(getattr(me, 'id', ''))
        self.state = 'ready'
        self._warm = False
        self._save_session()

    # ---------- вход ----------
    def status(self):
        return {'state': self.state, 'me': self.me, 'phone': self.phone,
                'creds': bool(env('TG_API_ID')) and bool(env('TG_API_HASH'))}

    def start(self):
        """Тихо входит по сохранённому ключу (если он есть)."""
        if self.state == 'ready':
            return
        if not os.path.exists(SESSION_FILE):
            self.state = 'need_phone'
            return
        try:
            self._creds()
        except TgError:
            self.state = 'need_phone'
            return
        self._run(self._astart(), 60)

    async def _astart(self):
        with open(SESSION_FILE, encoding='utf-8') as f:
            sess = f.read().strip()
        c = await self._amake(sess)
        await c.connect()
        if await c.is_user_authorized():
            self._client = c
            await self._afinish()
        else:
            await c.disconnect()
            self.state = 'need_phone'

    def login_phone(self, phone):
        phone = (phone or '').strip().replace(' ', '')
        if len(phone) < 8:
            raise TgError('Введи номер телефона с кодом страны, например +380501234567', 'auth')
        self._run(self._aphone(phone), 60)

    async def _aphone(self, phone):
        if self._client is not None:
            try:
                await self._client.disconnect()
            except Exception:
                pass
        c = await self._amake('')
        await c.connect()
        r = await c.send_code_request(phone)
        self._client, self.phone, self._hash, self.state = c, phone, r.phone_code_hash, 'need_code'

    def login_code(self, code):
        code = (code or '').strip().replace(' ', '').replace('-', '')
        if not code:
            raise TgError('Введи код из Телеграма', 'auth')
        self._run(self._acode(code), 60)

    async def _acode(self, code):
        from telethon.errors import SessionPasswordNeededError
        try:
            await self._client.sign_in(self.phone, code, phone_code_hash=self._hash)
        except SessionPasswordNeededError:
            self.state = 'need_password'
            return
        await self._afinish()

    def login_password(self, pw):
        if not pw:
            raise TgError('Введи пароль двухэтапной защиты', 'auth')
        self._run(self._apass(pw), 60)

    async def _apass(self, pw):
        await self._client.sign_in(password=pw)
        await self._afinish()

    def logout(self):
        try:
            if self._client is not None:
                self._run(self._alogout(), 30)
        except TgError:
            pass
        self._client = None
        self.state, self.me = 'need_phone', ''
        try:
            os.remove(SESSION_FILE)
        except OSError:
            pass

    async def _alogout(self):
        try:
            await self._client.log_out()
        finally:
            await self._client.disconnect()

    # ---------- чаты ----------
    def load_chats(self):
        if self.state != 'ready':
            raise TgError('Сначала войди в Телеграм', 'auth')
        return self._run(self._achats(), 300)

    async def _achats(self):
        from telethon import utils
        out = []
        async for d in self._client.iter_dialogs():
            info = classify(d.entity)
            if not info:
                continue
            info['id'] = str(utils.get_peer_id(d.entity))
            info['archived'] = bool(getattr(d, 'archived', False))
            out.append(info)
        self._warm = True
        self._save_session()
        return out

    # ---------- отправка ----------
    def send(self, chat_id, text, media=None, username=''):
        """Отправляет пост в чат. media: {'kind','path','w','h','dur'} или None. Возвращает ссылку или ''."""
        if self.state != 'ready':
            raise TgError('Сначала войди в Телеграм', 'auth')
        return self._run(self._asend(int(chat_id), text, media, username), 900)

    async def _asend(self, chat_id, text, media, username):
        c = self._client
        if not self._warm:                         # без этого Telethon не знает чаты по номеру после перезапуска
            async for _ in c.iter_dialogs():
                pass
            self._warm = True
        ent = await c.get_input_entity(chat_id)
        if not media:
            m = await c.send_message(ent, text, link_preview=False)
        else:
            kw = {}
            if media['kind'] == 'video':
                from telethon.tl.types import DocumentAttributeVideo
                kw['attributes'] = [DocumentAttributeVideo(duration=int(media.get('dur') or 0), w=int(media.get('w') or 0),
                                                           h=int(media.get('h') or 0), supports_streaming=True)]
                kw['supports_streaming'] = True
            cap = text if len(text) <= 1000 else None
            m = await c.send_file(ent, media['path'], caption=cap, **kw)
            if cap is None:
                await c.send_message(ent, text, link_preview=False)
        if isinstance(m, list):
            m = m[0]
        return msg_link(chat_id, username, getattr(m, 'id', ''))

    def close(self):
        try:
            if self._client is not None and self._loop is not None:
                self._save_session()
                self._run(self._client.disconnect(), 10)
        except Exception:
            pass
