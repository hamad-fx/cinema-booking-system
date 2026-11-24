# Software Requirements Specification (SRS) — CineVerse

**Version:** 1.0 working draft · **Application:** Cinema Booking System · **Team:** 5 student developers · **Date:** 2026-11-22

## 1. Purpose and Scope

CineVerse is a web-based cinema ticketing **demonstration** where customers discover movies and showtimes, select seats, add refreshments, apply promotional codes, and receive a demo confirmation. Admins manage movie/showtime data and view booking metrics. The system is intended for university assessment, not real-world cinema admissions or real payment collection.

### Actors and Roles

- **Visitor:** Browse movie catalog and showtimes; view seat availability and public movie reviews.
- **Registered Customer:** All visitor privileges plus favorites, movie reviews, seat booking, ticket history, printable QR code and cancellation (subject to policy).
- **Administrator:** Catalog/showtime creation and booking/revenue dashboard. Authentication required.

### Out of Scope (Current Implementation)

Real payment settlement/refunds, external movie licensing/catalog sync, real email/SMS dispatch, live ticket-gate verification, verified student ID discounts, admin deletion/editing, advanced accessibility audit and production-scale deployment/database persistence.

## 2. Functional Requirements

| ID | Requirement | Actor | Acceptance evidence |
|---|---|---|---|
| FR-01 | Display movie catalog and movie details | Visitor | Movie records visible and correct |
| FR-02 | Search and filter by movie title and genre | Visitor | Search returns matching cards |
| FR-03 | Show schedules with dates, times and cinema hall | Visitor | Showtime choices reflect database |
| FR-04 | Display 48 seats/show, occupied seats unavailable | Visitor | Occupied seats disabled |
| FR-05 | Select and deselect maximum 8 seats | Visitor | Selection state & summary update |
| FR-06 | Calculate standard and VIP prices on server | Customer | E/F rows +70 EGP; receipt totals correct |
| FR-07 | Select refreshment quantities | Customer | Snacks included in total and saved |
| FR-08 | Apply valid demo coupons and reject invalid | Customer | `CINE10` 10%, `STUDENT15` 15% |
| FR-09 | Register/login securely and log out | Customer/Admin | Hashed passwords; session cookies |
| FR-10 | Reject unauthenticated booking | Customer | HTTP 401 |
| FR-11 | Commit one booking atomically without double booking | Customer | HTTP 409 if seat already allocated |
| FR-12 | Display booking history per user | Customer | Only own bookings are returned |
| FR-13 | Cancel before show date, release seats | Customer | Cancelled status + seat available |
| FR-14 | Create printable ticket and QR booking code | Customer | Authenticated ticket available |
| FR-15 | Save and toggle favorite movies | Customer | Favorites list reflects saved IDs |
| FR-16 | Create or update one review per movie/user | Customer | Stars 1–5 and comment visible |
| FR-17 | Add movies and showtimes | Admin | New data appears to visitors |
| FR-18 | Review booking counts and demo revenue | Admin | Admin analytics totals shown |
| FR-19 | Prevent customer access to admin API | Backend | Returns 403 |
| FR-20 | Show meaningful errors for invalid requests | All | Validation errors surfaced in UI |

## 3. Nonfunctional Requirements

| ID | Requirement | How measured |
|---|---|---|
| NFR-01 | Responsive layout on mobile/tablet/desktop | Manual viewport tests at 375/768/1280 px |
| NFR-02 | Server-side input validation | Automated API tests with malformed JSON, seats, promo |
| NFR-03 | Preserve booking integrity under concurrent writes | SQLite immediate transaction and unique `(showtime_id, seat)` key |
| NFR-04 | Authn/authz implemented with no plaintext passwords | PBKDF2 password hash; session cookie; 401/403 tests |
| NFR-05 | Clear feedback on errors and pending actions | UI shows errors; buttons disabled during network call |
| NFR-06 | Maintainable separation of frontend modules | Feature-specific JS and backend domain modules |
| NFR-07 | Automated test pipeline on every PR to main | GitHub Actions results retained in repository |
| NFR-08 | Traceable individual contributions | Issue assignment + feature branch + PR review + commits |
| NFR-09 | Live deployment for Phase 2 | Public HTTPS URL + tests, deployment logs |
| NFR-10 | Data persistence for live system | Must be addressed with persistent disk or managed database |

## 4. Main Use Cases

