from django.contrib import messages
from django.shortcuts import redirect


class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if not request.user.is_staff:
            messages.error(
                request,
                "You do not have permission to access this page.",
            )
            return redirect("dashboard:dashboard")

        return super().dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")

        if not request.user.is_superuser:
            messages.error(
                request,
                "Administrator access required.",
            )
            return redirect("dashboard:dashboard")

        return super().dispatch(request, *args, **kwargs)