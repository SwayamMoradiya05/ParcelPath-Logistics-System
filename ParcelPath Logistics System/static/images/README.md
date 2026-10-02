# ParcelPath Static Assets

This directory stores all static assets used throughout the ParcelPath application.

## Folder Structure

```
static/
│
├── css/
├── js/
├── images/
├── icons/
├── fonts/
└── uploads/
```

---

## images/

Store all application images here.

Recommended files:

```
logo.png
logo-white.png
favicon.ico

hero-banner.jpg
about-banner.jpg
contact-banner.jpg

login-bg.jpg
register-bg.jpg

default-user.png
default-driver.png

empty-box.png
404.png
500.png

tracking-banner.jpg
delivery-truck.png

invoice-logo.png
```

---

## icons/

Recommended SVG icons.

```
truck.svg
box.svg
customer.svg
driver.svg
location.svg
delivery.svg
notification.svg
dashboard.svg
settings.svg
```

---

## uploads/

Runtime uploaded files.

Example

```
proof_of_delivery/
driver_documents/
profile_photos/
shipment_images/
```

Do not commit uploaded files to GitHub.

Add uploads directory to .gitignore.

---

## fonts/

Custom fonts if required.

Example

```
Poppins-Regular.ttf
Poppins-Medium.ttf
Poppins-Bold.ttf
```

Google Fonts can also be used instead.

```
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```