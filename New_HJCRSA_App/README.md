# New_HJCRSA_App

A Django-based membership and treasury management application for HJCRSA. It provides tools to manage main members and dependents, track treasury payments, scan and manage barcodes, view activity logs, and generate reports.

## Features
- Authentication (login, logout, signup) with custom auth backend.
- Manage Main Members and Dependents (add, list, edit, details API).
- Treasury and Treasury Dep payments (add, list, per-member and per-dependent payment history APIs).
- Activity log with filtering and pagination.
- Dashboard/Home with charts and real-time updates.
- Barcode generation, listing, detail views, scanner and lookup.
- Upload and store member pictures.
- Fund reports and aggregated stats endpoints.

## Tech Stack
- Python 3.10+ (recommended)
- Django 5.x
- django-filter
- Pillow (image handling)
- openpyxl (Excel export)
- SQLite/PostgreSQL (default settings use SQLite unless configured)

See `requirements.txt` for the full list of dependencies.

## Getting Started

### Prerequisites
- Python (3.10 or newer recommended)
- pip
- virtualenv (optional but recommended)

### 1) Clone the repository
```bash
git clone <your-repo-url> New_HJCRSA_App
cd New_HJCRSA_App
```

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Environment variables
Create a `.env` file in `New_HJCRSA_App/` (project package) or repository root as you prefer. Example variables (adjust as needed):
```
# Django
SECRET_KEY=replace-with-a-strong-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional; defaults to SQLite if not set in settings)
# DATABASE_URL=postgres://user:password@localhost:5432/hjcrsa
```
Note: The repo includes `New_HJCRSA_App/.env`. Ensure it has valid values before running the app.

### 5) Apply migrations and create a superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6) Run the development server
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser.

- Admin: http://127.0.0.1:8000/admin/
- Login: http://127.0.0.1:8000/login/
- Home/Dashboard: http://127.0.0.1:8000/home/

## Application URLs (high level)
The main app is `main_app`. Key routes exposed in `main_app/urls.py` include:
- Members: `/members/`, add `/member/add/`, edit `/member/<card>/edit/`
- Dependents: `/dependents/`, add `/dependent/add/`
- Treasury: `/treasury/`, add `/treasury/add/`
- Treasury Dep: `/treasury-dep/`, add `/treasury-dep/add/`
- Activity Log: `/activity-log/`
- Upload Picture: `/upload-picture/`
- Barcodes: `/barcodes/`, details `/barcodes/<id>/`, scanner `/barcodes/scanner/`, lookup `/barcodes/lookup/`
- Fund report: `/reports/fund/`

APIs:
- Member payments: `/api/member/<card_number>/payments/`
- Member dependents: `/api/member/<card_number>/dependents/`
- Member details: `/api/member/<card_number>/details/`
- Dependent payments: `/api/dependent/<dependent_id>/payments/`
- Gender distribution: `/api/gender-distribution/`

## Barcode Commands
The project includes a management command to generate member barcodes.

Run:
```bash
python manage.py generate_barcodes
```
Check `main_app/management/commands/generate_barcodes.py` for options and implementation.

## Static Files and Assets
- App static files under `main_app/static/main_app/` (CSS, JS, images).
- Templates under `main_app/templates/`.
- Logo assets are located in `/static` and `/main_app/static/main_app`.

In development, Django serves static files automatically with `runserver`.

## Testing
Basic tests may be found in `main_app/tests.py`.
Run tests:
```bash
python manage.py test
```

## Deployment Notes
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Configure `SECRET_KEY` securely through environment variables.
- Set up a production-ready database and run `migrate`.
- Collect static files:
```bash
python manage.py collectstatic
```
- Configure a WSGI server (e.g., gunicorn/uwsgi) and a reverse proxy (e.g., Nginx).

## Troubleshooting
- Missing migrations: run `python manage.py makemigrations && python manage.py migrate`.
- Authentication issues: ensure users are created and permissions are set. Some views require specific permissions like `main_app.view_treasurydep`.
- Image upload errors: ensure Pillow is installed and media settings are configured if you change defaults.
- Barcode pages: ensure JS is loaded and camera access is allowed in the browser for scanner.

## Contributing
1. Fork the repo.
2. Create a feature branch.
3. Commit your changes with clear messages.
4. Open a pull request.

## License
Add your preferred license here (e.g., MIT). If a `LICENSE` file is added, reference it.

## Acknowledgements
- Django and its community.
- django-filter, Pillow, openpyxl.
