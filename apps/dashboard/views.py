from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from apps.accounts.models import UserRole


@login_required
def dashboard(request):
    """Role-aware dashboard entry point.

    The existing customer and driver dashboards remain untouched.
    Only ADMIN/STAFF/SUPERUSER users are sent to the new operations dashboard.
    """
    user = request.user

    if user.is_superuser or user.is_staff or user.role == UserRole.ADMIN:
        from .admin_views import dashboard as admin_dashboard
        return admin_dashboard(request)

    if user.role == UserRole.CUSTOMER:
        return redirect("customers:dashboard")

    if user.role == UserRole.DRIVER:
        return redirect("drivers:dashboard")

    return redirect("home")
