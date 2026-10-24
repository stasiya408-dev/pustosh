# -*- coding: utf-8 -*-
"""Маленькие помощники для запросов в интернет (только стандартная библиотека)."""
import json, urllib.request, urllib.parse, urllib.error, uuid, mimetypes


class NetError(Exception):
    def __init__(self, msg, code=0, data=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.code = code
        self.data = data


def request(method, url, headers=None, body=None, timeout=60):
    """Возвращает (код, заголовки, байты). Ошибки HTTP НЕ бросает, кроме сетевых."""
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        try:
            data = e.read()
        except Exception:
            data = b''
        return e.code, e.headers, data
    except urllib.error.URLError as e:
        raise NetError('нет связи с интернетом (%s)' % (e.reason,))
    except (TimeoutError, OSError) as e:
        raise NetError('нет связи с интернетом (%s)' % (e,))


def jload(b):
    try:
        return json.loads(b.decode('utf-8'))
    except Exception:
        return {}


def api_err(d, code):
    """Достаёт понятный текст ошибки из ответа Google/Meta/Anthropic/GitHub."""
    if isinstance(d, dict):
        e = d.get('error')
        if isinstance(e, dict):
            return e.get('message') or e.get('error_user_msg') or str(e)
        if isinstance(e, str):
            return d.get('error_description') or e
        if d.get('message'):
            return d['message']
    return 'ответ сервера %s' % code


def post_form(url, fields, timeout=60):
    body = urllib.parse.urlencode(fields).encode()
    st, h, b = request('POST', url, {'Content-Type': 'application/x-www-form-urlencoded'}, body, timeout)
    return st, jload(b)


def get_json(url, params=None, headers=None, timeout=60):
    if params:
        url += ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
    st, h, b = request('GET', url, headers, None, timeout)
    return st, jload(b)


def post_json(url, obj, headers=None, timeout=120):
    hh = {'Content-Type': 'application/json'}
    hh.update(headers or {})
    st, h, b = request('POST', url, hh, json.dumps(obj).encode('utf-8'), timeout)
    return st, jload(b), h


def multipart(fields, files):
    """fields: {имя: значение}, files: {имя: (имя_файла, путь)}"""
    bd = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        if v is None:
            continue
        if isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (bd, k, v)).encode('utf-8'))
    for k, (fname, fpath) in files.items():
        ct = mimetypes.guess_type(fname)[0] or 'application/octet-stream'
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\nContent-Type: %s\r\n\r\n' % (bd, k, fname, ct)).encode('utf-8'))
        with open(fpath, 'rb') as f:
            parts.append(f.read())
        parts.append(b'\r\n')
    parts.append(('--%s--\r\n' % bd).encode())
    return b''.join(parts), 'multipart/form-data; boundary=%s' % bd
