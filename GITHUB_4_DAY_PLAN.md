# Four-Day GitHub Commit Plan

Use this plan for real development over four days. Commit after completing and testing each chunk. Do not backdate commits or change system time to create artificial history.

Create an empty public GitHub repository named `peer-skill-exchange-platform`, then open this folder in VS Code.

```bash
git init
git branch -M main
git remote add origin https://github.com/23f2002275/peer-skill-exchange-platform.git
git config user.name "Pratham Bhardwaj"
git config user.email "23f2002275@ds.study.iitm.ac.in"
```

## Day 1: Project setup, authentication and skill catalog

Files:

```text
.gitignore
backend/app.py
backend/config.py
backend/extensions.py
backend/models.py
backend/security_setup.py
backend/create_db.py
backend/requirements.txt
backend/routes/__init__.py
backend/routes/auth.py
backend/routes/skills.py
frontend/index.html
frontend/css/style.css
frontend/js/api.js
frontend/js/components/Home.js
frontend/js/components/Login.js
frontend/js/components/Register.js
```

Commands:

```bash
git add .gitignore backend/app.py backend/config.py backend/extensions.py backend/models.py backend/security_setup.py backend/create_db.py backend/requirements.txt backend/routes/__init__.py backend/routes/auth.py backend/routes/skills.py frontend/index.html frontend/css/style.css frontend/js/api.js frontend/js/components/Home.js frontend/js/components/Login.js frontend/js/components/Register.js
git commit -m "set up authentication profiles and skill catalog"
git push -u origin main
```

Verify registration gives 3 starter credits and protected endpoints reject missing tokens.

## Day 2: Offering CRUD and discovery pages

Files:

```text
backend/routes/offerings.py
frontend/js/components/Discover.js
frontend/js/components/OfferingDetails.js
frontend/js/components/ManageOffering.js
frontend/js/components/MyOfferings.js
frontend/js/app.js
```

Commands:

```bash
git add backend/routes/offerings.py frontend/js/components/Discover.js frontend/js/components/OfferingDetails.js frontend/js/components/ManageOffering.js frontend/js/components/MyOfferings.js frontend/js/app.js
git commit -m "add teaching offerings and discovery filters"
git push
```

Verify offering create, edit, pause, activate, archive, delete and search filters.

## Day 3: Requests, sessions, credits and dashboards

Files:

```text
backend/routes/requests.py
backend/routes/sessions.py
backend/routes/dashboard.py
frontend/js/components/Requests.js
frontend/js/components/Sessions.js
frontend/js/components/Wallet.js
frontend/js/components/Dashboard.js
frontend/js/components/Profile.js
```

Commands:

```bash
git add backend/routes/requests.py backend/routes/sessions.py backend/routes/dashboard.py frontend/js/components/Requests.js frontend/js/components/Sessions.js frontend/js/components/Wallet.js frontend/js/components/Dashboard.js frontend/js/components/Profile.js
git commit -m "build session workflow and credit wallet"
git push
```

Verify credit reservation, cancellation refund, scheduling, mutual confirmation, settlement and reviews.

## Day 4: Administration, jobs, tests and README

Files:

```text
backend/routes/admin.py
backend/celery_worker.py
backend/tasks.py
backend/tests/test_api.py
frontend/js/components/AdminDashboard.js
docs/screenshots/.gitkeep
README.md
GITHUB_4_DAY_PLAN.md
```

Commands:

```bash
git add backend/routes/admin.py backend/celery_worker.py backend/tasks.py backend/tests/test_api.py frontend/js/components/AdminDashboard.js docs/screenshots/.gitkeep README.md GITHUB_4_DAY_PLAN.md
git commit -m "add moderation background jobs and project docs"
git push
```

After taking screenshots:

```bash
git add docs/screenshots
git commit -m "add final application screenshots"
git push
```

## Daily checks

```bash
git status
git diff
python -m compileall backend
cd backend && pytest -q && cd ..
git add <files completed today>
git commit -m "clear description of today's work"
git push
```
