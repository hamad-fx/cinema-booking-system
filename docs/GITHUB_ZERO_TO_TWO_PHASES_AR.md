# دليل Git + GitHub من الصفر لخمسة طلاب — CineVerse

> **تاريخ التجهيز:** 22 نوفمبر 2026. مناقشة Phase 1: **28 نوفمبر إلى 3 ديسمبر 2026** (في اللاب المخصص لكم). موعد Phase 2 لم يحدده النص المرسل. **كل أمر داخل صندوق `bash` يتكتب في VS Code → Terminal → New Terminal أو Git Bash**، مش في ملف HTML ومش في شريط بحث GitHub. الأوامر اللي عليها عنوان `PowerShell` تتكتب في Windows PowerShell داخل Terminal. خطوات GitHub GUI تتعمل من موقع github.com.

## STEP 0 — قبل أي Git (كل الطلاب)

1. كل Member يعمل GitHub account خاص به. استخدموا حسابكم الحقيقي، كل شخص بيدخل بنفسه، ممنوع تبادل كلمات السر أو استخدام حساب واحد.
2. نزلوا **Git**, **VS Code**, **Python 3.10+**. على Windows اختاروا Add Python to PATH أثناء التنصيب. وجود Node.js مفيد للـ JS syntax check لكن الموقع نفسه لا يحتاج npm.
3. افتحوا VS Code → Terminal → New Terminal ثم اتأكدوا:

```bash
git --version
python --version
```

4. **كل عضو** ينفذ على جهازه (بدّل بالاسم والإيميل الخاصين به على GitHub):

```bash
git config --global user.name "Your Real Name"
git config --global user.email "your-github-email@example.com"
git config --global init.defaultBranch main
git config --global --list
```

5. اختاروا **Member 1** Repo Owner، والباقي Collaborators، وكلهم يكون عندهم وصول Write. خليكوا متفقين على Git usernames والمهام.

## STEP 1 — إنشاء الـ Repository (Member 1 على موقع GitHub)

1. github.com → زر **+** → **New repository**.
2. Repository name: `Cinema-Booking-System`.
3. Visibility اختاروا Public أو Private حسب سياسة المقرر، وخدوا بالكم إن بعض Branch Protection/Environments بتختلف حسب الخطة والـ Visibility.
4. ممكن تبدأوه **Empty** (بدون Add README) علشان أوامر الـ push تبقى مباشرة.
5. اضغط **Create repository**، وانسخ HTTPS repo URL شكله:

```text
https://github.com/YOUR-USERNAME/Cinema-Booking-System.git
```

6. من Repo → Settings → Collaborators (قد يظهر Collaborators and teams) → Invite/Add people → ادعُ الأربعة الباقيين. كل واحد يقبل الدعوة من إيميله/GitHub.

## STEP 2 — تنزيل المشروع وتشغيله محلياً (كل Member)

**خطة أكاديمية صحيحة:** عندكم ملفين: `CineVerse-Full-Reference.zip` يحتوي تطبيقًا مرجعيًا يعمل، و`CineVerse-Team-Starter.zip` يحتوي scaffold كبداية مشاركة حقيقية. الأفضل Member 1 يبدأ بالـ Starter في `main`، وكل واحد من الخمسة **ينفذ/يطور** أجزاءه بيده في Branch مستقلة مستفيداً من الـ Reference كمادة للمراجعة، وليس لمجرد نسخ المشروع كله ونسب الكود لأشخاص لم يكتبوه.

Member 1 يفتح VS Code Terminal في فولدر فارغ مثلاً `Desktop/projects` ويكتب:

```bash
git clone https://github.com/YOUR-USERNAME/Cinema-Booking-System.git
cd Cinema-Booking-System
```

انسخ **محتوى** Starter ZIP داخل الفولدر `Cinema-Booking-System` (مش فولدر داخل فولدر). وبعدها:

```bash
git status
git add .
git commit -m "chore: initialize CineVerse project scaffold"
git push -u origin main
```

باقي الأربعة (كل عضو على جهازه، في فولدر مختلف):

```bash
git clone https://github.com/YOUR-USERNAME/Cinema-Booking-System.git
cd Cinema-Booking-System
git status
```

