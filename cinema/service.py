"""Movie booking domain services (members 1–4). Server always computes prices and seat availability."""
import re
import secrets
import sqlite3
from datetime import date

from .db import connect, as_dict

SEAT_ROWS = 'ABCDEF'
SEAT_COLUMNS = range(1, 9)
VALID_SEATS = {f'{r}{c}' for r in SEAT_ROWS for c in SEAT_COLUMNS}
MAX_SEATS = 8


class ServiceError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def list_movies(search='', genre=''):
    with connect() as db:
        return [as_dict(x) for x in db.execute('''SELECT * FROM movies WHERE active=1
             AND LOWER(title) LIKE ? AND (?='' OR genre=?) ORDER BY id''',
             (f'%{search.strip().lower()}%', genre, genre))]


def list_showtimes(movie_id, requested_date=''):
    with connect() as db:
        return [as_dict(x) for x in db.execute('''SELECT s.*,m.title movie_title FROM showtimes s
            JOIN movies m ON m.id=s.movie_id WHERE s.movie_id=? AND s.active=1 AND m.active=1
            AND s.show_date>=? AND (?='' OR s.show_date=?)
            ORDER BY s.show_date,s.show_time,s.hall''',
            (movie_id, date.today().isoformat(), requested_date, requested_date))]


def get_seatmap(showtime_id):
    with connect() as db:
        row = db.execute('''SELECT s.*,m.title movie_title FROM showtimes s
          JOIN movies m ON m.id=s.movie_id WHERE s.id=? AND s.active=1''',(showtime_id,)).fetchone()
        if not row:
            raise ServiceError('Showtime not found', 404)
        occupied = [x['seat'] for x in db.execute('SELECT seat FROM booking_seats WHERE showtime_id=?',(showtime_id,))]
        return {'showtime': as_dict(row), 'occupied': occupied, 'vip_rows': ['E', 'F'], 'rows': list(SEAT_ROWS), 'columns': 8}


def calculate_quote(db, showtime_id, seats, snacks=None, promo=''):
    if not isinstance(seats, list) or not (1 <= len(seats) <= MAX_SEATS) or any(not isinstance(x, str) or x not in VALID_SEATS for x in seats) or len(set(seats)) != len(seats):
        raise ServiceError('Select 1–8 unique valid seats')
    show = db.execute('''SELECT s.* FROM showtimes s JOIN movies m ON m.id=s.movie_id
        WHERE s.id=? AND s.active=1 AND m.active=1''',(showtime_id,)).fetchone()
    if not show or show['show_date'] < date.today().isoformat():
        raise ServiceError('Showtime unavailable', 404)
    ticket_prices = {s: show['base_price'] + (70 if s[0] in 'EF' else 0) for s in seats}
    items = []
    snack_total = 0
    if snacks is None:
        snacks = []
    if not isinstance(snacks, list) or len(snacks) > 10:
        raise ServiceError('Invalid snack items')
    ids_seen = set()
    for item in snacks:
        if not isinstance(item, dict):
            raise ServiceError('Invalid snack item')
        try:
            sid, qty = int(item['id']), int(item['quantity'])
        except (KeyError, ValueError, TypeError):
            raise ServiceError('Invalid snack item')
        if sid in ids_seen or not 1 <= qty <= 10:
            raise ServiceError('Invalid snack quantity')
        ids_seen.add(sid)
        s = db.execute('SELECT * FROM snacks WHERE id=?',(sid,)).fetchone()
        if not s:
            raise ServiceError('Snack not found', 404)
        items.append({'id':sid,'quantity':qty,'price':s['price'],'name':s['name']})
        snack_total += qty * s['price']
    promo = str(promo or '').strip().upper()
    if promo not in ('','CINE10','STUDENT15'):
        raise ServiceError('Invalid promo code')
    subtotal = sum(ticket_prices.values()) + snack_total
    discount_percent = {'':0,'CINE10':10,'STUDENT15':15}[promo]
    discount = (subtotal * discount_percent) // 100
    return {'tickets':sum(ticket_prices.values()),'snacks':snack_total,'discount':discount,
            'total':subtotal-discount,'ticket_prices':ticket_prices,'snack_items':items,'promo':promo}


