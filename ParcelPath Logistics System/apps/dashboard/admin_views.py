from functools import wraps
from datetime import timedelta
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.forms import modelform_factory
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.models import (
    EmailVerificationToken,
    LoginHistory,
    PasswordResetToken,
    UserRole,
)
from apps.contact.models import Contact, ContactStatus
from apps.customers.models import Customer
from apps.destinations.models import Destination
from apps.drivers.models import Driver
from apps.notifications.models import Notification
from apps.routes.models import Route, RouteShipment
from apps.routes.services import RouteService
from apps.shipments.models import Payment, Shipment, ShipmentStatus
from apps.shipments.services import ShipmentService
from apps.tracking.models import TrackingEvent
from apps.drivers.services import DriverService


User = get_user_model()


# ============================================================
# ADMIN MODEL CONFIGURATION
# ============================================================

MODEL_CONFIG = {
    "users": (
        User,
        "Users",
        [
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "email_verified",
        ],
    ),

    "customers": (
        Customer,
        "Customers",
        [
            "customer_id",
            "company_name",
            "city",
            "state",
            "is_verified",
        ],
    ),

    "drivers": (
        Driver,
        "Drivers",
        [
            "driver_id",
            "user",
            "status",
            "is_verified",
            "vehicle_number",
        ],
    ),

    "shipments": (
        Shipment,
        "Shipments",
        [
            "tracking_number",
            "customer",
            "driver",
            "status",
            "shipping_cost",
            "created_at",
        ],
    ),

    "payments": (
        Payment,
        "Payments",
        [
            "shipment",
            "amount",
            "status",
            "razorpay_order_id",
            "razorpay_payment_id",
            "created_at",
        ],
    ),

    "routes": (
        Route,
        "Routes",
        [
            "route_code",
            "name",
            "driver",
            "status",
            "origin",
            "destination",
            "created_at",
        ],
    ),

    "route-shipments": (
        RouteShipment,
        "Route Shipments",
        [
            "route",
            "shipment",
            "stop_number",
            "delivered",
        ],
    ),

    "tracking": (
        TrackingEvent,
        "Tracking Events",
        [
            "shipment",
            "status",
            "location",
            "updated_by",
            "created_at",
        ],
    ),

    "notifications": (
        Notification,
        "Notifications",
        [
            "user",
            "title",
            "notification_type",
            "is_read",
            "created_at",
        ],
    ),

    "contacts": (
        Contact,
        "Contact Requests",
        [
            "name",
            "email",
            "category",
            "status",
            "created_at",
        ],
    ),

    "destinations": (
        Destination,
        "Destinations",
        [
            "destination_code",
            "name",
            "city",
            "state",
            "is_active",
        ],
    ),

    "login-history": (
        LoginHistory,
        "Login History",
        [
            "user",
            "ip_address",
            "successful",
            "login_time",
        ],
    ),

    "email-verification-tokens": (
        EmailVerificationToken,
        "Email Verification Tokens",
        [
            "user",
            "expires_at",
            "is_used",
            "created_at",
        ],
    ),

    "password-reset-tokens": (
        PasswordResetToken,
        "Password Reset Tokens",
        [
            "user",
            "expires_at",
            "is_used",
            "created_at",
        ],
    ),
}


# Fields which should not be edited through the generic dashboard form.
READ_ONLY_FIELDS = {
    "id",
    "created_at",
    "updated_at",
    "last_login",
    "last_seen",
    "login_time",
    "logout_time",
    "paid_at",
    "delivered_at",
    "proof_uploaded_at",
}


# ============================================================
# ADMIN PERMISSION
# ============================================================

def is_admin(user):
    """
    Centralized admin permission check.

    The custom dashboard accepts:
    - Django superusers
    - Django staff users
    - Users with the application's ADMIN role
    """

    if not user or not user.is_authenticated:
        return False

    return bool(
        user.is_superuser
        or user.is_staff
        or getattr(user, "role", None) == UserRole.ADMIN
    )


def admin_required(view):
    """
    Protect all custom-admin operations.

    Customer and driver users cannot access these views.
    """

    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):

        if not is_admin(request.user):
            return HttpResponseForbidden(
                "Access denied."
            )

        return view(
            request,
            *args,
            **kwargs,
        )

    return wrapped


# ============================================================
# GENERIC FORM HELPERS
# ============================================================

def _form_fields(model):
    """
    Return safe editable model fields for generic CRUD.
    """

    fields = []

    for field in model._meta.fields:

        if field.primary_key:
            continue

        if not field.editable:
            continue

        if field.name in READ_ONLY_FIELDS:
            continue

        fields.append(field.name)

    return fields


def _singular_title(title):
    """
    Convert simple plural model titles to readable singular titles.
    """

    if title.endswith("ies"):
        return f"{title[:-3]}y"

    if title.endswith("s"):
        return title[:-1]

    return title


def _display_value(obj, field_name):
    """
    Safely obtain a human-readable field value.
    """

    try:
        value = getattr(obj, field_name, "")
    except Exception:
        return "—"

    if callable(value):
        try:
            value = value()
        except TypeError:
            pass
        except Exception:
            return "—"

    if value is None or value == "":
        return "—"

    return value


def _get_model_config(model_key):
    """
    Safely resolve an admin model configuration.
    """

    config = MODEL_CONFIG.get(model_key)

    if not config:
        raise Http404("Admin module not found.")

    return config


# ============================================================
# USER FORM
# ============================================================

class DashboardUserForm(forms.ModelForm):
    """
    Custom user form because Django's normal UserCreationForm
    is not designed for this project's email-based authentication.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
        required=False,
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "new-password",
            }
        ),
        required=False,
    )

    class Meta:
        model = User

        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "profile_picture",
            "date_of_birth",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "email_verified",
            "phone_verified",
            "is_active",
            "is_staff",
            "is_superuser",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(
                    {
                        "class": "form-check-input",
                    }
                )

            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update(
                    {
                        "class": "form-select",
                    }
                )

            else:
                field.widget.attrs.update(
                    {
                        "class": "form-control",
                    }
                )

        if self.instance and self.instance.pk:
            self.fields["password1"].help_text = (
                "Leave blank to keep the current password."
            )
        else:
            self.fields["password1"].help_text = (
                "Required when creating a new user."
            )

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not self.instance.pk and not password1:
            self.add_error(
                "password1",
                "Password is required when creating a user.",
            )

        if password1 and password1 != password2:
            self.add_error(
                "password2",
                "Passwords do not match.",
            )

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            return email

        email = email.lower().strip()

        queryset = User.objects.filter(
            email=email,
        )

        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise forms.ValidationError(
                "A user with this email already exists."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        if user.email:
            user.email = user.email.lower().strip()

        if not user.username:
            user.username = (
                user.email.split("@", 1)[0]
            )

        password = self.cleaned_data.get(
            "password1"
        )

        if password:
            user.set_password(password)

        if commit:
            user.save()
            self.save_m2m()

        return user


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@admin_required
def dashboard(request):
    """
    Main custom ParcelPath Operations Dashboard.

    This view is ADMIN-only.
    Customer and driver dashboards are handled by
    apps/dashboard/views.py.

    Dashboard includes:
    - Operational KPIs
    - Revenue information
    - Customer and driver statistics
    - Shipment performance
    - Six-month revenue trend
    - Business overview chart data
    - Recent operational records
    """

    # ========================================================
    # SHIPMENT STATISTICS
    # ========================================================

    total_shipments = Shipment.objects.count()

    pending = Shipment.objects.filter(
        status=ShipmentStatus.PENDING,
    ).count()

    confirmed = Shipment.objects.filter(
        status=ShipmentStatus.CONFIRMED,
    ).count()

    pickup_assigned = Shipment.objects.filter(
        status=ShipmentStatus.PICKUP_ASSIGNED,
    ).count()

    picked_up = Shipment.objects.filter(
        status=ShipmentStatus.PICKED_UP,
    ).count()

    in_transit = Shipment.objects.filter(
        status=ShipmentStatus.IN_TRANSIT,
    ).count()

    out_for_delivery = Shipment.objects.filter(
        status=ShipmentStatus.OUT_FOR_DELIVERY,
    ).count()

    delivered = Shipment.objects.filter(
        status=ShipmentStatus.DELIVERED,
    ).count()

    cancelled = Shipment.objects.filter(
        status=ShipmentStatus.CANCELLED,
    ).count()

    returned = Shipment.objects.filter(
        status=ShipmentStatus.RETURNED,
    ).count()

    active_shipments = Shipment.objects.filter(
        status__in=[
            ShipmentStatus.CONFIRMED,
            ShipmentStatus.PICKUP_ASSIGNED,
            ShipmentStatus.PICKED_UP,
            ShipmentStatus.IN_TRANSIT,
            ShipmentStatus.OUT_FOR_DELIVERY,
        ],
    ).count()

    # ========================================================
    # REVENUE
    # ========================================================

    total_revenue = (
        Payment.objects.filter(
            status="PAID",
        )
        .aggregate(
            total=Sum("amount"),
        )["total"]
        or 0
    )

    # ========================================================
    # CUSTOMER STATISTICS
    # ========================================================

    total_customers = Customer.objects.count()

    verified_customers = Customer.objects.filter(
        is_verified=True,
    ).count()

    # ========================================================
    # DRIVER STATISTICS
    # ========================================================

    total_drivers = Driver.objects.count()

    verified_drivers = Driver.objects.filter(
        is_verified=True,
    ).count()

    available_drivers = Driver.objects.filter(
        status=Driver.Status.AVAILABLE,
    ).count()

    busy_drivers = Driver.objects.filter(
        status=Driver.Status.ON_DELIVERY,
    ).count()

    # ========================================================
    # USER STATISTICS
    # ========================================================

    total_users = User.objects.count()

    active_users = User.objects.filter(
        is_active=True,
    ).count()

    # ========================================================
    # NOTIFICATIONS / SUPPORT
    # ========================================================

    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False,
    ).count()

    pending_contacts = Contact.objects.filter(
        status=ContactStatus.PENDING,
    ).count()

    # ========================================================
    # SIX-MONTH REVENUE TREND
    # ========================================================

    revenue_labels = []
    revenue_data = []

    shipment_labels = []
    shipment_volume_data = []

    current_month = timezone.localtime().replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    month_cursor = current_month

    # Build the last 6 months from oldest -> newest.
    months = []

    for _ in range(6):
        months.append(month_cursor)

        previous_day = month_cursor - timedelta(days=1)

        month_cursor = previous_day.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    months.reverse()

    for month_start in months:

        # Calculate the beginning of the next month.
        if month_start.month == 12:
            next_month = month_start.replace(
                year=month_start.year + 1,
                month=1,
            )
        else:
            next_month = month_start.replace(
                month=month_start.month + 1,
            )

        month_revenue = (
            Payment.objects.filter(
                status="PAID",
                created_at__gte=month_start,
                created_at__lt=next_month,
            )
            .aggregate(
                total=Sum("amount"),
            )["total"]
            or 0
        )

        month_shipments = Shipment.objects.filter(
            created_at__gte=month_start,
            created_at__lt=next_month,
        ).count()

        revenue_labels.append(
            month_start.strftime("%b %Y")
        )

        revenue_data.append(
            float(month_revenue)
        )

        shipment_labels.append(
            month_start.strftime("%b")
        )

        shipment_volume_data.append(
            month_shipments
        )

    # ========================================================
    # SHIPMENT PERFORMANCE CHART
    # ========================================================

    shipment_status_labels = [
        "Pending",
        "Confirmed",
        "Pickup Assigned",
        "Picked Up",
        "In Transit",
        "Out for Delivery",
        "Delivered",
        "Cancelled",
        "Returned",
    ]

    shipment_status_data = [
        pending,
        confirmed,
        pickup_assigned,
        picked_up,
        in_transit,
        out_for_delivery,
        delivered,
        cancelled,
        returned,
    ]

    # ========================================================
    # BUSINESS OVERVIEW CHART
    # ========================================================

    business_overview_labels = [
        "Customers",
        "Drivers",
        "Verified Drivers",
        "Shipments",
        "Delivered",
        "Active Shipments",
    ]

    business_overview_data = [
        total_customers,
        total_drivers,
        verified_drivers,
        total_shipments,
        delivered,
        active_shipments,
    ]

    # ========================================================
    # RECENT SHIPMENTS
    # ========================================================

    recent_shipments = (
        Shipment.objects
        .select_related(
            "customer",
            "driver",
        )
        .order_by("-created_at")[:10]
    )

    # ========================================================
    # RECENT PAYMENTS
    # ========================================================

    recent_payments = (
        Payment.objects
        .select_related("shipment")
        .order_by("-created_at")[:5]
    )

    # ========================================================
    # RECENT CONTACTS
    # ========================================================

    recent_contacts = (
        Contact.objects
        .select_related("user")
        .order_by("-created_at")[:5]
    )

    # ========================================================
    # DASHBOARD CONTEXT
    # ========================================================

    context = {

        # ----------------------------------------------------
        # Shipment KPIs
        # ----------------------------------------------------

        "total_shipments": total_shipments,

        "pending": pending,
        "confirmed": confirmed,
        "pickup_assigned": pickup_assigned,
        "picked_up": picked_up,

        "active": active_shipments,

        "in_transit": in_transit,
        "out_for_delivery": out_for_delivery,
        "delivered": delivered,
        "cancelled": cancelled,
        "returned": returned,

        # ----------------------------------------------------
        # Revenue
        # ----------------------------------------------------

        "total_revenue": total_revenue,

        # ----------------------------------------------------
        # Customers
        # ----------------------------------------------------

        "total_customers": total_customers,
        "verified_customers": verified_customers,

        # ----------------------------------------------------
        # Drivers
        # ----------------------------------------------------

        "total_drivers": total_drivers,
        "verified_drivers": verified_drivers,
        "available_drivers": available_drivers,
        "busy_drivers": busy_drivers,

        # ----------------------------------------------------
        # Users
        # ----------------------------------------------------

        "total_users": total_users,
        "active_users": active_users,

        # ----------------------------------------------------
        # Notifications / Support
        # ----------------------------------------------------

        "unread_notifications": unread_notifications,
        "pending_contacts": pending_contacts,

        # ----------------------------------------------------
        # Recent records
        # ----------------------------------------------------

        "recent_shipments": recent_shipments,
        "recent_payments": recent_payments,
        "recent_contacts": recent_contacts,

        # ----------------------------------------------------
        # Chart 1 - Revenue Trend
        # ----------------------------------------------------

        "revenue_labels": revenue_labels,
        "revenue_data": revenue_data,

        # Shipment volume is also available if we want
        # to display it later without another database query.
        "shipment_volume_data": shipment_volume_data,
        "shipment_volume_labels": shipment_labels,

        # ----------------------------------------------------
        # Chart 2 - Shipment Performance
        # ----------------------------------------------------

        "shipment_status_labels": shipment_status_labels,
        "shipment_status_data": shipment_status_data,

        # ----------------------------------------------------
        # Chart 3 - Business Overview
        # ----------------------------------------------------

        "business_overview_labels": business_overview_labels,
        "business_overview_data": business_overview_data,
    }

    return render(
        request,
        "dashboard/admin_dashboard.html",
        context,
    )

# ============================================================
# GENERIC MODEL LIST
# ============================================================

@admin_required
def model_list(request, model_key):

    model, title, default_columns = (
        _get_model_config(model_key)
    )

    queryset = model.objects.all()

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    query = request.GET.get(
        "q",
        "",
    ).strip()

    if query:

        conditions = Q()

        for field in model._meta.fields:

            internal_type = field.get_internal_type()

            if internal_type not in {
                "CharField",
                "TextField",
                "EmailField",
                "SlugField",
            }:
                continue

            conditions |= Q(
                **{
                    f"{field.name}__icontains": query,
                }
            )

        if conditions:
            queryset = queryset.filter(
                conditions
            )

    # --------------------------------------------------------
    # Status filter
    # --------------------------------------------------------

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if status and any(
        field.name == "status"
        for field in model._meta.fields
    ):
        valid_statuses = {
            value
            for value, _ in model._meta.get_field(
                "status"
            ).choices
        }

        if status in valid_statuses:
            queryset = queryset.filter(
                status=status
            )

    # --------------------------------------------------------
    # Boolean filters
    # --------------------------------------------------------

    is_active = request.GET.get(
        "is_active",
        "",
    ).strip()

    if (
        is_active in {"true", "false"}
        and any(
            field.name == "is_active"
            for field in model._meta.fields
        )
    ):
        queryset = queryset.filter(
            is_active=(
                is_active == "true"
            )
        )

    # --------------------------------------------------------
    # Ordering
    # --------------------------------------------------------

    order = request.GET.get(
        "order",
        "",
    ).strip()

    valid_order_fields = {
        field.name
        for field in model._meta.fields
    }

    if (
        order
        and order.lstrip("-")
        in valid_order_fields
    ):
        queryset = queryset.order_by(
            order
        )

    else:

        ordering = getattr(
            model._meta,
            "ordering",
            None,
        )

        if ordering:
            queryset = queryset.order_by(
                *ordering
            )

        else:
            queryset = queryset.order_by(
                "-pk"
            )

    # --------------------------------------------------------
    # Related objects
    # --------------------------------------------------------

    select_related_fields = []

    for field in model._meta.fields:

        remote = getattr(
            field,
            "remote_field",
            None,
        )

        if (
            remote
            and not getattr(
                remote,
                "many_to_many",
                False,
            )
        ):
            select_related_fields.append(
                field.name
            )

    if select_related_fields:

        queryset = queryset.select_related(
            *select_related_fields
        )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    paginator = Paginator(
        queryset,
        25,
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {
        "title": title,
        "model_key": model_key,
        "columns": default_columns,
        "objects": page_obj,
        "page_obj": page_obj,
        "query": query,
        "selected_status": status,
        "selected_is_active": is_active,
        "total_count": paginator.count,
    }

    return render(
        request,
        "dashboard/admin_list.html",
        context,
    )


# ============================================================
# GENERIC CREATE
# ============================================================

@admin_required
def model_create(request, model_key):

    model, title, _ = (
        _get_model_config(model_key)
    )

    fields = _form_fields(model)

    Form = (
        DashboardUserForm
        if model is User
        else modelform_factory(
            model,
            fields=fields,
        )
    )

    form = Form(
        request.POST or None,
        request.FILES or None,
    )
    # --------------------------------------------------------
# Shipment driver filter
# --------------------------------------------------------
    if model is Shipment and "driver" in form.fields:
        form.fields["driver"].queryset = (
            Driver.objects.filter(
                status=Driver.Status.AVAILABLE,
                is_verified=True,
            )
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
            )
        )
    if request.method == "POST":

        if form.is_valid():

            try:

                with transaction.atomic():

                    obj = form.save(
                        commit=False
                    )

                    # Automatically associate
                    # admin as creator where the
                    # model supports created_by.
                    if (
                        model is Shipment
                        and hasattr(
                            obj,
                            "created_by",
                        )
                        and not obj.created_by_id
                    ):
                        obj.created_by = (
                            request.user
                        )

                    obj.save()

                    if hasattr(
                        form,
                        "save_m2m",
                    ):
                        form.save_m2m()

                messages.success(
                    request,
                    (
                        f"{_singular_title(title)} "
                        "created successfully."
                    ),
                )

                return redirect(
                    "dashboard:model_detail",
                    model_key=model_key,
                    pk=obj.pk,
                )

            except Exception as exc:

                messages.error(
                    request,
                    f"Unable to create record: {exc}",
                )

    return render(
        request,
        "dashboard/admin_form.html",
        {
            "form": form,
            "title": (
                f"Create "
                f"{_singular_title(title)}"
            ),
            "model_key": model_key,
            "is_create": True,
        },
    )


# ============================================================
# GENERIC UPDATE
# ============================================================

@admin_required
def model_update(
    request,
    model_key,
    pk,
):
    model, title, _ = (
        _get_model_config(model_key)
    )

    obj = get_object_or_404(
        model,
        pk=pk,
    )

    fields = _form_fields(model)

    Form = (
        DashboardUserForm
        if model is User
        else modelform_factory(
            model,
            fields=fields,
        )
    )

    form = Form(
        request.POST or None,
        request.FILES or None,
        instance=obj,
    )

    # --------------------------------------------------------
    # Shipment driver filter
    # --------------------------------------------------------
    if model is Shipment and "driver" in form.fields:
        form.fields["driver"].queryset = (
            Driver.objects.filter(
                status=Driver.Status.AVAILABLE,
                is_verified=True,
            )
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
            )
        )

    if request.method == "POST":

        if form.is_valid():

            try:

                with transaction.atomic():
                    form.save()

                messages.success(
                    request,
                    (
                        f"{_singular_title(title)} "
                        "updated successfully."
                    ),
                )

                return redirect(
                    "dashboard:model_detail",
                    model_key=model_key,
                    pk=obj.pk,
                )

            except Exception as exc:

                messages.error(
                    request,
                    f"Unable to update record: {exc}",
                )

    return render(
        request,
        "dashboard/admin_form.html",
        {
            "form": form,
            "title": (
                f"Edit "
                f"{_singular_title(title)}"
            ),
            "model_key": model_key,
            "is_create": False,
            "object": obj,
        },
    )


# ============================================================
# GENERIC DETAIL
# ============================================================

@admin_required
def model_detail(
    request,
    model_key,
    pk,
):

    model, title, columns = (
        _get_model_config(model_key)
    )

    obj = get_object_or_404(
        model,
        pk=pk,
    )

    fields = []

    for field in model._meta.fields:

        fields.append(
            (
                field.verbose_name.title(),
                _display_value(
                    obj,
                    field.name,
                ),
            )
        )

    context = {
        "title": _singular_title(title),
        "model_key": model_key,
        "object": obj,
        "fields": fields,
        "columns": columns,
    }

    # --------------------------------------------------------
    # Shipment-specific information
    # --------------------------------------------------------

    if model is Shipment:

        context["status_choices"] = (
            ShipmentStatus.choices
        )

        context["available_drivers"] = (
            Driver.objects.filter(
                status=Driver.Status.AVAILABLE,
                is_verified=True,
            )
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
            )
        )

        context["payments"] = (
            obj.payments
            .all()
            .order_by("-created_at")
        )

        context["tracking_events"] = (
            obj.tracking_events
            .select_related("updated_by")
            .order_by("-created_at")
        )

    # --------------------------------------------------------
    # Route-specific information
    # --------------------------------------------------------

    if model is Route:

        context["route_shipments"] = (
            obj.route_shipments
            .select_related(
                "shipment",
                "shipment__customer",
            )
            .order_by(
                "stop_number"
            )
        )

    # --------------------------------------------------------
    # Customer-specific information
    # --------------------------------------------------------

    if model is Customer:

        context["customer_shipments"] = (
            obj.shipments
            .select_related("driver")
            .order_by("-created_at")[:20]
        )

    # --------------------------------------------------------
    # Driver-specific information
    # --------------------------------------------------------

    if model is Driver:

        context["driver_shipments"] = (
            obj.shipments
            .select_related("customer")
            .order_by("-created_at")[:20]
        )

    return render(
        request,
        "dashboard/admin_detail.html",
        context,
    )


# ============================================================
# GENERIC DELETE
# ============================================================

@admin_required
@require_POST
def model_delete(
    request,
    model_key,
    pk,
):

    model, title, _ = (
        _get_model_config(model_key)
    )

    obj = get_object_or_404(
        model,
        pk=pk,
    )

    # Never allow an administrator
    # to delete their own currently
    # authenticated account.
    if (
        model is User
        and obj.pk == request.user.pk
    ):
        messages.error(
            request,
            "You cannot delete your own admin account.",
        )

        return redirect(
            "dashboard:model_detail",
            model_key=model_key,
            pk=pk,
        )

    try:

        with transaction.atomic():
            obj.delete()

        messages.success(
            request,
            (
                f"{_singular_title(title)} "
                "deleted successfully."
            ),
        )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to delete record: {exc}",
        )

        return redirect(
            "dashboard:model_detail",
            model_key=model_key,
            pk=pk,
        )

    return redirect(
        "dashboard:model_list",
        model_key=model_key,
    )


# ============================================================
# SHIPMENT STATUS
# ============================================================

@admin_required
@require_POST
def shipment_status(
    request,
    pk,
    status,
):

    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "customer",
            "driver",
            "created_by",
        ),
        pk=pk,
    )

    valid_statuses = {
        value
        for value, _ in ShipmentStatus.choices
    }

    if status not in valid_statuses:

        messages.error(
            request,
            "Invalid shipment status.",
        )

        return redirect(
            "dashboard:model_detail",
            model_key="shipments",
            pk=pk,
        )

    try:

        with transaction.atomic():

            ShipmentService.update_status(
                shipment,
                status,
            )

        messages.success(
            request,
            (
                f"Shipment "
                f"{shipment.tracking_number} "
                f"updated to "
                f"{shipment.get_status_display()}."
            ),
        )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to update shipment: {exc}",
        )

    return redirect(
        "dashboard:model_detail",
        model_key="shipments",
        pk=pk,
    )


# ============================================================
# SHIPMENT DRIVER ASSIGNMENT
# ============================================================

@admin_required
@require_POST
def shipment_assign_driver(
    request,
    pk,
):

    shipment = get_object_or_404(
        Shipment,
        pk=pk,
    )

    driver_id = request.POST.get(
        "driver_id"
    )

    if not driver_id:

        messages.error(
            request,
            "Please select a driver.",
        )

        return redirect(
            "dashboard:model_detail",
            model_key="shipments",
            pk=pk,
        )

    driver = get_object_or_404(
        Driver.objects.select_related("user"),
        pk=driver_id,
        status=Driver.Status.AVAILABLE,
        is_verified=True,
    )

    try:

        with transaction.atomic():

            ShipmentService.assign_driver(
                shipment,
                driver,
            )

        driver_name = (
            getattr(
                driver.user,
                "full_name",
                None,
            )
            or driver.user.email
        )

        messages.success(
            request,
            (
                f"Driver '{driver_name}' "
                "assigned successfully."
            ),
        )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to assign driver: {exc}",
        )

    return redirect(
        "dashboard:model_detail",
        model_key="shipments",
        pk=pk,
    )


# ============================================================
# DRIVER VERIFICATION
# ============================================================

@admin_required
@require_POST
def driver_verify(
    request,
    pk,
):

    driver = get_object_or_404(
        Driver,
        pk=pk,
    )

    try:

        if driver.is_verified:

            DriverService.unverify(
                driver
            )

            messages.success(
                request,
                "Driver verification removed.",
            )

        else:

            DriverService.verify(
                driver
            )

            messages.success(
                request,
                "Driver verified successfully.",
            )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to update driver verification: {exc}",
        )

    return redirect(
        "dashboard:model_detail",
        model_key="drivers",
        pk=pk,
    )


# ============================================================
# CONTACT ACTIONS
# ============================================================

@admin_required
@require_POST
def contact_action(
    request,
    pk,
    action,
):

    contact = get_object_or_404(
        Contact,
        pk=pk,
    )

    try:

        if action == "progress":

            contact.status = (
                ContactStatus.IN_PROGRESS
            )

            update_fields = ["status"]

            if hasattr(
                contact,
                "updated_at",
            ):
                update_fields.append(
                    "updated_at"
                )

            contact.save(
                update_fields=update_fields
            )

        elif action == "resolve":

            if hasattr(
                contact,
                "admin_reply",
            ):
                contact.admin_reply = (
                    request.POST.get(
                        "reply",
                        "",
                    ).strip()
                )

            if hasattr(
                contact,
                "replied_by",
            ):
                contact.replied_by = (
                    request.user
                )

            if hasattr(
                contact,
                "replied_at",
            ):
                contact.replied_at = (
                    timezone.now()
                )

            contact.status = (
                ContactStatus.RESOLVED
            )

            update_fields = ["status"]

            for field_name in (
                "admin_reply",
                "replied_by",
                "replied_at",
            ):
                if hasattr(
                    contact,
                    field_name,
                ):
                    update_fields.append(
                        field_name
                    )

            if hasattr(
                contact,
                "updated_at",
            ):
                update_fields.append(
                    "updated_at"
                )

            contact.save(
                update_fields=update_fields
            )

        elif action == "close":

            contact.status = (
                ContactStatus.CLOSED
            )

            update_fields = ["status"]

            if hasattr(
                contact,
                "updated_at",
            ):
                update_fields.append(
                    "updated_at"
                )

            contact.save(
                update_fields=update_fields
            )

        else:
            raise Http404(
                "Invalid contact action."
            )

        messages.success(
            request,
            "Contact request updated successfully.",
        )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to update contact request: {exc}",
        )

    return redirect(
        "dashboard:model_detail",
        model_key="contacts",
        pk=pk,
    )


# ============================================================
# NOTIFICATION READ / UNREAD
# ============================================================

@admin_required
@require_POST
def notification_read(
    request,
    pk,
):

    notification = get_object_or_404(
        Notification,
        pk=pk,
    )

    try:

        if notification.is_read:

            notification.mark_as_unread()

            messages.success(
                request,
                "Notification marked as unread.",
            )

        else:

            notification.mark_as_read()

            messages.success(
                request,
                "Notification marked as read.",
            )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to update notification: {exc}",
        )

    return redirect(
        "dashboard:model_detail",
        model_key="notifications",
        pk=pk,
    )


# ============================================================
# ROUTE OPERATIONS
# ============================================================

@admin_required
@require_POST
def route_action(
    request,
    pk,
    action,
):

    route = get_object_or_404(
        Route,
        pk=pk,
    )

    try:

        if action == "start":

            from apps.routes.models import RouteStatus

            route.status = (
                RouteStatus.STARTED
            )

            update_fields = ["status"]

            if hasattr(
                route,
                "updated_at",
            ):
                update_fields.append(
                    "updated_at"
                )

            route.save(
                update_fields=update_fields
            )

        elif action == "complete":

            RouteService.complete_route(
                route
            )

        elif action == "cancel":

            from apps.routes.models import RouteStatus

            route.status = (
                RouteStatus.CANCELLED
            )

            update_fields = ["status"]

            if hasattr(
                route,
                "updated_at",
            ):
                update_fields.append(
                    "updated_at"
                )

            route.save(
                update_fields=update_fields
            )

            if route.driver:

                route.driver.status = (
                    Driver.Status.AVAILABLE
                )

                route.driver.save(
                    update_fields=[
                        "status",
                    ]
                )

        elif action == "assign":

            driver_id = request.POST.get(
                "driver_id"
            )

            if not driver_id:
                raise ValueError(
                    "Please select a driver."
                )

            driver = get_object_or_404(
                Driver,
                pk=driver_id,
                is_verified=True,
                status=Driver.Status.AVAILABLE,
            )

            RouteService.assign_driver(
                route,
                driver,
            )

        elif action == "add-shipment":

            shipment_id = request.POST.get(
                "shipment_id"
            )

            if not shipment_id:
                raise ValueError(
                    "Please select a shipment."
                )

            shipment = get_object_or_404(
                Shipment,
                pk=shipment_id,
            )

            RouteService.add_shipment(
                route,
                shipment,
            )

        elif action == "remove-shipment":

            shipment_id = request.POST.get(
                "shipment_id"
            )

            if not shipment_id:
                raise ValueError(
                    "Please select a shipment."
                )

            shipment = get_object_or_404(
                Shipment,
                pk=shipment_id,
            )

            RouteService.remove_shipment(
                route,
                shipment,
            )

        else:
            raise Http404(
                "Invalid route action."
            )

        messages.success(
            request,
            "Route updated successfully.",
        )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to update route: {exc}",
        )

    return redirect(
        "dashboard:model_detail",
        model_key="routes",
        pk=pk,
    )