**ملاحظة:** GitHub Authentication في الـ Terminal ممكن يطلب فتح المتصفح أو Credential Manager؛ استخدم GitHub sign-in المناسب. **متكتبش Password الحساب في أمر git**.

## STEP 3 — GitHub Project Board (موقع GitHub، القيادة Member 1 و2 وكل الفريق مشارك)

1. GitHub → Profile أو Organization → **Projects** → **New project** → Board.
2. سمّوه `CineVerse — Phase 1 & Phase 2`.
3. أنشئوا Status: **Todo / In Progress / In Review / Done**.
4. أضيفوا Custom Fields: **Priority** (High/Medium/Low)، **Estimate (hours)** (Number)، **Start Date** و **Due Date** (Date)، **Iteration** (Sprint 1/Sprint 2). Status موجود غالباً من البداية.
5. افتحوا View باسم `Board`، وView باسم `Backlog`، وView باسم `Roadmap` لو مناسب.
6. ربطوا Issues بتاعة repo بالـ Project (من sidebar issue: Projects → select project، أو Add item من board)، واختروا Assignee ودِدلين وEstimate وحالة كل واحدة.
7. **تحديث يومي:** يبدأ Todo → In Progress عند بدء كتابة الكود، In Review عند فتح PR، Done بعد الدمج والنجاح، مش كلهم Done في نفس يوم المناقشة.

## STEP 4 — Repo Milestones and Issues (موقع GitHub)

1. Repository → Issues → Milestones → New milestone.
2. `Phase 1 — Working Demo`، Due: `2026-11-27` (هدف داخلي قبل تقييم 28 نوفمبر).
3. `Phase 2 — Complete Engineering & Deployment`، Due: بعد ما الدكتور يعلن الموعد، **سيبوه بدون تاريخ مؤقتاً**.
4. Issues → New Issue. استخدموا Feature/Bug template الموجود في `.github/ISSUE_TEMPLATE/`، أو Free text لو لسه القوالب مش مدموجة.
5. طبقوا المهام **F01–F10** من `docs/TEAM_BACKLOG.md`، كل واحدة Issue منفصلة، Assigned Member محدد، Labels + Priority + Start + Estimate + Due + Milestone.
6. كل عضو لازم يضيف Comments وتحديثات عن التنفيذ، ويكتب مشكلة حقيقية كـ Bug Issue لو ظهرت.

مثال Issue واضح:

```text
Title: F05 — Implement interactive seat selection
Assignee: Member 3
Label: feature, phase-1, priority:high
Estimate: 7h
Description: Render rows A-F with eight seats each.
Acceptance Criteria:
- Available seats can be toggled.
- Occupied seats are disabled.
- Selected seats displayed in the summary.
- Price updates as selections change.
- Tested manually, no console errors.
```

## STEP 5 — كل واحد يفتح Branch الخاص بالـ Feature (في VS Code Terminal)

القاعدة الذهبية: **فرع واحد لكل Feature جديدة، ومفيش Code Push مباشر على main**. كل Member ينفذ نفس النمط مع branch باسمه من جدول F01–F10. مثال Member 3:

```bash
git checkout main
git pull origin main
git switch -c feature/seat-selection
```

بعدها Member 3 يفتح الملفات المعنية من **VS Code Explorer** (مثلاً `public/js/seats.js`, `public/css/style.css`)، ويكتب كوده، ويجربه محلياً، وبعدين:

```bash
git status
git diff
git add public/js/seats.js public/css/style.css
git commit -m "feat: render cinema seat grid and selection states"
```

بعد جزء برمجة ثانٍ فعلي:

```bash
git add public/js/seats.js
git commit -m "feat: prevent selecting unavailable seats"
git push -u origin feature/seat-selection
```

**لازم رسائل الـ Commits تكون عن شغل حقيقي**. ممنوع `git commit -m "update"` أو `final` أو `any changes` أو تغيير Comment فقط لمجرد إثبات نشاط.

### Example branches for Phase 1

```text
feature/movie-catalog             → Member 1
feature/movie-showtimes           → Member 2
feature/seat-selection            → Member 3
feature/booking-flow              → Member 4
feature/user-authentication       → Member 5
```

