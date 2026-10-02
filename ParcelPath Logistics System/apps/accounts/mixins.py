from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import UserRole


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in self.allowed_roles:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = [UserRole.ADMIN]


class CustomerRequiredMixin(RoleRequiredMixin):
    allowed_roles = [UserRole.CUSTOMER]


class DriverRequiredMixin(RoleRequiredMixin):
    allowed_roles = [UserRole.DRIVER]