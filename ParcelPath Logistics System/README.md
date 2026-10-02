# 🚚 ParcelPath - Smart Logistics & Parcel Delivery System

# 📌 Overview

ParcelPath is a full-stack logistics management system designed to streamline parcel shipping, driver assignment, shipment tracking, and customer management.

The system supports three different user roles:

- 👨‍💼 Administrator
- 👤 Customer
- 🚚 Driver

Each role has its own dashboard and permissions, ensuring secure and efficient management of logistics operations.

---

# ✨ Features

## 👨‍💼 Administrator

- Dashboard Analytics
- Customer Management
- Driver Management
- Shipment Management
- Route Management
- Driver Assignment
- Shipment Status Updates
- Contact Request Management
- Notification Management
- Shipment Labels
- Driver Availability Monitoring

---

## 👤 Customer

- User Registration
- Secure Login
- Customer Dashboard
- Create Shipments
- Shipment Tracking
- Shipment History
- Profile Management
- Contact Support

---

## 🚚 Driver

- Driver Dashboard
- Assigned Shipments
- Update Shipment Status
- Delivery History
- Revenue Statistics
- Toggle Availability
- Profile Management

Driver Availability:

- ✅ Available
- 🚚 On Delivery
- 🌙 Off Duty
- 🌴 On Leave

Drivers marked as **Off Duty**, **On Leave**, or **On Delivery** are automatically excluded from shipment assignment.

---

# 📦 Shipment Workflow

```text
Shipment Created
        │
        ▼
Pickup Assigned
        │
        ▼
Picked Up
        │
        ▼
In Transit
        │
        ▼
Arrived at Hub
        │
        ▼
Out For Delivery
        │
        ▼
Delivered
```

---

# 🏗 Project Structure

```text
ParcelPath/

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
├── requirements.txt
├── manage.py
└── README.md
```

---

# 🛠 Technology Stack

## Backend

- Python
- Django

## Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

## Database

- SQLite (Development)

## Version Control

- Git
- GitHub

---

# 🔐 User Roles

| Role | Access |
|------|--------|
| Administrator | Full System Access |
| Customer | Shipment Management & Tracking |
| Driver | Assigned Deliveries & Status Updates |

---

# 📊 Major Modules

- Authentication
- Customer Management
- Driver Management
- Shipment Management
- Route Management
- Tracking System
- Notification System
- Contact Management
- Dashboard Analytics

---

# 📷 Screenshots

Create a folder named:

```
screenshots/
```

Recommended screenshots:

- Home Page
- Admin Dashboard
- Customer Dashboard
- Driver Dashboard
- Shipment Tracking
- Shipment Details
- Admin Panel
- Contact Page

Example:

```text
screenshots/
    home.png
    admin_dashboard.png
    customer_dashboard.png
    driver_dashboard.png
    tracking.png
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ParcelPath.git
```

Navigate into the project

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

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Create admin

```bash
python manage.py createsuperuser
```

Run server

```bash
python manage.py runserver
```

Visit

```
http://127.0.0.1:8000/
```

---

# 📚 Documentation

Complete project documentation is available inside the `docs/` folder.

- Installation Guide
- Database Documentation
- API Documentation
- Entity Relationship Diagram (ERD)

---

# 🔒 Security Features

- Django Authentication
- Role-Based Authorization
- CSRF Protection
- Form Validation
- Protected Admin Panel
- Secure Password Hashing

---

# 📈 Future Improvements

- REST API
- Mobile Application
- Live GPS Tracking
- Payment Gateway Integration
- OTP Delivery Verification
- Email Notifications
- SMS Notifications
- QR Code Based Parcel Tracking
- AI-Based Route Optimization

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Added new feature"
```

4. Push the branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Developer

**Swayam Moradiya**

- GitHub: https://github.com/SwayamMoradiya05
- LinkedIn: https://www.linkedin.com/in/swayam-moradiya/

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It helps others discover the project and supports future development.

---

<div align="center">

**ParcelPath — Delivering Logistics with Precision 🚚**

</div>
