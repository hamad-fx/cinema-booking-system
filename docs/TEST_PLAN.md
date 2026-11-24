# CineVerse — Test Plan and Acceptance Checklist

## Automated tests

From VS Code Terminal in repo root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

`tests/test_system.py` starts a real local HTTP server on a random port and uses an isolated SQLite database. This keeps test data separate from the demonstration database. The GitHub Actions job also runs syntax checks and these tests on PRs and pushes.

## Manual end-to-end scenarios

| ID | Steps | Expected result | Owner for verification |
|---|---|---|---|
| T01 | Open site | Movie catalog loads responsively | M1 |
| T02 | Search Interstellar, filter Sci-Fi | Correct movie cards | M1 |
| T03 | Open detail, read reviews, pick future time | Showtime selected | M2 |
| T04 | Select A1 then deselect A1 | Seat state toggles | M3 |
| T05 | Try occupied seat | Cannot select | M3 |
| T06 | Select E1 VIP | +70 EGP compared with standard | M3 |
| T07 | Select 2 seats, popcorn x2, CINE10 | Correct preview/checkout totals | M3 + M4 |
| T08 | Try checkout without account | Redirect to login | M5 |
| T09 | Register and complete booking | Confirmation stored on server | M4 + M5 |
| T10 | Log out, log back in, My Bookings | Own reservation visible | M4 |
| T11 | Another user tries reserved seat same show | Server rejects double booking | M3 |
| T12 | View/print ticket | Reference and QR display | M4 |
| T13 | Cancel tomorrow's booking | Status cancelled, seat released | M4 |
| T14 | Submit bad promo or invalid seat IDs by API | 400 validation response | M3 |
| T15 | Ordinary customer opens admin API/page | 403 / no access | M5 |
| T16 | Admin adds movie and showtime | New movie & show appear | M2 |
| T17 | Save favorite and movie review | Persisted for own account | M1 |
| T18 | Inspect GitHub Actions PR check | Tests green; logs show actual tests | M5 |
| T19 | Live deployment: open URL on another device | Site loads; main flow works | All |

## Tests still worth adding in Phase 2

Concurrent POST booking attempts via threads, session expiry behavior, HTML accessibility with automated tooling, responsive browser screenshots, rate-limiting/security tests if implemented, deployed smoke tests, load test and database backup recovery.

## What to show the instructor

Record **actual** output of test commands, screenshots from GitHub Actions, PR reviews and bug Issues. Do not include fake test results or pretend untested functionality is complete.