**UC-01 Browse Movies**
- Primary actor: Visitor. Precondition: Server is available.
- Normal flow: Open Home → view movies → filter/search → select details.
- Alternate flow: No matches → display empty results.

**UC-02 Book Seats**
- Primary actor: Customer. Precondition: Login, valid showtime, selected valid seats.
- Normal flow: View seats → choose seats → optionally add snacks/coupon → submit → server checks prices/uniqueness → booking saved → e-ticket shown.
- Alternate 1: Another customer takes a seat → server responds HTTP 409 → user chooses other seats.
- Alternate 2: Invalid promo/seat → server rejects request with clear error.

**UC-03 Cancel Booking**
- Primary actor: Customer. Precondition: Own confirmed booking, show date in future.
- Normal flow: My Bookings → Cancel → confirm → booking status becomes cancelled → seats freed.
- Alternate: Same-day cancellation is rejected. **Payment refunds are not supported**.

**UC-04 Manage Showtimes**
- Primary actor: Admin. Precondition: Role=admin.
- Normal flow: Admin Dashboard → enter movie, hall, date, time, price → server checks inputs → new showtime visible.
- Alternate: duplicate showtime → HTTP 409.

## 5. Data Model

Tables: `users`, `sessions`, `movies`, `showtimes`, `favorites`, `reviews`, `snacks`, `bookings`, `booking_seats`, `booking_snacks`. See `cinema/db.py` and `docs/diagrams/ERD.mmd`.

Business Rules:
- Valid seat IDs are A1–F8; E and F are VIP.
- One seat may belong to at most one **active** booking in one showtime (`PRIMARY KEY(showtime_id, seat)`). Cancellation deletes the seat allocation while leaving booking history.
- A confirmed booking has one owner; other users cannot access its ticket QR or cancel it.
- Tickets are priced entirely on the backend; discounts apply to ticket+snacks subtotal.
- Booking limit is 8 seats; customer may only cancel before calendar date of show.

## 6. API Summary

| Method & Route | Description | Role |
|---|---|---|
| GET `/api/health` | health status | Public |
| GET `/api/movies`, `/api/movies/{id}` | catalog/details and reviews | Public |
| GET `/api/showtimes?movie_id=...` | schedule | Public |
| GET `/api/showtimes/{id}/seats` | seat map/occupied seats | Public |
| GET `/api/snacks` | concessions | Public |
| POST `/api/auth/register`, `/api/auth/login`, `/api/auth/logout` | authentication | Public/User |
| GET `/api/me` | current account | Public |
| GET/POST `/api/bookings` | own booking history / create booking | Customer |
| POST `/api/bookings/{id}/cancel` | cancel own booking | Customer |
| GET `/api/bookings/{id}/qr` | QR ticket for owner | Customer |
| GET `/api/favorites`, POST `/api/favorites/{id}` | favorite movie list/toggle | Customer |
| POST `/api/reviews` | save review | Customer |
| GET `/api/admin/stats` | statistics and recent bookings | Admin |
| POST `/api/admin/movies` | add movie | Admin |
| POST `/api/admin/showtimes` | add showtime | Admin |

## 7. Verification and Traceability

The automated integration suite is in `tests/test_system.py`: test names map to catalog/search, showtimes, authentication, conflict prevention, price/promo, malformed inputs, favorites/reviews, cancellation, admin authorization and HTTP health. Supplement it with manual browser scenarios from `docs/TEST_PLAN.md`; upgrade coverage in Phase 2 to negative tests, concurrency, UI integration and deployed smoke tests.

## 8. Engineering and Project Management

For each change: GitHub Issue (acceptance criteria, owner, estimate and due date) → feature branch → meaningful commits → PR referencing Issue → peer review → green CI → merge to main → update Project board. Five members, at least two complete features per member. Scrum notes and architectural diagrams are tracked as files in `docs/` and reviewed through PRs.

## 9. Assumptions, Limitations and Risks

- Sample movies are fictional/illustrative for a university demo; no agreement with cinema operator.
- Free hosted SQLite persistence may be lost on restart. This is a documented Phase 2 deployment risk requiring mitigation.
- No real payment gateway integration or money movement exists; receipt amounts are **demo values**.
- The server is educational rather than independently security-audited; additional CSRF protection, rate limiting, monitoring, migrations and backups are needed for production.
- QR codes encode unverified demo references. They do not authenticate admission or record check-ins.