### Feature branches for Phase 2 (at least a second feature each)

```text
feature/favorites-reviews         → Member 1
feature/admin-programming         → Member 2
feature/vip-seat-locking          → Member 3
feature/cancel-snacks-promos      → Member 4
feature/analytics-ci-cd           → Member 5
```

> أنتم ممكن تعملوا فروع أكتر، وده أفضل لو Feature كبيرة لازم تتقسم. كل Feature جديدة تبدأ من **أحدث** `main` بعد الدمج. الـ Bug fix على branch مستقل `fix/...`.

## STEP 6 — Pull Request & Review (على موقع GitHub)

1. بعد Push، افتح Repository → Pull Requests → **New pull request**.
2. `base: main` / `compare: feature/seat-selection`.
3. Title واضح: `feat: implement interactive seat selection`.
4. Description:

```text
Closes #REAL_ISSUE_NUMBER

What changed:
- Implemented 48 seat buttons.
- Disabled booked seats.
- Updated ticket totals.

How tested:
- Started local server and booked two seats.
- Tried booked seat and verified it could not be selected.
- Ran: python -m unittest discover -s tests -v
```

5. Request Reviewer **Member 4**. Reviewer يفتح Files changed، يجرب الكود، ويكتب تعليق Review ويختار **Approve** أو **Request changes**.
6. لو طلب Changes، صاحب PR يصلح على **نفس branch** ويعمل new Commit and Push؛ PR بتتحدث تلقائياً.
7. اتأكد من **green GitHub Actions check**, وامنع الدمج لو الاختبارات فاشلة. بعد الموافقة: **Squash and merge** أو Merge حسب سياسة التيم، واحذف Branch بعد الدمج.
8. Issue المرتبطة تتقفل تلقائيًا بعد الدمج لما تستخدموا `Closes #N`، وحدّثوا Status في Project إلى Done.

### كل طالب بعد Merge يرجع لأحدث main

```bash
git checkout main
git pull origin main
git branch -d feature/seat-selection
```

**ملاحظة مهمة**: إذا PR مش مدموجة، ما تكتبوش إنه تم Merge أو Test passed في التقرير.

## STEP 7 — GitHub Actions (ملف YAML داخل VS Code؛ النتائج على GitHub)

الـ Workflow جاهز في `.github/workflows/ci-cd.yml`. مكانه جوه repo، وليس ملف تكتب أوامره في Terminal. لما حد يعمل PR إلى main، أو Push على main، GitHub يشغل:

- **Python Compile**: syntax errors.
- **JavaScript syntax check** عبر Node على ملفات `public/js/`.
- **Integration tests**: `python -m unittest discover -s tests -v` على Database مؤقتة.
- **Deploy**: بعد دمج main ونجاح الاختبارات، يستدعي Render Hook **إذا** Secret موجود.

على GitHub افتح **Actions → CineVerse CI and CD → أحدث Run → Jobs**. اعرض للدكتور Output الـ Tests. لو أحمر، افتح Logs، صلح الخطأ بفرع جديد وPR جديدة؛ متشيلش الاختبار.

جرب نفس Tests محلياً من VS Code Terminal قبل الـ Push:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q cinema server.py tests
```

ولتشغيل الموقع محلياً:

```bash
python server.py
```

سيب الـ Terminal دي مفتوحة، وافتح Chrome على `http://localhost:8000`. لإيقاف السيرفر، اضغط `Ctrl+C` في التيرمنال. **متفتحش index.html مباشرة بدبل كليك** لأن المشروع ده يحتاج API Backend مش static HTML فقط.

## STEP 8 — التعامل مع Merge Conflicts (Terminal)

لو Member 4 عنده PR وظهر Conflict مع `main`:

```bash
git checkout feature/booking-flow
git fetch origin
git merge origin/main
```

افتح ملفات الـ Conflict في VS Code، استخدم Merge Editor، وافهم كل تغيير. بعد حل التعارضات وتشغيل الاختبارات:

```bash
git add .
git commit -m "merge: resolve booking integration conflicts"
git push origin feature/booking-flow
```

