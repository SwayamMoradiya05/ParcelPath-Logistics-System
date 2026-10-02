import secrets
import string


def generate_username(first_name="", last_name=""):
    base = (
        f"{first_name}{last_name}"
        .replace(" ", "")
        .lower()
    )

    if not base:
        base = "user"

    suffix = "".join(
        secrets.choice(string.digits)
        for _ in range(5)
    )

    return f"{base}{suffix}"


def generate_reference(prefix):
    token = secrets.token_hex(4).upper()
    return f"{prefix}-{token}"


def generate_otp(length=6):
    return "".join(
        secrets.choice(string.digits)
        for _ in range(length)
    )


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def is_image(filename):
    extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
    )

    return filename.lower().endswith(extensions)