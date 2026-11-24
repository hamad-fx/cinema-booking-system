"""Integration tests: real HTTP endpoints + temporary SQLite database."""
import json
import os
import tempfile
import threading
import unittest
import uuid
from datetime import date, timedelta
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from cinema import db
from cinema.service import calculate_quote, ServiceError
from server import Handler, seed_admin_from_environment


class CinemaIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        db.DB_PATH = os.path.join(cls.tmp.name,'test.sqlite3')
        os.environ['DEMO_ADMIN_EMAIL']='admin@cineverse.test'
        os.environ['DEMO_ADMIN_PASSWORD']='ADMIN_TEST_PASSWORD_2026'
        db.init_db(); seed_admin_from_environment()
        cls.httpd = ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.base=f'http://127.0.0.1:{cls.httpd.server_address[1]}'
        cls.thread=threading.Thread(target=cls.httpd.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown();cls.httpd.server_close();cls.thread.join(timeout=5)
        cls.tmp.cleanup()
        os.environ.pop('DEMO_ADMIN_EMAIL',None)
        os.environ.pop('DEMO_ADMIN_PASSWORD',None)

    def setUp(self):
        with db.connect() as conn:
            conn.execute('DELETE FROM booking_snacks')
            conn.execute('DELETE FROM booking_seats')
            conn.execute('DELETE FROM bookings')
        self.cookie=''
        self.email=f'test-{uuid.uuid4().hex[:10]}@example.com'
        self.show_date=(date.today()+timedelta(days=1)).isoformat()
        shows=self.request('GET','/api/showtimes?movie_id=1')['showtimes']
        self.show=next(s for s in shows if s['show_date']==self.show_date)

    def request(self,method,path,payload=None,expect=200,cookie=None):
        headers={}
        if payload is not None:
            headers['Content-Type']='application/json'
        if cookie is not None or self.cookie:
            headers['Cookie']=self.cookie if cookie is None else cookie
        req=Request(self.base+path,method=method,headers=headers,
                    data=json.dumps(payload).encode() if payload is not None else None)
        try:
            with urlopen(req,timeout=10) as response:
                status=response.status
                result=json.load(response)
                set_cookie=response.headers.get('Set-Cookie')
                if set_cookie: self.cookie=set_cookie.split(';',1)[0]
        except HTTPError as error:
            status=error.code
            result=json.load(error)
        self.assertEqual(status,expect, f'Expected {expect}, got {status}: {result}')
        return result

    def register(self):
        return self.request('POST','/api/auth/register',{'name':'Cine Tester','email':self.email,'password':'LongPassword#123'},201)

    def test_health_and_static_site(self):
        self.assertEqual(self.request('GET','/api/health')['status'],'ok')
        with urlopen(self.base+'/') as page:
            self.assertIn(b'CINE',page.read())

    def test_movies_catalog_and_genre_filter(self):
        movies=self.request('GET','/api/movies')['movies']
        self.assertGreaterEqual(len(movies),6)
        filtered=self.request('GET','/api/movies?genre=Sci-Fi')['movies']
        self.assertTrue(all(m['genre']=='Sci-Fi' for m in filtered))
        self.assertTrue(self.request('GET','/api/movies?search=Inter')['movies'])

    def test_movie_details_and_showtimes(self):
        self.assertEqual(self.request('GET','/api/movies/1')['movie']['title'],'Interstellar')
        self.assertTrue(self.request('GET','/api/showtimes?movie_id=1')['showtimes'])
        self.assertEqual(self.request('GET',f"/api/showtimes/{self.show['id']}/seats")['occupied'],[])

    def test_authentication_and_login(self):
        self.register()
        self.assertEqual(self.request('GET','/api/me')['user']['email'],self.email)
        self.request('POST','/api/auth/logout',{})
        self.assertIsNone(self.request('GET','/api/me')['user'])
        self.request('POST','/api/auth/login',{'email':self.email,'password':'bad'},401)
        self.request('POST','/api/auth/login',{'email':self.email,'password':'LongPassword#123'})
        self.assertEqual(self.request('GET','/api/me')['user']['name'],'Cine Tester')

    def test_duplicate_user_rejected(self):
        self.register()
        self.request('POST','/api/auth/register',{'name':'Test 2','email':self.email,'password':'LongPassword#123'},409)

    def test_booking_requires_authentication(self):
        self.request('POST','/api/bookings',{'showtime_id':self.show['id'],'seats':['A1']},401)

    def test_booking_seat_lock_and_conflict(self):
        self.register()
        payload={'showtime_id':self.show['id'],'seats':['A1','A2']}
        first=self.request('POST','/api/bookings',payload,201)['booking']
        self.assertTrue(first['code'].startswith('CV-'))
        seats=self.request('GET',f"/api/showtimes/{self.show['id']}/seats")['occupied']
        self.assertEqual(set(seats),{'A1','A2'})
        self.request('POST','/api/bookings',payload,409)
        own=self.request('GET','/api/bookings')['bookings']
        self.assertEqual(len(own),1)
        self.assertEqual(set(own[0]['seats']),{'A1','A2'})

    def test_price_vip_snacks_promo(self):
        self.register()
        snack=self.request('GET','/api/snacks')['snacks'][0]
        payload={'showtime_id':self.show['id'],'seats':['A1','E1'],
                 'snacks':[{'id':snack['id'],'quantity':2}],'promo':'CINE10'}
        result=self.request('POST','/api/bookings',payload,201)['booking']
        subtotal=2*self.show['base_price']+70+2*snack['price']
        self.assertEqual(result['total'],subtotal-(subtotal*10)//100)

    def test_invalid_seats_and_promo_rejected(self):
        self.register()
        for seats in [['A1','A1'],['Z9'],[],['A0'],list('ABCDEFGHI')]:
            self.request('POST','/api/bookings',{'showtime_id':self.show['id'],'seats':seats},400)
        self.request('POST','/api/bookings',{'showtime_id':self.show['id'],'seats':['A1'],'promo':'FREE100'},400)

    def test_favorites_and_reviews(self):
        self.register()
        self.assertEqual(self.request('POST','/api/favorites/1',{})['favorite'],True)
        self.assertEqual(self.request('GET','/api/favorites')['movie_ids'],[1])
        self.assertEqual(self.request('POST','/api/favorites/1',{})['favorite'],False)
        self.request('POST','/api/reviews',{'movie_id':1,'stars':5,'comment':'Loved this movie'})
        self.assertEqual(self.request('GET','/api/movies/1')['reviews'][0]['stars'],5)

    def test_cancel_and_release_seat(self):
        self.register()
        item=self.request('POST','/api/bookings',{'showtime_id':self.show['id'],'seats':['B1']},201)['booking']
        self.request('POST',f"/api/bookings/{item['id']}/cancel",{})
        self.assertEqual(self.request('GET',f"/api/showtimes/{self.show['id']}/seats")['occupied'],[])
        self.assertEqual(self.request('GET','/api/bookings')['bookings'][0]['status'],'cancelled')

    def test_qr_ticket_requires_owner_and_returns_png(self):
        self.register()
        cookie=self.cookie
        result=self.request('POST','/api/bookings',{'showtime_id':self.show['id'],'seats':['C4']},201)
        booking_id=result['booking']['id']
        with urlopen(Request(self.base+f'/api/bookings/{booking_id}/qr',headers={'Cookie':cookie})) as qr:
            self.assertEqual(qr.headers.get('Content-Type'),'image/png')
            self.assertTrue(qr.read(8).startswith(b'\x89PNG'))
        self.request('POST','/api/auth/logout',{})
        self.request('GET',f'/api/bookings/{booking_id}/qr',expect=401)

    def test_concurrent_attempts_cannot_double_book(self):
        import concurrent.futures
        self.register()
        first_cookie=self.cookie
        other_email=f'other-{uuid.uuid4().hex[:10]}@example.com'
        self.request('POST','/api/auth/register',{'name':'Other Tester','email':other_email,'password':'LongPassword#456'},201)
        second_cookie=self.cookie
        payload=json.dumps({'showtime_id':self.show['id'],'seats':['D4']}).encode()
        def attempt(cookie):
            request=Request(self.base+'/api/bookings',data=payload,method='POST',headers={'Content-Type':'application/json','Cookie':cookie})
            try:
                with urlopen(request,timeout=10) as r: return r.status
            except HTTPError as err:
                return err.code
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results=list(executor.map(attempt,[first_cookie,second_cookie]))
        self.assertEqual(sorted(results),[201,409])

    def test_admin_authorization_and_create(self):
        self.register()
        self.request('GET','/api/admin/stats',expect=403)
        self.request('POST','/api/auth/login',{'email':'admin@cineverse.test','password':'ADMIN_TEST_PASSWORD_2026'})
        result=self.request('POST','/api/admin/movies',{'title':'New Team Feature','genre':'Drama','duration':120,'summary':'A movie written for team testing.'},201)
        mid=result['movie_id']
        self.assertTrue(any(m['id']==mid for m in self.request('GET','/api/movies')['movies']))
        show=self.request('POST','/api/admin/showtimes',{'movie_id':mid,'hall':'Hall 1','show_date':self.show_date,'show_time':'12:45','base_price':175},201)
        self.assertTrue(show['showtime_id'])
        self.assertGreaterEqual(self.request('GET','/api/admin/stats')['stats']['movies'],7)


if __name__ == '__main__':
    unittest.main()