لو مش عارف تحل Conflict بأمان اسأل صاحب الـ Feature التانية وراجعوا الكود سوا. متستخدمش `git push --force` على `main`.

## STEP 9 — Phase 1: ماذا تعرضوا في اللاب؟

**Nov 22–27 (internal sprint)**
- Nov 22: Repo, collaborators, board, milestones, Issues, module interface agreement.
- Nov 23–24: Member 1 catalog + Member 2 details/showtimes + Member 5 auth/API setup.
- Nov 24–25: Member 3 seat selection, Member 4 booking flow.
- Nov 26: Cross-integration, PR reviews, bug issues and fixes.
- Nov 27: Tests green, README updated, project board complete, 5-member rehearsal.

**Demo sequence**: Register → Home → choose movie → choose showtime → seats → snacks/promos optional → login/checkout → confirm → My Bookings → ticket. Demonstrate second user cannot double-book same seat. Show GitHub Projects fields, Issues, one real bug, PR review, Actions, and every member's commits.

## STEP 10 — Phase 2: what is still mandatory?

1. Finish **at least 2 real features per member** (10+ team total); each on a **new feature branch**, feature complete + tested before merge.
2. Keep Projects Backlog / Roadmap and milestones current; record real Scrum notes under `docs/scrum/` (date, attendees, yesterday/today/blockers, decisions, next sprint). Don't invent meetings.
3. Complete SRS (`docs/SRS.md`), Architecture, Use Case, Class, Sequence, Activity, State, ERD and Deployment diagrams under `docs/diagrams/`; customize them to the implemented version and your lecture requirements.
4. Expand meaningful automated test cases: authentication, wrong role, seat concurrency, date validation, promos, cancellation, reviews, favorites, admin, end-to-end manual UI.
5. Deploy a **live URL** using `docs/DEPLOYMENT.md`, test it from a teammate's laptop/phone, add URL to README and show live during the evaluation.
6. Add phase-wise evidence: Sprint notes, GitHub Issues and PRs, Actions logs and demo screenshots. All must be real evidence.

## STEP 11 — في المناقشة كل واحد يقول إيه؟

| Member | Coding demo | GitHub proof |
|---|---|---|
| 1 | Catalog/search & favorites/reviews | F01, F02 Issues/PRs/commits, Project creation |
| 2 | Details/showtimes and admin scheduling | F03, F04, issue estimates & sprint backlog |
| 3 | Seats and VIP locking | F05, F06, own tests & PR reviews |
| 4 | Booking, cancellation, snacks and promos | F07, F08, milestone & board updates |
| 5 | Auth, admin stats, CI/CD and tests | F09, F10, workflow logs & release |

## STEP 12 — أهم 6 أخطاء تجنبوها

- رفع ZIP كامل بحساب Member 1 ثم تقسيم نفس الملفات على 5 بدون عمل برمجي فعلي. **ده مش دليل Contributors**.
- كل الشغل على main وPRs شكلية بعد انتهاء التنفيذ.
- GitHub Project board اتعمل ليلة المناقشة ومفيش أي تاريخ تحديث حقيقي.
- PRs اتعمل لها Merge بدون Review حقيقي أو Tests.
- GitHub Actions workflow موجود في YAML لكنه فاشل أو لم يعمل قط.
- القول إن المشروع Live بدون رابط شغال، أو القول إن SQLite على Render Free بيحفظ الحجوزات بشكل دائم.

## Git cheat sheet لكل Member (داخل VS Code Terminal)

```bash
git status                         # أنا على أنهي branch وفيه تغييرات إيه؟
git branch                         # كل الفروع المحلية
git log --oneline --max-count=12   # آخر commits
git checkout main                  # ارجع main
git pull origin main               # نزّل أحدث نسخة
git switch -c feature/my-feature  # Branch جديدة
# ... write/test actual code ...
git add path/to/myfile.js          # Stage ملف معين
git commit -m "feat: describe changes"  # Commit واضح
git push -u origin feature/my-feature      # ارفع branch
```

## Where to learn more (official)

- [GitHub Projects quickstart](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects)
- [GitHub Issues milestones](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/creating-and-editing-milestones-for-issues-and-pull-requests)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Render deployment](https://render.com/docs/deploys)
