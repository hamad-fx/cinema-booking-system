# Live deployment — GitHub Actions → Render

> **Phase 2 requires a LIVE deployed application**, not merely GitHub source code. The ZIP itself does **not** deploy anything.

## How to deploy

1. Push the team repository (with real team PR history) to GitHub under a repository controlled by a team member.
2. Sign up for [Render](https://render.com). In Dashboard select **New → Web Service**.
3. Link your GitHub repository and choose the **main** branch.
4. Runtime: Python. Build command: `pip install -r requirements.txt`. Start command: `python server.py`. The application binds to the `PORT` environment variable supplied by Render.
5. Add environment variables in Render's service settings:
   - `COOKIE_SECURE=1` because the deployed site is HTTPS.
   - `DEMO_ADMIN_EMAIL=...` (use a unique admin email).
   - `DEMO_ADMIN_PASSWORD=...` (unique 16+ character password, never commit it).
   - `DATABASE_PATH=/var/data/cinema.sqlite3` **only if you have attached persistent storage** at `/var/data`; otherwise omit the variable and note the demo DB is temporary.
6. Choose a suitable service plan and deploy. Note the actual assigned `https://...onrender.com` URL. Test `/api/health` and then the browser booking flow.
7. In Render, under **Settings**, copy the confidential **Deploy Hook URL**. Switch off automatic code-triggered deploys so the CI workflow gates deployments (or at least understand the duplicate-deploy risk).
8. In GitHub repository select **Settings → Secrets and variables → Actions → New repository secret**, name it `RENDER_DEPLOY_HOOK_URL`, paste your deploy hook URL.
9. `.github/workflows/ci-cd.yml` automatically runs syntax checks and integration tests on Pull Requests and pushes to `main`. After all tests pass on `main`, its `deploy` job calls the hook. A *requested deploy* is not proof that the new version is live: verify Render's build/start/health logs and the live URL.
10. Put the actual live URL in `README.md` and in the GitHub Project milestone evidence, and demonstrate it during Phase 2.

Official docs: [Render deployment](https://render.com/docs/deploys), [Render deploy hooks](https://render.com/docs/deploy-hooks), [GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).

## Important persistence limitation

**Render Free web services have ephemeral filesystems.** They can spin down after inactivity; local SQLite files disappear after spin-down/restart/redeploy. You therefore cannot honestly call a free SQLite deployment a permanent multi-user ticketing system. This is acceptable only as a **clearly labeled demo with resettable state**, if your instructor accepts it. For lasting data, use a paid persistent disk or migrate to a managed PostgreSQL database and document/test the migration. Render's free Postgres option, where offered, has retention/expiry limitations too. See [Render Free limitations](https://render.com/docs/free).

## Security scope

The code demonstrates password hashing and role checks, SQLite transactional seat uniqueness and HttpOnly session cookies. For a production service add CSRF tokens, per-IP login rate limits, database backups/migrations, robust TLS/reverse-proxy config, monitoring, external provider integration, privacy retention policy, payment-provider-hosted checkout and verifiable ticket scanning. Do not store payment card data.

**No live deployment has been performed as part of this deliverable.** The team must connect the repository and hosting account themselves.
