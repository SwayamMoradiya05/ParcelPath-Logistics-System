import random
import string
from datetime import datetime

from django.utils.text import slugify


def generate_tracking_number(prefix="TRK", length=8):
    digits = "".join(random.choices(string.digits, k=length))
    return f"{prefix}{digits}"


def generate_reference_code(prefix, length=6):
    chars = "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=length,
        )
    )
    return f"{prefix}-{chars}"


def generate_destination_code(city, sequence):
    prefix = (city[:3] if city else "DST").upper()
    return f"{prefix}{sequence:04d}"


def generate_route_code(sequence):
    return f"RTE-{sequence:05d}"


def generate_driver_code(sequence):
    return f"DRV-{sequence:05d}"


def format_phone_number(phone):
    if not phone:
        return ""

    phone = "".join(filter(str.isdigit, str(phone)))

    if len(phone) == 10:
        return f"+91-{phone}"

    return phone


def full_name(first_name, last_name):
    return f"{first_name} {last_name}".strip()


def create_slug(text):
    return slugify(text)


def current_timestamp():
    return datetime.now()


def yes_no(value):
    return "Yes" if value else "No"


def status_badge_class(status):
    mapping = {
        "Pending": "warning",
        "In Transit": "info",
        "Delivered": "success",
        "Cancelled": "danger",
        "Failed": "danger",
        "Active": "success",
        "Inactive": "secondary",
    }

    return mapping.get(status, "primary")


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default