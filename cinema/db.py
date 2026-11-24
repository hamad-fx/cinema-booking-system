"""SQLite schema and sample data. Member 4 owns bookings; Member 5 maintains schema migrations."""
import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = os.environ.get('DATABASE_PATH', str(Path(__file__).resolve().parent.parent / 'cinema.sqlite3'))


class ManagedConnection(sqlite3.Connection):
    """Close SQLite connections automatically after `with connect()`."""
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def connect():
    conn = sqlite3.connect(DB_PATH, timeout=20, factory=ManagedConnection)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA busy_timeout=20000')
    return conn


def init_db():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'customer'
        );
        CREATE TABLE IF NOT EXISTS sessions (
          token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          expires_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS movies (
          id INTEGER PRIMARY KEY, title TEXT NOT NULL, genre TEXT NOT NULL,
          duration INTEGER NOT NULL, rating TEXT NOT NULL DEFAULT 'NR',
          summary TEXT NOT NULL, emoji TEXT NOT NULL DEFAULT '🎬', accent TEXT NOT NULL DEFAULT '#9f345c',
          active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS showtimes (
          id INTEGER PRIMARY KEY, movie_id INTEGER NOT NULL REFERENCES movies(id),
          hall TEXT NOT NULL, show_date TEXT NOT NULL, show_time TEXT NOT NULL,
          base_price INTEGER NOT NULL, active INTEGER NOT NULL DEFAULT 1,
          UNIQUE(movie_id,hall,show_date,show_time)
        );
        CREATE TABLE IF NOT EXISTS favorites (
          user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
          movie_id INTEGER NOT NULL REFERENCES movies(id), PRIMARY KEY(user_id,movie_id)
        );
        CREATE TABLE IF NOT EXISTS reviews (
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
          movie_id INTEGER NOT NULL REFERENCES movies(id), stars INTEGER NOT NULL CHECK(stars BETWEEN 1 AND 5),
          comment TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(user_id,movie_id)
        );
        CREATE TABLE IF NOT EXISTS snacks (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL, emoji TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS bookings (
          id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE,
          user_id INTEGER NOT NULL REFERENCES users(id),
          showtime_id INTEGER NOT NULL REFERENCES showtimes(id),
          status TEXT NOT NULL DEFAULT 'confirmed',
          total INTEGER NOT NULL, discount INTEGER NOT NULL DEFAULT 0,
          promo_code TEXT, guest_name TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS booking_seats (
          showtime_id INTEGER NOT NULL REFERENCES showtimes(id), seat TEXT NOT NULL,
          booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
          price INTEGER NOT NULL, PRIMARY KEY(showtime_id,seat)
        );
        CREATE TABLE IF NOT EXISTS booking_snacks (
          booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
          snack_id INTEGER NOT NULL REFERENCES snacks(id), quantity INTEGER NOT NULL, price INTEGER NOT NULL,
          PRIMARY KEY(booking_id,snack_id)
        );
        ''')
        if not db.execute('SELECT 1 FROM movies LIMIT 1').fetchone():
            db.executemany('''INSERT INTO movies(title,genre,duration,rating,summary,emoji,accent)
                VALUES(?,?,?,?,?,?,?)''', [
                ('Interstellar','Sci-Fi',169,'8.7','Explorers travel beyond the stars to seek a future for humanity.','🌌','#304b83'),
                ('The Dark Knight','Action',152,'9.0','A masked hero faces a criminal mastermind in a troubled city.','🦇','#293e67'),
                ('Inception','Sci-Fi',148,'8.8','A skilled team enters dreams to perform an impossible mission.','🌀','#70446b'),
                ('The Grand Adventure','Animation',103,'8.1','A colorful quest filled with friendship, magic and surprises.','🐉','#98624d'),
                ('Midnight Signal','Thriller',118,'7.9','A mysterious signal leads to an unforgettable discovery.','📡','#416d66'),
                ('The Last Encore','Drama',122,'8.2','A musician takes one last chance to make a new beginning.','🎼','#885671')
            ])
        if not db.execute('SELECT 1 FROM snacks LIMIT 1').fetchone():
            db.executemany('INSERT INTO snacks(name,price,emoji) VALUES(?,?,?)', [
                ('Popcorn',70,'🍿'),('Cola',40,'🥤'),('Nachos',85,'🧀'),('Water',25,'💧')])
        # Sample showtimes are continually available for the next few days, including after a restart.
        for offset in range(0, 10):
            day = (date.today() + timedelta(days=offset)).isoformat()
            for movie_id in (1, 2, 3, 4, 5, 6):
                for hall, clock, price in [('Hall 1','15:00',120), ('Hall 2','19:30',150), ('IMAX','22:30',190)]:
                    db.execute('''INSERT OR IGNORE INTO showtimes(movie_id,hall,show_date,show_time,base_price)
                        VALUES(?,?,?,?,?)''',(movie_id,hall,day,clock,price))


def as_dict(row):
    return dict(row) if row is not None else None
