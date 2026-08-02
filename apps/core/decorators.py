from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if not request.user.is_staff:
            messages.error(
                request,
                "You do not have permission to access this page.",
            )
            return redirect("dashboard:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


def superuser_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if not request.user.is_superuser:
            messages.error(
                request,
                "Administrator access required.",
            )
            return redirect("dashboard:dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper