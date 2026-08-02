# ParcelPath Database Documentation

## Overview

ParcelPath uses a relational database managed by Django ORM to store users, shipments, tracking events, drivers, customers, notifications, routes, and contact requests.

The database is normalized to reduce redundancy while maintaining high performance through indexes and foreign-key relationships.

---

# Database Engine

Development

- SQLite

Production (Recommended)

- PostgreSQL
- MySQL

---

# Database Architecture

```
User
 │
 ├──────────────┐
 │              │
Customer      Driver
 │              │
 └──────┐   ┌───┘
        │   │
     Shipment
        │
        │
 TrackingEvent

Shipment
    │
    └────────── Route

User
    │
 Notification

User
    │
 Contact
```

---

# Tables

## User

Stores all system users.

Primary Key

```
id
```

Important Fields

- first_name
- last_name
- email
- phone
- role
- profile_picture
- address
- city
- state
- country
- postal_code
- email_verified
- phone_verified
- is_online
- last_seen

Relationships

- One User → One Customer
- One User → One Driver
- One User → Many Notifications
- One User → Many Contact Requests

---

## Customer

Stores customer information.

Primary Key

```
id
```

Foreign Keys

```
user → User
```

Important Fields

- customer_id
- company_name
- gst_number
- city
- state
- country
- postal_code
- total_shipments
- completed_shipments
- cancelled_shipments
- is_verified

Relationships

Customer

↓

Many Shipments

---

## Driver

Stores delivery driver information.

Primary Key

```
id
```

Foreign Key

```
user → User
```

Important Fields

- driver_id
- vehicle_number
- vehicle_type
- vehicle_capacity
- license_number
- status
- rating
- current_latitude
- current_longitude
- total_deliveries
- successful_deliveries
- cancelled_deliveries
- is_verified

Driver Status

- Available
- On Delivery
- Off Duty
- On Leave

Relationships

Driver

↓

Many Shipments

---

## Shipment

Central table of the application.

Primary Key

```
id
```

Foreign Keys

```
customer → Customer

driver → Driver

created_by → User
```

Important Fields

- tracking_number
- sender_name
- sender_phone
- sender_address
- receiver_name
- receiver_phone
- receiver_address
- package_type
- weight
- dimensions
- declared_value
- shipping_cost
- expected_delivery
- delivered_at
- remarks
- status

Shipment Status

- Created
- Pickup Assigned
- Picked Up
- In Transit
- Arrived at Hub
- Out For Delivery
- Delivered
- Cancelled
- Returned

Relationships

Shipment

↓

Many Tracking Events

Shipment

↓

One Driver

Shipment

↓

One Customer

---

## Tracking Event

Stores shipment movement history.

Primary Key

```
id
```

Foreign Keys

```
shipment → Shipment

updated_by → User
```

Important Fields

- status
- location
- description
- latitude
- longitude
- created_at

Relationships

Many Tracking Events

↓

One Shipment

---

## Route

Stores logistics routes.

Primary Key

```
id
```

Important Fields

- origin
- destination
- estimated_distance
- estimated_duration
- status

Relationships

One Route

↓

Many Shipments

---

## Notification

Stores notifications sent to users.

Primary Key

```
id
```

Foreign Key

```
user → User
```

Important Fields

- title
- message
- is_read
- created_at

Relationships

One User

↓

Many Notifications

---

## Contact

Stores contact form submissions.

Primary Key

```
id
```

Foreign Key

```
user → User (Optional)
```

Important Fields

- name
- email
- phone
- subject
- message
- category
- status
- admin_reply
- replied_by
- replied_at

Categories

- General Inquiry
- Shipment
- Delivery
- Payment
- Complaint
- Feedback
- Other

Status

- Pending
- In Progress
- Resolved
- Closed

---

# Relationships Summary

```
User
 ├── Customer
 ├── Driver
 ├── Notification
 └── Contact

Customer
 └── Shipment

Driver
 └── Shipment

Shipment
 ├── TrackingEvent
 └── Route
```

---

# Indexing

ParcelPath uses database indexes to improve query performance.

Indexed fields include:

- Email
- Tracking Number
- Driver Status
- Shipment Status
- Customer ID
- Driver ID
- Created Date
- Tracking Event Date
- Notification Status
- Contact Status

---

# ORM Relationships

Examples

Customer → Shipments

```python
customer.shipments.all()
```

Shipment → Tracking

```python
shipment.tracking_events.all()
```

Driver → Shipments

```python
driver.shipments.all()
```

User → Notifications

```python
user.notifications.all()
```

---

# Database Features

- Relational database design
- Foreign key constraints
- Indexed search fields
- Django ORM
- Automatic timestamps
- Data validation
- Role-based relationships
- Shipment tracking history
- Driver availability management
- Customer shipment statistics

---

# Future Improvements

- Multi-warehouse support
- Shipment insurance records
- Payment transactions
- Audit logs
- GPS history
- Live driver locations
- Delivery proof images
- OTP delivery verification

---

**ParcelPath Database Documentation**