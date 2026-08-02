# ParcelPath

A production-ready Logistics, Courier, Shipment & Delivery Management System built with Django.

ParcelPath is designed like a real logistics company software rather than a portfolio project. It supports customer shipment booking, driver management, shipment tracking, route planning, notifications, reporting, invoices, and an admin dashboard.

---

# Features

## Customer Portal

- Register/Login
- Dashboard
- Book Shipment
- Shipment History
- Track Shipment
- Notifications
- Profile Management

---

## Driver Portal

- Driver Dashboard
- Assigned Deliveries
- Delivery History
- Route Management
- Update Shipment Status
- Upload Delivery Proof

---

## Admin Dashboard

- Dashboard Analytics
- Customer Management
- Driver Management
- Shipment Management
- Tracking Management
- Route Management
- Reports
- Notifications
- Settings

---

## Shipment Management

- Create Shipment
- Assign Driver
- Generate Tracking Number
- Generate Invoice
- Print Shipping Label
- Shipment Timeline
- Delivery Status

---

## Tracking System

- Public Tracking
- Live Shipment Updates
- Tracking Timeline
- Delivery History

---

## Route Management

- Create Routes
- Assign Drivers
- Route Overview
- Stop Management

---

## Notification System

- Shipment Created
- Driver Assigned
- Out for Delivery
- Delivered
- Failed Delivery
- System Notifications

---

## Reports

- Shipment Reports
- Delivery Reports
- Revenue Reports
- Driver Reports
- Customer Reports

---

# Tech Stack

Backend

- Django
- SQLite
- Django ORM

Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

Libraries

- Pillow
- ReportLab
- QRCode
- Pandas
- OpenPyXL
- Channels

Deployment Ready

- Gunicorn
- WhiteNoise
- PostgreSQL Ready
- Docker Ready

---

# Project Structure

```
ParcelPath/

accounts/
customers/
drivers/
shipments/
tracking/
dashboard/
notifications/
routes/
contact/
destinations/
core/

templates/

static/

media/

config/

manage.py
requirements.txt
README.md
```

---

# Installation

Clone repository

```bash
git clone https://github.com/yourusername/ParcelPath.git
```

Move inside project

```bash
cd ParcelPath
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Copy environment

```bash
cp .env.example .env
```

Windows

```bash
copy .env.example .env
```

Run migrations

```bash
python manage.py migrate
```

Create superuser

```bash
python manage.py createsuperuser
```

Run server

```bash
python manage.py runserver
```

Visit

```
http://127.0.0.1:8000
```
---

# Default User Roles

## Administrator

Complete system access.

Permissions

- Dashboard
- Customer Management
- Driver Management
- Shipment Management
- Route Management
- Reports
- Notifications
- Settings

---

## Customer

Permissions

- Register
- Login
- Book Shipment
- Track Shipment
- View Shipment History
- Edit Profile
- Receive Notifications

---

## Driver

Permissions

- Login
- Assigned Deliveries
- Delivery History
- Update Delivery Status
- Upload Delivery Proof
- View Assigned Routes

---

# Shipment Workflow

```
Customer

↓

Book Shipment

↓

Shipment Created

↓

Tracking Number Generated

↓

Admin Verification

↓

Driver Assigned

↓

Pickup Completed

↓

In Transit

↓

Out For Delivery

↓

Delivered

↓

Delivery Confirmation

↓

Invoice Completed
```

---

# Database Modules

```
Accounts

Customers

Drivers

Shipments

Shipment Tracking

Routes

Notifications

Dashboard

Reports

Settings

