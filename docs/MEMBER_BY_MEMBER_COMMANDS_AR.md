# أوامر Git الجاهزة لكل Member — اكتبها فين؟

**كل الأوامر دي في VS Code → Terminal → New Terminal أو Git Bash**، وإنت واقف داخل فولدر `Cinema-Booking-System`. **أوامر Browser UI زي Issue / PR / Project Board تتعمل على github.com وليس داخل Terminal.**

كل واحد ينفذ مرة واحدة أول ما يبدأ بعد ما Repo Owner يضيفه Collaborator:

```bash
git clone https://github.com/OWNER_USERNAME/Cinema-Booking-System.git
cd Cinema-Booking-System
git config user.name "YOUR OWN NAME"
git config user.email "YOUR OWN GITHUB EMAIL"
```

## Member 1 — Movie Catalog + Favorites/Reviews

**Coding:** `public/js/catalog.js`, parts of `public/js/showtimes.js`, styles. Own Issues F01 and F02.

**Phase 1 first feature:**

```bash
git checkout main
git pull origin main
git switch -c feature/movie-catalog
# Open VS Code Explorer and implement catalog.js + styles
python -m unittest discover -s tests -v
git add public/js/catalog.js public/css/style.css
git commit -m "feat: implement searchable movie catalog"
git push -u origin feature/movie-catalog
```

**On GitHub:** New PR base main, link **real F01 issue number**, request review **Member 2**. After approved/merged, pull main and delete branch.

**Phase 2 second feature:** `feature/favorites-reviews`. Implement user-specific Favorites and movie ratings, add tests, commit `feat: add movie favorites and customer reviews`, push and open a separate PR for F02. Review Member 5's PR.

## Member 2 — Showtimes + Admin Programming

**Coding:** `public/js/showtimes.js`, `public/js/admin.js`, related API validation.

```bash
git checkout main
git pull origin main
git switch -c feature/movie-showtimes
# Implement details and date/time/hall logic in VS Code
python -m unittest discover -s tests -v
git add public/js/showtimes.js
git commit -m "feat: add movie details and showtime selection"
git push -u origin feature/movie-showtimes
```

**On GitHub:** PR linked to F03, request review Member 3. Second feature in Phase 2: branch `feature/admin-programming`, create admin movie/showtime forms + backend validation, test, PR linked to F04. Review Member 1's PR. **Maintain backlog and estimate fields**.

## Member 3 — Seat Selection + Server Seat Locking

**Coding:** `public/js/seats.js`, `cinema/service.py`, seat-locking tests.

```bash
git checkout main
git pull origin main
git switch -c feature/seat-selection
# Implement 48-seat interactive map in VS Code
python -m unittest discover -s tests -v
git add public/js/seats.js public/css/style.css
git commit -m "feat: build interactive seat selection grid"
git push -u origin feature/seat-selection
```

**On GitHub:** PR linked to F05, review by Member 4. Phase 2: branch `feature/vip-seat-locking`, implement row pricing and backend prevention of duplicate allocation; add concurrency tests. Commit `feat: enforce VIP pricing and atomic seat reservations`. Review Member 2's PR.

## Member 4 — Booking Flow + Cancellations/Snacks/Promos

**Coding:** `public/js/booking.js`, booking service, booking/history tests.

```bash
git checkout main
git pull origin main
git switch -c feature/booking-flow
# Implement confirmation and My Bookings; save on server
python -m unittest discover -s tests -v
git add public/js/booking.js cinema/service.py
git commit -m "feat: save confirmed bookings and show reservation history"
git push -u origin feature/booking-flow
```

**On GitHub:** PR linked to F07, review by Member 5. Phase 2 branch `feature/cancel-snacks-promos`, implement cancellation policy, refreshment quantities and promo validation with tests, link F08. Review Member 3's PR. **Own milestone deadlines**.

## Member 5 — Authentication + Analytics/Testing/DevOps

**Coding:** `cinema/auth.py`, `server.py`, `public/js/account.js`, `public/js/admin.js`, `tests/test_system.py`, `.github/workflows/ci-cd.yml`.

```bash
git checkout main
git pull origin main
git switch -c feature/user-authentication
# Implement registration/login with session cookies in VS Code
python -m unittest discover -s tests -v
git add cinema/auth.py server.py public/js/account.js
git commit -m "feat: add secure registration and login sessions"
git push -u origin feature/user-authentication
```

**On GitHub:** PR linked to F09, reviewed by Member 1. Phase 2 branch `feature/analytics-ci-cd`: implement admin analytics, expand tests and CI/CD (this can be broken into more branches/issues), add evidence of successful runs and deployment. Commit `feat: add admin dashboard metrics` and `ci: run integration tests before Render deploy`. Review Member 4's PR.

## Every member after their PR is merged

```bash
git checkout main
git pull origin main
git status
```

Then create a **fresh** new branch for the next feature. If you need to fix bugs:

```bash
git checkout main
git pull origin main
git switch -c fix/clear-bug-name
# Fix and test genuinely
git add path/to/file
git commit -m "fix: describe actual bug solved"
git push -u origin fix/clear-bug-name
```

Create a **Bug Issue** and a **Pull Request** linked to it. The reviewer must not be the PR author.

## How to check everyone's contribution on GitHub

- Repo → **Insights → Contributors** (may lag) / Commits history.
- Repo → **Pull requests** → filter by author.
- Repo → **Issues** → filter by assignee.
- GitHub Project → group by assignee / status.
- Repo → **Actions** → CI runs and logs.

There is no Git command that retroactively proves work a member did not do. The source code, understandable commits, reviews, and working test cases should tell the same authentic story.
