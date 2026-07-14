# Peer Skill Exchange Platform

A student-to-student learning platform where members publish skills they can teach, request sessions, schedule meetings and exchange non-monetary skill credits.

## Main features

- Registration and login with Flask-Security
- Token-based protected REST APIs
- Member and admin authorization
- Public member profiles
- Skill categories and normalized skill catalog
- Complete teaching-offering CRUD
- Search by keyword, category, skill, level and teaching mode
- Learning request acceptance and rejection
- Credit reservation when a teacher accepts a request
- Session scheduling with overlap validation
- Mutual completion confirmation
- One-time credit settlement after completion
- Credit wallet and immutable transaction history
- Reviews, reports and admin moderation
- Role dashboard
- Celery and Redis task for stale request cleanup
- Pytest API tests

## Technology used

- Flask
- Flask-SQLAlchemy
- Flask-Security-Too
- SQLite
- VueJS 2
- Vue Router
- Axios
- Bootstrap 5
- Celery and Redis

The frontend uses CDN scripts and is served directly by Flask. Node.js and npm are not required.

## Project structure

```text
peer-skill-exchange-platform/
├── backend/
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── offerings.py
│   │   ├── requests.py
│   │   ├── sessions.py
│   │   └── skills.py
│   ├── tests/test_api.py
│   ├── app.py
│   ├── celery_worker.py
│   ├── config.py
│   ├── create_db.py
│   ├── extensions.py
│   ├── models.py
│   ├── requirements.txt
│   ├── security_setup.py
│   └── tasks.py
├── frontend/
│   ├── css/style.css
│   ├── js/components/
│   ├── js/api.js
│   ├── js/app.js
│   └── index.html
├── docs/screenshots/
├── .gitignore
└── README.md
```

## Installation on Windows

Open the project folder in VS Code and run:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
cd backend
python create_db.py
python app.py
```

Open `http://127.0.0.1:5001`.

For Git Bash:

```bash
source .venv/Scripts/activate
```

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@skillexchange.com | admin123 |
| Member/Teacher | teacher@skillexchange.com | teacher123 |
| Member/Learner | learner@skillexchange.com | learner123 |

Each member starts with 3 credits. The seed command also creates categories, skills and sample offerings.

## Authentication

Protected requests send the login token using:

```text
Authentication-Token: <token>
```

Example:

```bash
curl -X POST http://127.0.0.1:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"learner@skillexchange.com","password":"learner123"}'
```

## API documentation

### Authentication and profiles

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Register member with starter credits |
| POST | `/api/auth/login` | Public | Login and receive token |
| GET | `/api/auth/me` | Authenticated | Current profile and balance |
| PUT | `/api/auth/profile` | Authenticated | Update profile |
| GET | `/api/auth/users/<id>` | Public | Public member profile |
| POST | `/api/auth/logout` | Authenticated | Invalidate current token |

### Skills and offerings

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api/skills` | Public | Search active skills |
| GET | `/api/skills/categories` | Public | List categories |
| GET | `/api/offerings` | Public | Search active offerings |
| GET | `/api/offerings/mine` | Member | Own offerings |
| GET | `/api/offerings/<id>` | Public | Offering details |
| POST | `/api/offerings` | Member | Create offering |
| PUT | `/api/offerings/<id>` | Owner/Admin | Update offering |
| DELETE | `/api/offerings/<id>` | Owner/Admin | Delete offering without history |
| PATCH | `/api/offerings/<id>/status` | Owner/Admin | Activate, pause, archive or hide |

Offering search supports `keyword`, `skill_id`, `category_id`, `mode`, `level`, `page` and `per_page`.

### Requests and sessions

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/offerings/<id>/requests` | Member | Request learning session |
| GET | `/api/requests/mine` | Member | Incoming and outgoing requests |
| PATCH | `/api/requests/<id>/accept` | Teacher | Accept and reserve learner credits |
| PATCH | `/api/requests/<id>/reject` | Teacher | Reject request |
| PATCH | `/api/requests/<id>/cancel` | Participant/Admin | Cancel request |
| POST | `/api/requests/<id>/session` | Teacher | Schedule accepted request |
| GET | `/api/sessions/mine` | Member | List sessions |
| GET | `/api/sessions/<id>` | Participant/Admin | Session details |
| PATCH | `/api/sessions/<id>/cancel` | Participant/Admin | Cancel and release reserved credits |
| PATCH | `/api/sessions/<id>/confirm` | Participant | Confirm completion |
| POST | `/api/sessions/<id>/reviews` | Participant | Review after completion |
| GET | `/api/credits/transactions` | Member | Wallet history |
| POST | `/api/reports` | Member | Submit moderation report |
| GET | `/api/dashboard` | Member | Summary and upcoming sessions |

### Administration

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| GET | `/api/admin/statistics` | Admin | Platform metrics |
| GET | `/api/admin/users` | Admin | List users |
| PATCH | `/api/admin/users/<id>/active` | Admin | Suspend or activate user |
| POST | `/api/admin/users/<id>/credit-adjustments` | Admin | Adjust credits with reason |
| POST | `/api/admin/categories` | Admin | Create category |
| POST | `/api/admin/skills` | Admin | Create skill |
| GET | `/api/admin/offerings` | Admin | List all offerings |
| PATCH | `/api/admin/offerings/<id>/visibility` | Admin | Hide or restore offering |
| GET | `/api/admin/reports` | Admin | List reports |
| PATCH | `/api/admin/reports/<id>` | Admin | Resolve or dismiss report |

## Credit workflow

1. A new member receives 3 starter credits.
2. Creating a request does not change the balance.
3. When the teacher accepts, the required credits are deducted and marked as reserved.
4. Cancelling before settlement refunds the reserved credits.
5. Both participants confirm completion.
6. The reserved credits are transferred to the teacher exactly once.
7. Every change is stored as a `CreditTransaction`.

## Celery and Redis setup

Start Redis:

```powershell
docker run -d --name skill-exchange-redis -p 6379:6379 redis:7
```

Start the worker from `backend`:

```powershell
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

Start the scheduler in another terminal:

```powershell
celery -A celery_worker.celery beat --loglevel=info
```

The scheduled job cancels old pending requests after the configured stale period.
