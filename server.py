"""CineVerse zero-dependency Python API and static web server.
Run: python server.py ; visit http://localhost:8000
Not intended as a hardened payment-processing production server.
"""
import hashlib
import json
import mimetypes
import os
import re
import sqlite3
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

from cinema.auth import (hash_password, verify_password, create_session,
                         current_user, cookie_value, logout)
from cinema.db import connect, init_db, as_dict
from cinema.service import (ServiceError, list_movies, list_showtimes, get_seatmap,
                            get_bookings, create_booking, cancel_booking, review_movie)

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'


def seed_admin_from_environment():
    email = os.getenv('DEMO_ADMIN_EMAIL','').strip().lower()
    password = os.getenv('DEMO_ADMIN_PASSWORD','')
    if not email or len(password) < 12:
        return
    with connect() as db:
        db.execute('''INSERT OR IGNORE INTO users(name,email,password_hash,role)
             VALUES(?,?,?,'admin')''',('Cinema Admin',email,hash_password(password)))


class Handler(BaseHTTPRequestHandler):
    server_version = 'CineVerse/1.0'

    def send_json(self, body, status=200, cookie=None):
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        if cookie is not None:
            self.send_header('Set-Cookie',cookie)
        self.end_headers()
        self.wfile.write(data)

    def respond_error(self, message, status=400):
        self.send_json({'error':message},status)

    def read_json(self):
        try:
            size = int(self.headers.get('Content-Length','0'))
        except ValueError:
            raise ServiceError('Invalid Content-Length')
        if size < 1 or size > 65536 or 'application/json' not in self.headers.get('Content-Type',''):
            raise ServiceError('Expected JSON body under 64 KB')
        try:
            payload = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeDecodeError):
            raise ServiceError('Invalid JSON')
        if not isinstance(payload, dict):
            raise ServiceError('Expected JSON object')
        return payload

    def require_user(self):
        user = current_user(self.headers.get('Cookie'))
        if not user:
            raise ServiceError('Please log in to continue',401)
        return user

    def require_admin(self):
        user = self.require_user()
        if user['role'] != 'admin':
            raise ServiceError('Administrator access required',403)
        return user

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path, params = parsed.path, parse_qs(parsed.query)
            get = lambda key, default='': params.get(key,[default])[0]
            if not path.startswith('/api/'):
                return self.static_file(path)
            if path == '/api/health':
                return self.send_json({'status':'ok'})
            if path == '/api/me':
                return self.send_json({'user':current_user(self.headers.get('Cookie'))})
            if path == '/api/movies':
                return self.send_json({'movies':list_movies(get('search'),get('genre'))})
            if re.fullmatch(r'/api/movies/\d+',path):
                mid = int(path.rsplit('/',1)[1])
                with connect() as db:
                    movie = db.execute('SELECT * FROM movies WHERE id=? AND active=1',(mid,)).fetchone()
                    if not movie:
                        raise ServiceError('Movie not found',404)
                    reviews = [as_dict(r) for r in db.execute('''SELECT r.stars,r.comment,r.created_at,u.name
                      FROM reviews r JOIN users u ON u.id=r.user_id WHERE r.movie_id=? ORDER BY r.id DESC LIMIT 20''',(mid,))]
                return self.send_json({'movie':as_dict(movie),'reviews':reviews})
            if path == '/api/showtimes':
                try: mid = int(get('movie_id'))
                except ValueError: raise ServiceError('Choose a movie')
                return self.send_json({'showtimes':list_showtimes(mid,get('date'))})
            if re.fullmatch(r'/api/showtimes/\d+/seats',path):
                sid = int(path.split('/')[3])
                return self.send_json(get_seatmap(sid))
            if path == '/api/snacks':
                with connect() as db:
                    snacks = [as_dict(r) for r in db.execute('SELECT * FROM snacks ORDER BY id')]
                return self.send_json({'snacks':snacks})
            if path == '/api/bookings':
                user = self.require_user()
                return self.send_json({'bookings':get_bookings(user['id'])})
            if re.fullmatch(r'/api/bookings/\d+/qr',path):
                user = self.require_user()
                booking_id = int(path.split('/')[3])
                with connect() as db:
                    ticket = db.execute("SELECT code FROM bookings WHERE id=? AND user_id=? AND status='confirmed'",
                                        (booking_id,user['id'])).fetchone()
                if not ticket:
                    raise ServiceError('Active ticket not found',404)
                try:
                    from io import BytesIO
                    import qrcode
                    qr = qrcode.make('CINEVERSE DEMO TICKET: ' + ticket['code'])
                    stream = BytesIO()
                    qr.save(stream, format='PNG')
                    content = stream.getvalue()
                except ImportError:
                    raise ServiceError('QR generator is not installed',503)
                self.send_response(200)
                self.send_header('Content-Type','image/png')
                self.send_header('Content-Length',str(len(content)))
                self.send_header('Cache-Control','private, no-store')
                self.send_header('X-Content-Type-Options','nosniff')
                self.end_headers()
                self.wfile.write(content)
                return
            if path == '/api/favorites':
                user = self.require_user()
                with connect() as db:
                    ids = [r['movie_id'] for r in db.execute('SELECT movie_id FROM favorites WHERE user_id=?',(user['id'],))]
                return self.send_json({'movie_ids':ids})
            if path == '/api/admin/stats':
                self.require_admin()
                with connect() as db:
                    stats = {
                      'movies':db.execute('SELECT COUNT(*) n FROM movies WHERE active=1').fetchone()['n'],
                      'shows':db.execute('SELECT COUNT(*) n FROM showtimes WHERE active=1').fetchone()['n'],
                      'bookings':db.execute("SELECT COUNT(*) n FROM bookings WHERE status='confirmed'").fetchone()['n'],
                      'revenue':db.execute("SELECT COALESCE(SUM(total),0) n FROM bookings WHERE status='confirmed'").fetchone()['n'],
                    }
                    recent = [as_dict(r) for r in db.execute('''SELECT b.code,b.total,b.status,m.title movie_title,u.email
                          FROM bookings b JOIN showtimes s ON s.id=b.showtime_id
                          JOIN movies m ON m.id=s.movie_id JOIN users u ON u.id=b.user_id ORDER BY b.id DESC LIMIT 12''')]
                return self.send_json({'stats':stats,'recent':recent})
            raise ServiceError('API endpoint not found',404)
        except ServiceError as ex:
            self.respond_error(str(ex),ex.status)
        except (ValueError,TypeError):
            self.respond_error('Invalid request')
        except Exception as ex:
            print('SERVER ERROR:',repr(ex),file=sys.stderr)
            self.respond_error('Internal server error',500)

    def do_POST(self):
        try:
            path = urlparse(self.path).path
            # Same-origin JSON POSTs; reject explicit mismatched Origin headers.
            origin = self.headers.get('Origin','')
            if origin and urlparse(origin).netloc != self.headers.get('Host',''):
                raise ServiceError('Cross-origin request blocked',403)
            data = self.read_json()
            secure_cookie = os.environ.get('COOKIE_SECURE','0') == '1'
            if path == '/api/auth/register':
                name = str(data.get('name','')).strip()
                email = str(data.get('email','')).strip().lower()
                password = data.get('password','')
                if not isinstance(password,str) or not (2 <= len(name) <= 80) or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email) or len(email)>180 or len(password)<8 or len(password)>128:
                    raise ServiceError('Use valid name, email, and a password of 8–128 characters')
                with connect() as db:
                    try:
                        cur=db.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)',(name,email,hash_password(password)))
                    except sqlite3.IntegrityError:
                        raise ServiceError('Email is already registered',409)
                    token=create_session(db,cur.lastrowid)
                return self.send_json({'user':{'id':cur.lastrowid,'name':name,'email':email,'role':'customer'}},201,cookie_value(token,secure_cookie))
            if path == '/api/auth/login':
                email = str(data.get('email','')).strip().lower()
                password = data.get('password','')
                with connect() as db:
                    user=db.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
                    if not user or not isinstance(password,str) or not verify_password(password,user['password_hash']):
                        raise ServiceError('Invalid email or password',401)
                    token=create_session(db,user['id'])
                return self.send_json({'user':{'id':user['id'],'name':user['name'],'email':email,'role':user['role']}},cookie=cookie_value(token,secure_cookie))
            if path == '/api/auth/logout':
                logout(self.headers.get('Cookie'))
                return self.send_json({'logged_out':True},cookie='cine_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0' + ('; Secure' if secure_cookie else ''))
            if path == '/api/bookings':
                user=self.require_user()
                return self.send_json({'booking':create_booking(user['id'],data)},201)
            if re.fullmatch(r'/api/bookings/\d+/cancel',path):
                user=self.require_user()
                bid=int(path.split('/')[3])
                return self.send_json(cancel_booking(user['id'],bid))
            if re.fullmatch(r'/api/favorites/\d+',path):
                user=self.require_user()
                mid=int(path.rsplit('/',1)[1])
                with connect() as db:
                    if not db.execute('SELECT 1 FROM movies WHERE id=? AND active=1',(mid,)).fetchone():
                        raise ServiceError('Movie not found',404)
                    exists=db.execute('SELECT 1 FROM favorites WHERE user_id=? AND movie_id=?',(user['id'],mid)).fetchone()
                    if exists: db.execute('DELETE FROM favorites WHERE user_id=? AND movie_id=?',(user['id'],mid))
                    else: db.execute('INSERT INTO favorites(user_id,movie_id) VALUES(?,?)',(user['id'],mid))
                return self.send_json({'favorite':not bool(exists)})
            if path == '/api/reviews':
                user=self.require_user()
                return self.send_json(review_movie(user['id'],data))
            if path == '/api/admin/movies':
                self.require_admin()
                title=str(data.get('title','')).strip()
                genre=str(data.get('genre','')).strip()
                summary=str(data.get('summary','')).strip()
                try: duration=int(data.get('duration')); price_unused=0
                except (ValueError,TypeError): raise ServiceError('Invalid duration')
                if not(2<=len(title)<=100 and 3<=len(genre)<=40 and 5<=len(summary)<=1000 and 30<=duration<=300):
                    raise ServiceError('Enter a valid title, genre, duration and summary')
                with connect() as db:
                    cur=db.execute('''INSERT INTO movies(title,genre,duration,rating,summary,emoji,accent)
                          VALUES(?,?,?,'NR',?,'🎞️','#67416f')''',(title,genre,duration,summary))
                return self.send_json({'movie_id':cur.lastrowid},201)
            if path == '/api/admin/showtimes':
                self.require_admin()
                try: mid=int(data.get('movie_id')); price=int(data.get('base_price'))
                except (ValueError,TypeError): raise ServiceError('Invalid movie ID or price')
                hall=str(data.get('hall','')).strip()
                day=str(data.get('show_date','')).strip()
                clock=str(data.get('show_time','')).strip()
                if hall not in ('Hall 1','Hall 2','IMAX') or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',day) or not re.fullmatch(r'([01]\d|2[0-3]):[0-5]\d',clock) or day < date.today().isoformat() or not (50<=price<=1000):
                    raise ServiceError('Invalid showtime details')
                with connect() as db:
                    if not db.execute('SELECT 1 FROM movies WHERE id=? AND active=1',(mid,)).fetchone():
                        raise ServiceError('Movie not found',404)
                    try:
                        cur=db.execute('''INSERT INTO showtimes(movie_id,hall,show_date,show_time,base_price)
                            VALUES(?,?,?,?,?)''',(mid,hall,day,clock,price))
                    except sqlite3.IntegrityError:
                        raise ServiceError('This showtime already exists',409)
                return self.send_json({'showtime_id':cur.lastrowid},201)
            raise ServiceError('API endpoint not found',404)
        except ServiceError as ex:
            self.respond_error(str(ex),ex.status)
        except (ValueError, TypeError):
            self.respond_error('Invalid request')
        except Exception as ex:
            print('SERVER ERROR:',repr(ex),file=sys.stderr)
            self.respond_error('Internal server error',500)

    def static_file(self, url_path):
        route = '/index.html' if url_path in ('','/') else unquote(url_path)
        resolved = (PUBLIC / route.lstrip('/')).resolve()
        if not resolved.is_relative_to(PUBLIC.resolve()) or not resolved.is_file():
            self.send_error(404,'Not found')
            return
        mimetype = mimetypes.guess_type(str(resolved))[0] or 'application/octet-stream'
        data = resolved.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type',mimetype + ('; charset=utf-8' if mimetype.startswith('text/') or mimetype=='application/javascript' else ''))
        self.send_header('Content-Length',str(len(data)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; script-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)


def run():
    init_db()
    seed_admin_from_environment()
    port=int(os.environ.get('PORT','8000'))
    server=ThreadingHTTPServer(('0.0.0.0',port),Handler)
    print(f'CineVerse running at http://localhost:{port}')
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__=='__main__':
    run()