Destinations
```

---

# Main Features

### Authentication

- Secure Login
- Registration
- Password Reset
- Change Password
- User Profile

---

### Customer

- Dashboard
- Book Shipment
- Shipment History
- Shipment Details
- Notifications

---

### Driver

- Dashboard
- Route List
- Delivery History
- Proof Upload
- Status Updates

---

### Shipment

- Create Shipment
- Edit Shipment
- Cancel Shipment
- Assign Driver
- Generate Invoice
- Print Label

---

### Tracking

- Public Tracking
- Internal Tracking
- Live Status
- Timeline History

---

### Dashboard

- Shipment Analytics
- Revenue Statistics
- Driver Statistics
- Customer Statistics
- Monthly Reports

---

# Future Improvements

- GPS Live Tracking

- SMS Notifications

- WhatsApp Integration

- Email Automation

- Payment Gateway

- Customer Wallet

- Multi Warehouse Support

- Barcode Scanner

- QR Code Scanner

- AI Route Optimization

- AI Delivery Prediction

- Mobile Application

- REST API

- GraphQL API

- Multi-language Support

- Multi-company Support

- Audit Logs

- Role Based Permissions

- Two Factor Authentication

- OTP Login

- Digital Signature

- Driver Attendance

- Fleet Management

- Fuel Management

- Maintenance Scheduler

- Business Intelligence Dashboard

---

# Production Ready Features

- Responsive UI

- Modular Django Apps

- Environment Variables

- Static File Management

- Media Management

- PostgreSQL Ready

- Docker Ready

- Nginx Ready

- Gunicorn Ready

- WhiteNoise Ready

- Celery Ready

- Redis Ready

- Django Channels Ready

- Logging Ready

- Secure Authentication

- CSRF Protection

- XSS Protection

- SQL Injection Protection

- Session Management

- Password Hashing

- Form Validation

---

# Recommended Production Deployment

## Operating System

- Ubuntu 24.04 LTS

---

## Python

- Python 3.12+

---

## Database

Development

- SQLite

Production

- PostgreSQL

---

## Web Server

- Nginx

---

## WSGI / ASGI

- Gunicorn
- Daphne

---

## Cache

- Redis

---

## Background Tasks

- Celery

---

## File Storage

Development

- Local Storage

Production

- AWS S3
- DigitalOcean Spaces
- Cloudflare R2

---

## Monitoring

- Sentry
- Prometheus
- Grafana

---

## Suggested Folder Structure

```
ParcelPath/

accounts/
customers/
drivers/
shipments/
tracking/
dashboard/
routes/
notifications/
contact/
destinations/
core/

config/

templates/
static/
media/

logs/
backups/

requirements.txt
.env
manage.py
README.md
Dockerfile
docker-compose.yml
```

---

# Security Checklist

- Password Hashing
- CSRF Protection
- XSS Protection
- SQL Injection Protection
- Session Expiry
- Secure Cookies
- HTTPS Support
- Environment Variables
- Content Security Policy
- Rate Limiting
- Audit Logs
- Login Attempt Limiting
- Secure File Upload Validation

---

# Performance Optimizations

- Database Indexing
- ORM Query Optimization
- Select Related
- Prefetch Related
- Static File Compression
- WhiteNoise
- Browser Caching
- Lazy Loading
- Image Compression
- Redis Cache
- Pagination
- Background Tasks
- Query Caching

---

# Planned Integrations

- Google Maps API
- Razorpay
- Stripe
- Twilio SMS
- WhatsApp Business API
- Firebase Cloud Messaging
- SendGrid
- Gmail SMTP
- AWS S3
- OpenStreetMap
- Google reCAPTCHA
- Cloudinary

---

# Testing

Run all tests

```bash
python manage.py test
```

Run a specific app

```bash
python manage.py test shipments
```

Run with coverage

```bash
coverage run manage.py test
coverage report
```

---

# Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

# License

This project is released under the MIT License.

---

# Author

**ParcelPath Development Team**

Built using:

- Django
- Bootstrap 5
- HTML5
- CSS3
- JavaScript

---

# Version History

## v1.0.0

Initial production-ready release including:

- Authentication
- Customer Portal
- Driver Portal
- Shipment Management
- Tracking System
- Route Management
- Notifications
- Dashboard
- Reports
- Invoice Generation
- Shipping Labels
- Responsive UI
- Docker Ready Configuration
- PostgreSQL Support
- WebSocket Support
- Production Deployment Structure

---

## Upcoming Versions

### v1.1

- GPS Tracking
- Email Notifications
- SMS Notifications
- Advanced Reports

### v1.2

- Mobile API
- Payment Gateway
- QR Code Tracking
- Barcode Scanner

### v2.0

- AI Route Optimization
- Fleet Management
- Warehouse Management
- Business Intelligence Dashboard
- Multi-company Support
- Advanced Analytics

---

**Thank you for using ParcelPath!**