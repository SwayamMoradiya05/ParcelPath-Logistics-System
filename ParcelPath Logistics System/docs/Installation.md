# ParcelPath Installation Guide

## Overview

This guide explains how to install and run the ParcelPath Logistics Management System on your local machine.

---

# System Requirements

Before installing the project, ensure the following software is installed.

- Python 3.13+
- Git
- SQLite (Default)
- Visual Studio Code (Recommended)

---

# Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ParcelPath.git
```

Move into the project directory.

```bash
cd ParcelPath
```

---

# Create Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate the virtual environment.

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

Activate it.

```bash
source venv/bin/activate
```

---

# Install Dependencies

Install all required packages.

```bash
pip install -r requirements.txt
```

---

# Database Migration

Create database tables.

```bash
python manage.py makemigrations
```

Apply migrations.

```bash
python manage.py migrate
```

---

# Create Superuser

Create an administrator account.

```bash
python manage.py createsuperuser
```

Follow the prompts:

- Email
- Password

---

# Run Development Server

```bash
python manage.py runserver
```

The application will be available at:

```
http://127.0.0.1:8000/
```

---

# Django Admin

Visit

```
http://127.0.0.1:8000/admin/
```

Login using the superuser credentials.

---

# Default User Roles

ParcelPath supports three user roles.

## Administrator

- Manage shipments
- Manage customers
- Manage drivers
- Assign drivers
- Update shipment status
- View reports
- Manage contact requests

---

## Customer

- Register account
- Create shipments
- Track shipments
- View shipment history
- Update profile
- Contact support

---

## Driver

- View assigned shipments
- Update delivery status
- Toggle availability
- Track delivery progress
- Manage profile

---

# Project Structure

```
ParcelPath/
│
├── apps/
│   ├── accounts/
│   ├── contact/
│   ├── customers/
│   ├── dashboard/
│   ├── destinations/
│   ├── drivers/
│   ├── notifications/
│   ├── routes/
│   ├── shipments/
│   └── tracking/
│
├── config/
├── docs/
├── media/
├── static/
├── templates/
│
├── manage.py
├── requirements.txt
└── README.md
```

---

# Static Files

During development, static files are served automatically.

For production:

```bash
python manage.py collectstatic
```

---

# Media Files

Uploaded files are stored inside:

```
media/
```

Examples include:

- Profile Pictures
- Shipment Images
- Labels

---

# Useful Django Commands

Run server

```bash
python manage.py runserver
```

Create migrations

```bash
python manage.py makemigrations
```

Apply migrations

```bash
python manage.py migrate
```

Check project

```bash
python manage.py check
```

Open Django shell

```bash
python manage.py shell
```

Create superuser

```bash
python manage.py createsuperuser
```

Collect static files

```bash
python manage.py collectstatic
```

---

# Troubleshooting

## ModuleNotFoundError

Install dependencies again.

```bash
pip install -r requirements.txt
```

---

## Database Errors

Delete the SQLite database only if starting from scratch.

```text
db.sqlite3
```

Then run:

```bash
python manage.py migrate
```

---

## Static Files Not Loading

Run

```bash
python manage.py collectstatic
```

Check:

- STATIC_URL
- STATIC_ROOT
- STATICFILES_DIRS

---

## Port Already in Use

Run on another port.

```bash
python manage.py runserver 8001
```

---

# Deployment Checklist

Before deployment ensure:

- All migrations applied
- DEBUG=False
- ALLOWED_HOSTS configured
- SECRET_KEY secured
- Static files collected
- Media storage configured
- requirements.txt updated
- python manage.py check reports no issues

---

# Technology Stack

Backend

- Python
- Django

Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

Database

- SQLite (Development)

Version Control

- Git
- GitHub

---

# Support

For issues, suggestions, or bug reports, create an issue in the GitHub repository.

---

**ParcelPath – Smart Logistics & Parcel Delivery System**