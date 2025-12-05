# Sistema de Consultas Médicas - CIMED

## Overview
This is a Django-based medical consultation system that allows patients to schedule appointments with doctors, manage medical records, and handle medication information. The system includes Google OAuth authentication via django-allauth, individual professional pages organized by specialty, and smooth login/registration transitions.

## Project Type
- **Framework**: Django 5.2.6
- **Language**: Python 3.11
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript with CSS animations
- **Authentication**: Django Auth + Google OAuth (django-allauth)

## Recent Changes (December 2, 2025)
- ✅ Created missing `cadastro_pessoas/settings.py` file configured for Replit environment
- ✅ Replaced MySQL with SQLite for development (PostgreSQL support for production)
- ✅ Updated `requirements.txt` to use `psycopg2-binary` instead of `mysqlclient`
- ✅ Added `requests` library as dependency for django-allauth Google provider
- ✅ Configured ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS for Replit proxy
- ✅ Ran all database migrations successfully
- ✅ Updated `.gitignore` for Python/Django best practices
- ✅ Configured Django server workflow on port 5000 with webview
- ✅ Improved production security: dynamic SECRET_KEY generation, configurable ALLOWED_HOSTS
- ✅ Added whitenoise for static file serving in production
- ✅ Configured deployment with gunicorn and collectstatic build step
- ✅ Added production-only security settings (CSRF_COOKIE_SECURE, SESSION_COOKIE_SECURE)
- ✅ Created Especialidade and Profissional models for individual professional pages
- ✅ Implemented professional listing, individual detail pages, and specialty filtering
- ✅ Added CSS transitions and animations to login/registration pages
- ✅ Created database initialization script (scripts/init_db.py)
- ✅ Added success messages with Django messages framework for smooth transitions

### Latest Updates (December 2, 2025)
- ✅ Migrated to PostgreSQL database (Replit Database)
- ✅ Applied all 40 database migrations successfully
- ✅ Fixed Swiper carousel loading order for certificates section
- ✅ Adjusted map size on "Nos Encontre" page (reduced proportions)
- ✅ Added Railway deployment configuration (Procfile, railway.json, runtime.txt)
- ✅ Added CSRF trusted origins for Railway deployment
- ✅ Created comprehensive README.md with installation guide
- ✅ Created SQL script for database creation (scripts/create_database.sql)
- ✅ Updated Google OAuth documentation
- ✅ Implemented role-based permission system with hierarchy (Admin > Médico > Atendente > Paciente)
- ✅ Created permission decorators (admin_required, medico_required, atendente_required, paciente_required)
- ✅ Modernized scheduling/agenda page with interactive calendar and time slots
- ✅ Fixed JavaScript calendar null element errors with proper DOM checks
- ✅ Updated Bootstrap to version 5.3.3 with correct integrity hashes

## Project Architecture

### Apps
1. **cadastro_pessoas** (main project)
   - Settings and URL configuration
   - WSGI/ASGI configuration

2. **pessoas** (main app)
   - User profiles (Médico, Paciente, Atendente)
   - Consultation scheduling and management
   - Medication catalog
   - Dashboard views for different user types

### Models
- **Perfil**: Extended user profile with type (medico/paciente/atendente), birth date, RG, address, phone
- **Consulta**: Appointment scheduling with status tracking, medical reports, and professional assignment
- **Medicamento**: Medication catalog with photos, prices, stock, and prescription requirements
- **Especialidade**: Medical specialties with name, icon, and description
- **Profissional**: Healthcare professionals with specialty, credentials, bio, certifications, and photos

### Key Features
- User authentication (traditional + Google OAuth)
- Role-based access control (doctors, patients, attendants)
- Appointment scheduling with 15-minute time slots (8 AM - 6 PM)
- Medical report writing
- Medication management with stock control
- Multiple specialized services (surgery, exams, dentistry, ophthalmology, tomography)
- Individual professional pages organized by specialty
- Smooth login/registration transitions with CSS animations
- Success messages for user feedback

## Database Configuration

### Development (Current)
Uses SQLite database (`db.sqlite3`) for simplicity and no external dependencies.

### Production (Optional)
To use PostgreSQL, create a Replit Database and the app will automatically detect it via environment variables:
- PGDATABASE
- PGUSER
- PGPASSWORD
- PGHOST
- PGPORT

## Environment Variables

### Recommended for Production
- `SECRET_KEY`: Django secret key (auto-generated with secure random if not set)
- `DEBUG`: Set to "False" for production (defaults to "True" for development)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (defaults to "*" for development)

### Optional (Google OAuth)
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

Note: Google OAuth can also be configured via Django admin after setting up a superuser.

## Running the Application

### Development Server
The Django development server runs automatically on port 5000:
```bash
python manage.py runserver 0.0.0.0:5000
```

### Create Superuser (First Time Setup)
```bash
python manage.py createsuperuser
```

### Admin Panel
Access at: `/admin/`

## Google OAuth Setup (Optional)

1. Create a superuser account
2. Access Django admin at `/admin/`
3. Under "Sites", edit the default site:
   - Domain name: Your Replit domain
   - Display name: Sistema de Consultas
4. Under "Social applications", add Google:
   - Provider: Google
   - Name: Google OAuth
   - Client ID: (from Google Cloud Console)
   - Secret: (from Google Cloud Console)
   - Sites: Select your site

## URLs Structure
- `/` - Home page
- `/login/` - Login page with CSS animations
- `/cadastrar_usuario/` - User registration with CSS animations
- `/profissionais/` - List all healthcare professionals
- `/profissional/<slug>/` - Individual professional page
- `/especialidade/<id>/` - Professionals filtered by specialty
- `/painel/` - User dashboard (redirects based on user type)
- `/admin/` - Django admin panel
- `/accounts/` - django-allauth authentication URLs

## Database Initialization
Run the initialization script to populate sample data:
```bash
python scripts/init_db.py
```
This creates:
- 10 medical specialties
- 6 sample healthcare professionals
- 5 sample medications

## Static Files
Static files are served from `pessoas/static/`:
- CSS: `pessoas/static/css/`
- JavaScript: `pessoas/static/script/`
- Images: `pessoas/static/images/`

Media files (uploaded content) are stored in `media/`.

## Dependencies
See `requirements.txt` for full list. Main dependencies:
- Django 5.2.6
- django-allauth 65.3.0
- psycopg2-binary 2.9.10 (PostgreSQL adapter)
- Pillow 11.0.0 (Image processing)
- PyJWT 2.10.1 (JWT tokens)
- cryptography 44.0.0 (Encryption)
- requests 2.32.3 (HTTP library)
- gunicorn 23.0.0 (Production WSGI server)
- whitenoise 6.8.2 (Static file serving)

## Notes
- The application is configured to work with Replit's proxy/iframe setup
- CSRF protection is configured for Replit domains
- X-Frame-Options set to SAMEORIGIN for preview compatibility
- Calendar JavaScript on home page may show console errors (expected, calendar is used on other pages)