def create_booking(user_id, data):
    if not isinstance(data, dict):
        raise ServiceError('Invalid booking')
    try:
        showtime_id = int(data.get('showtime_id'))
    except (TypeError, ValueError):
        raise ServiceError('Choose a showtime')
    seats = data.get('seats')
    # Begin an immediate transaction to serialize bookings; UNIQUE seat keys provide a second defense.
    db = connect()
    try:
        db.execute('BEGIN IMMEDIATE')
        quote = calculate_quote(db, showtime_id, seats, data.get('snacks'), data.get('promo', ''))
        used = db.execute('SELECT seat FROM booking_seats WHERE showtime_id=?',(showtime_id,)).fetchall()
        occupied = {x['seat'] for x in used}
        if occupied.intersection(seats):
            raise ServiceError('One or more seats were just booked. Choose other seats.',409)
        guest = db.execute('SELECT name FROM users WHERE id=?',(user_id,)).fetchone()
        if not guest:
            raise ServiceError('Login required',401)
        code = 'CV-' + secrets.token_hex(5).upper()
        cur = db.execute('''INSERT INTO bookings(code,user_id,showtime_id,total,discount,promo_code,guest_name)
                           VALUES(?,?,?,?,?,?,?)''', (code,user_id,showtime_id,quote['total'],quote['discount'],quote['promo'],guest['name']))
        booking_id = cur.lastrowid
        db.executemany('INSERT INTO booking_seats(showtime_id,seat,booking_id,price) VALUES(?,?,?,?)',
                       [(showtime_id,seat,booking_id,quote['ticket_prices'][seat]) for seat in seats])
        db.executemany('INSERT INTO booking_snacks(booking_id,snack_id,quantity,price) VALUES(?,?,?,?)',
                       [(booking_id,x['id'],x['quantity'],x['price']) for x in quote['snack_items']])
        db.commit()
        return {'id':booking_id,'code':code,'total':quote['total']}
    except sqlite3.IntegrityError:
        db.rollback()
        raise ServiceError('Seats are no longer available',409)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_bookings(user_id):
    with connect() as db:
        bookings = []
        for row in db.execute('''SELECT b.*,m.title movie_title,m.emoji movie_emoji,s.show_date,s.show_time,s.hall
              FROM bookings b JOIN showtimes s ON s.id=b.showtime_id JOIN movies m ON m.id=s.movie_id
              WHERE b.user_id=? ORDER BY b.id DESC''',(user_id,)).fetchall():
            item = as_dict(row)
            item['seats'] = [x['seat'] for x in db.execute('SELECT seat FROM booking_seats WHERE booking_id=? ORDER BY seat',(item['id'],))]
            item['snack_items'] = [as_dict(x) for x in db.execute('''SELECT sn.name,bs.quantity,bs.price FROM booking_snacks bs
                 JOIN snacks sn ON sn.id=bs.snack_id WHERE bs.booking_id=?''',(item['id'],))]
            bookings.append(item)
        return bookings


def cancel_booking(user_id, booking_id):
    with connect() as db:
        row = db.execute('''SELECT b.id,b.status,s.show_date,s.show_time FROM bookings b
            JOIN showtimes s ON s.id=b.showtime_id WHERE b.id=? AND b.user_id=?''',(booking_id,user_id)).fetchone()
        if not row:
            raise ServiceError('Booking not found',404)
        if row['status'] != 'confirmed':
            raise ServiceError('Booking already cancelled')
        # Demo cancellation policy: permitted until the calendar day of the show.
        if row['show_date'] <= date.today().isoformat():
            raise ServiceError('Bookings cannot be cancelled on the show date')
        db.execute("UPDATE bookings SET status='cancelled' WHERE id=?",(booking_id,))
        db.execute('DELETE FROM booking_seats WHERE booking_id=?',(booking_id,))
        return {'cancelled':True}


def review_movie(user_id, data):
    try:
        movie_id, stars = int(data.get('movie_id')), int(data.get('stars'))
    except (TypeError, ValueError):
        raise ServiceError('Invalid movie or rating')
    comment = str(data.get('comment','')).strip()
    if not (1 <= stars <= 5) or not (3 <= len(comment) <= 500):
        raise ServiceError('Rating must be 1–5 and comment must be 3–500 characters')
    with connect() as db:
        if not db.execute('SELECT id FROM movies WHERE id=? AND active=1',(movie_id,)).fetchone():
            raise ServiceError('Movie not found',404)
        db.execute('''INSERT INTO reviews(user_id,movie_id,stars,comment) VALUES(?,?,?,?)
            ON CONFLICT(user_id,movie_id) DO UPDATE SET stars=excluded.stars,comment=excluded.comment''',
            (user_id,movie_id,stars,comment))
    return {'saved':True}
