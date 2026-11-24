# Five-member ownership, issues, branches and delivery plan

> Replace Member 1–5 with real GitHub usernames in GitHub Issues and Projects. Issue numbers are assigned by GitHub, **not** by this template. Tasks below are a *plan*, not completed work.

## Work distribution — ten independently reviewable features

| Owner | Feature ID | Feature and code ownership | Primary files | Branch | Phase / estimated effort |
|---|---|---|---|---|---|
| Member 1 | F01 | Movie catalog: list, search, filters, responsive cards | `public/js/catalog.js`, `public/css/style.css` | `feature/movie-catalog` | P1, 6h |
| Member 1 | F02 | Favorites and review UI / API work | `public/js/catalog.js`, `public/js/showtimes.js`, `cinema/service.py` | `feature/favorites-reviews` | P2, 7h |
| Member 2 | F03 | Movie details, date/time/hall showtimes | `public/js/showtimes.js`, `cinema/db.py` | `feature/movie-showtimes` | P1, 7h |
| Member 2 | F04 | Admin create movies and scheduled shows; validation | `public/js/admin.js`, `server.py` | `feature/admin-programming` | P2, 7h |
| Member 3 | F05 | Interactive 48-seat UI / select/deselect | `public/js/seats.js`, `public/css/style.css` | `feature/seat-selection` | P1, 7h |
| Member 3 | F06 | VIP pricing, backend seat-conflict transaction and tests | `cinema/service.py`, `tests/test_system.py` | `feature/vip-seat-locking` | P2, 8h |
| Member 4 | F07 | Checkout, confirmation, booking history | `public/js/booking.js`, `cinema/service.py` | `feature/booking-flow` | P1, 8h |
| Member 4 | F08 | Cancel booking, snacks, promo discounts and tests | `public/js/booking.js`, `cinema/service.py` | `feature/cancel-snacks-promos` | P2, 8h |
| Member 5 | F09 | Signup, login, auth/session validation | `public/js/account.js`, `cinema/auth.py`, `server.py` | `feature/user-authentication` | P1, 8h |
| Member 5 | F10 | Admin analytics, advanced integration tests and CI/CD | `public/js/admin.js`, `tests/test_system.py`, `.github/workflows/ci-cd.yml` | `feature/analytics-ci-cd` | P2, 8h |

**Critical:** Before claiming a feature, a member must create meaningful code changes and tests in their own branch. The full ZIP is a **reference implementation**. Simply copying the entire ZIP into `main` and making superficial edits from 5 accounts is **not** evidence of five independent contributions. Use the starter scaffold (separate ZIP) and build feature-by-feature from this reference, or take meaningful independently engineered enhancements beyond it.

## Who does GitHub management? Everyone — with additional leads

| Member | Project management responsibility | PR review partner |
|---|---|---|
| 1 | Create repository and project, maintain README and Demo Checklist | Reviews Member 5 |
| 2 | Draft feature issues and acceptance criteria; maintain project backlog | Reviews Member 1 |
| 3 | Review branch hygiene and code-quality/seat bug issues | Reviews Member 2 |
| 4 | Manage milestone dates, time estimates and daily board updates | Reviews Member 3 |
| 5 | Own CI/CD config, testing reports and release readiness | Reviews Member 4 |

**Every single member also must:** create/update issues, set status, implement code, write clear commits, open 2+ PRs (one per feature), review a different member's PR, discuss changes on PRs, and participate in Scrum notes.

## Phase 1 tasks (target: before Nov 28 evaluation)

| Priority | Task | Owner | Due | Status initially |
|---|---|---|---|---|
| P0 | Create repo, invite collaborators, establish issue/PR templates | 1 + all | Nov 22 | Todo |
| P0 | Create GitHub Project board, issue labels, fields, milestone | 2 + all | Nov 22 | Todo |
| P1 | F01 Movie Catalog | 1 | Nov 24 | Todo |
| P1 | F03 Details/Showtimes | 2 | Nov 25 | Todo |
| P1 | F05 Seat Selection | 3 | Nov 25 | Todo |
| P1 | F07 Checkout and History | 4 | Nov 26 | Todo |
| P1 | F09 Registration/login and protected bookings | 5 | Nov 26 | Todo |
| P0 | Add test smoke checks & GitHub Action; all 5 review code | 5 + all | Nov 27 | Todo |
| P0 | Integration testing and demonstration rehearsal | All | Nov 27 | Todo |

**Phase 2** due dates should be entered as soon as the instructor announces the Phase 2 deadline; do not invent dates. Planned Sprint 2 contains F02, F04, F06, F08, F10 plus test expansion, diagrams, SRS and deployment.

## Create these GitHub Issues

Create one issue for F01–F10, and one for each newly discovered bug. Use label `phase-1` or `phase-2`, `feature`, `bug`, `priority:high/medium`, proper assignee, estimate and date. Connect all issues to Project. Add the correct milestone.

**Feature issue acceptance criteria format:**

```text
Title: F05 — Interactive seat selection
Assignee: Member 3
Priority: High
Estimate: 7 hours
Milestone: Phase 1 — Working Demo
Description: Allow the user to select and deselect valid seats for a showtime.
Acceptance Criteria:
- [ ] Render 48 seats with labels.
- [ ] Show occupied seats as disabled.
- [ ] Select/deselect seats and display total.
- [ ] Works on mobile widths.
- [ ] Automated test / manual validation is documented.
```

## Pull Request review rotation

Member 1 → reviewed by Member 2 → reviewed by Member 3 → reviewed by Member 4 → reviewed by Member 5 → reviewed by Member 1.

For each PR: reference the Issue (`Closes #ISSUE_NUMBER`), add testing evidence, request review, fix feedback, and merge only after tests pass. Member authors and reviewers must be distinct.
