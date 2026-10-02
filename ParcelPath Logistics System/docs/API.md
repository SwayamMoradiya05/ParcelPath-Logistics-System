# ParcelPath API & URL Documentation

## Overview

This document describes the major URLs, modules, and functionality of the ParcelPath Logistics Management System.

The application follows Django's URL routing architecture and is divided into multiple apps.

---

# Base URL

```
http://127.0.0.1:8000/
```

---

# Public Pages

| URL | Description |
|------|-------------|
| `/` | Home Page |
| `/about/` | About ParcelPath |
| `/services/` | Services |
| `/pricing/` | Pricing Plans |
| `/destinations/` | Delivery Destinations |
| `/faq/` | Frequently Asked Questions |
| `/contact/` | Public Contact Form |
| `/track/` | Public Shipment Tracking |

---

# Authentication

Base URL

```
/accounts/
```

| URL | Description |
|------|-------------|
| `/accounts/login/` | User Login |
| `/accounts/logout/` | Logout |
| `/accounts/register/` | Register Customer/Driver |
| `/accounts/profile/` | View Profile |
| `/accounts/profile/edit/` | Edit Profile |
| `/accounts/change-password/` | Change Password |

---

# Dashboard

Base URL

```
/dashboard/
```

| URL | Description |
|------|-------------|
| `/dashboard/` | Redirects user to role-specific dashboard |

Roles Supported

- Administrator
- Customer
- Driver

---

# Customer Module

Base URL

```
/customers/
```

| URL | Description |
|------|-------------|
| `/customers/` | Customer List |
| `/customers/dashboard/` | Customer Dashboard |
| `/customers/create/` | Create Customer Profile |
| `/customers/<id>/` | Customer Details |
| `/customers/<id>/edit/` | Update Customer |
| `/customers/<id>/delete/` | Delete Customer |

---

# Driver Module

Base URL

```
/drivers/
```

| URL | Description |
|------|-------------|
| `/drivers/` | Driver List |
| `/drivers/dashboard/` | Driver Dashboard |
| `/drivers/create/` | Create Driver |
| `/drivers/<id>/` | Driver Details |
| `/drivers/<id>/edit/` | Edit Driver |
| `/drivers/<id>/delete/` | Delete Driver |
| `/drivers/status/` | Update Driver Availability |

Driver Status

- Available
- On Delivery
- Off Duty
- On Leave

---

# Shipment Module

Base URL

```
/shipments/
```

| URL | Description |
|------|-------------|
| `/shipments/` | Shipment List |
| `/shipments/create/` | Create Shipment |
| `/shipments/<id>/` | Shipment Details |
| `/shipments/<id>/edit/` | Update Shipment |
| `/shipments/<id>/delete/` | Delete Shipment |
| `/shipments/<id>/assign-driver/` | Assign Driver |
| `/shipments/<id>/driver-update/` | Driver Updates Shipment Status |
| `/shipments/<id>/status/<status>/` | Admin Updates Shipment Status |
| `/shipments/available-drivers/` | Available Drivers |
| `/shipments/<id>/label/` | Shipment Label |
| `/shipments/<id>/label/pdf/` | Download Shipment Label PDF |
| `/shipments/track/<tracking_number>/` | Track Shipment |

---

# Tracking Module

Base URL

```
/track/
```

| URL | Description |
|------|-------------|
| `/track/` | Public Tracking Search |
| `/track/?tracking_number=XXXX` | Shipment Timeline |

Tracking Status

- Created
- Pickup Assigned
- Picked Up
- In Transit
- Arrived At Hub
- Out For Delivery
- Delivered
- Cancelled
- Returned

---

# Routes Module

Base URL

```
/routes/
```

Functions

- Route Management
- Delivery Routes
- Logistics Planning

---

# Notifications Module

Base URL

```
/notifications/
```

Functions

- User Notifications
- Read/Unread Status
- Shipment Updates

---

# Contact Module

Base URL

```
/contact-us/
```

Admin Features

- View Contact Requests
- Reply to Requests
- Delete Requests
- Manage Status

Public Contact Page

```
/contact/
```

---

# Destination Module

Base URL

```
/locations/
```

Functions

- Destination Management
- City Management
- Delivery Locations

---

# Django Admin

```
/admin/
```

Administrator Features

- User Management
- Driver Management
- Customer Management
- Shipment Management
- Tracking Events
- Routes
- Notifications
- Contact Requests

---

# User Roles

## Administrator

Access

- Full System Access

Permissions

- Manage Everything
- Assign Drivers
- Update Shipment Status
- Dashboard Analytics
- Contact Management

---

## Customer

Permissions

- Register
- Login
- Create Shipments
- Track Shipments
- View Shipment History
- Contact Support
- Update Profile

---

## Driver

Permissions

- Login
- Dashboard
- View Assigned Shipments
- Update Shipment Status
- Change Availability
- Update Profile

---

# Authentication

The application uses Django Authentication.

Supported Features

- Login
- Logout
- Registration
- Password Change
- Role-Based Access Control

---

# Security Features

- CSRF Protection
- Django Authentication
- Role-Based Authorization
- Login Required Decorators
- Form Validation
- Protected Admin Panel

---

# Response Types

The project primarily returns:

- HTML Pages
- Redirect Responses
- Success Messages
- Validation Errors
- Django Templates

---

# Future API Enhancements

Future versions may include:

- REST API
- JWT Authentication
- Mobile App Support
- Live GPS Tracking API
- Delivery OTP API
- Payment Gateway API
- WebSocket Notifications

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

---

**ParcelPath API Documentation**

Version **1.0**