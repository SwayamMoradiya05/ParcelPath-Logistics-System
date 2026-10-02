from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import UserRole


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")

            if request.user.role not in roles:
                messages.error(
                    request,
                    "You do not have permission to access this page.",
                )
                return redirect("dashboard:dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def admin_required(view_func):
    return role_required(UserRole.ADMIN)(view_func)


def customer_required(view_func):
    return role_required(UserRole.CUSTOMER)(view_func)


def driver_required(view_func):
    return role_required(UserRole.DRIVER)(view_func)