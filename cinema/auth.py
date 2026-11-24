"""Password hashing and server-side sessions; no secrets are stored in browser JS."""
import hashlib
import hmac
import secrets
import time
from http.cookies import SimpleCookie

from .db import connect, as_dict

SESSION_SECONDS = 7 * 24 * 3600


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 310_000)
    return f'{salt.hex()}:{digest.hex()}'


def verify_password(password, encoded):
    try:
        salt_hex, expected = encoded.split(':', 1)
        actual = hash_password(password, bytes.fromhex(salt_hex)).split(':', 1)[1]
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_session(db, user_id):
    token = secrets.token_urlsafe(36)
    db.execute('INSERT INTO sessions(token_hash,user_id,expires_at) VALUES(?,?,?)',
               (hashlib.sha256(token.encode()).hexdigest(), user_id, int(time.time()) + SESSION_SECONDS))
    return token


def read_token(cookie_header):
    cookie = SimpleCookie()
    try:
        cookie.load(cookie_header or '')
        return cookie['cine_session'].value if 'cine_session' in cookie else None
    except Exception:
        return None


def current_user(cookie_header):
    token = read_token(cookie_header)
    if not token:
        return None
    with connect() as db:
        user = db.execute('''SELECT u.id,u.name,u.email,u.role FROM sessions s
            JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?''',
            (hashlib.sha256(token.encode()).hexdigest(), int(time.time()))).fetchone()
        return as_dict(user)


def cookie_value(token, secure=False):
    return f'cine_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_SECONDS}' + ('; Secure' if secure else '')


def logout(cookie_header):
    token = read_token(cookie_header)
    if token:
        with connect() as db:
            db.execute('DELETE FROM sessions WHERE token_hash=?', (hashlib.sha256(token.encode()).hexdigest(),))
