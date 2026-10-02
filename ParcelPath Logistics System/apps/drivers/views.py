from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum
from django.utils import timezone
from apps.accounts.models import UserRole

from .forms import DriverForm
from .models import Driver
from django.db.models import Count
from apps.shipments.models import Shipment
from apps.shipments.models import ShipmentStatus

def can_manage_driver(user, driver=None):
    """
    Returns True if the user can manage the driver profile.
    """

    if not user.is_authenticated:
        return False

    if user.role == UserRole.ADMIN:
        return True

    if driver and driver.user == user:
        return True

    return False


@login_required
def driver_list(request):
    search = request.GET.get("search", "").strip()

    drivers = (
        Driver.objects.select_related("user")
        .only(
            "id",
            "driver_id",
            "status",
            "vehicle_type",
            "vehicle_number",
            "vehicle_model",
            "rating",
            "is_verified",
            "total_deliveries",
            "successful_deliveries",
            "cancelled_deliveries",
            "user__first_name",
            "user__last_name",
            "user__email",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    if request.user.role != UserRole.ADMIN:
        drivers = drivers.filter(
            user=request.user,
        )

    if search:
        drivers = drivers.filter(
            Q(driver_id__icontains=search)
            | Q(vehicle_number__icontains=search)
            | Q(vehicle_model__icontains=search)
            | Q(license_number__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__email__icontains=search)
        )

    paginator = Paginator(drivers, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "drivers/driver_list.html",
        {
            "drivers": page_obj,
            "page_obj": page_obj,
            "search": search,
            "total_drivers": drivers.count(),
        },
    )


@login_required
def driver_detail(request, pk):
    driver = get_object_or_404(
    Driver,
    pk=pk,
    user=request.user,
)

    if not can_manage_driver(
        request.user,
        driver,
    ):
        return HttpResponseForbidden(
            "You do not have permission to view this driver."
        )

    return render(
        request,
        "drivers/driver_detail.html",
        {
            "driver": driver,
        },
    )
@login_required
def driver_create(request):
    if request.user.role != UserRole.DRIVER:
        return HttpResponseForbidden(
            "Only drivers can create a driver profile."
        )

    if Driver.objects.filter(user=request.user).exists():
        messages.warning(
            request,
            "You already have a driver profile.",
        )

        return redirect(
            "drivers:driver_detail",
            request.user.driver_profile.pk,
        )

    form = DriverForm(
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    driver = form.save(commit=False)

                    if Driver.objects.filter(user=request.user).exists():
                        messages.warning(
                            request,
                            "You already have a driver profile."
                        )
                        return redirect("drivers:driver_detail")

                    driver.user = request.user
                    driver.save()
                messages.success(
                    request,
                    "Driver profile created successfully.",
                )

                return redirect(
                    "drivers:driver_detail",
                    driver.pk,
                )

            except Exception:
                messages.error(
                    request,
                    "Unable to create driver profile.",
                )

    return render(
        request,
        "drivers/driver_form.html",
        {
            "form": form,
            "is_create": True,
        },
    )


@login_required
def driver_update(request, pk):
    driver = get_object_or_404(
    Driver,
    pk=pk,
    user=request.user,
)

    if not can_manage_driver(
        request.user,
        driver,
    ):
        return HttpResponseForbidden(
            "You do not have permission to update this driver."
        )

    form = DriverForm(
        request.POST or None,
        request.FILES or None,
        instance=driver,
    )

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

                messages.success(
                    request,
                    "Driver updated successfully.",
                )

                return redirect(
                    "drivers:driver_detail",
                    driver.pk,
                )

            except Exception:
                messages.error(
                    request,
                    "Unable to update driver profile.",
                )

    return render(
        request,
        "drivers/driver_form.html",
        {
            "form": form,
            "driver": driver,
            "is_create": False,
        },
    )


@login_required
def driver_delete(request, pk):
    driver = get_object_or_404(
    Driver,
    pk=pk,
    user=request.user,
)

    if not can_manage_driver(
        request.user,
        driver,
    ):
        return HttpResponseForbidden(
            "You do not have permission to delete this driver."
        )

    if request.method == "POST":
        try:
            with transaction.atomic():
                driver.delete()

            messages.success(
                request,
                "Driver deleted successfully.",
            )

            return redirect(
                "drivers:driver_list",
            )

        except Exception:
            messages.error(
                request,
                "Unable to delete driver profile.",
            )

            return redirect(
                "drivers:driver_detail",
                driver.pk,
            )

    return render(
        request,
        "drivers/driver_confirm_delete.html",
        {
            "driver": driver,
        },
    )

@login_required
def dashboard(request):

    if request.user.role != UserRole.DRIVER:
        return HttpResponseForbidden(
            "Only drivers can access the driver dashboard."
        )

    try:
        driver = request.user.driver_profile

    except Driver.DoesNotExist:
        return redirect(
            "drivers:complete_profile"
        )

    assigned_shipments = (
        Shipment.objects.filter(
            driver=driver,
        )
        .select_related(
            "customer",
        )
        .order_by(
            "-created_at",
        )
    )

    pending_count = assigned_shipments.filter(
        status=ShipmentStatus.PICKUP_ASSIGNED,
    ).count()

    transit_count = assigned_shipments.filter(
        status=ShipmentStatus.IN_TRANSIT,
    ).count()

    out_delivery_count = assigned_shipments.filter(
        status=ShipmentStatus.OUT_FOR_DELIVERY,
    ).count()

    delivered_count = assigned_shipments.filter(
        status=ShipmentStatus.DELIVERED,
    ).count()

    return render(
        request,
        "drivers/dashboard.html",
        {
            "driver": driver,
            "assigned_shipments": assigned_shipments,
            "pending_count": pending_count,
            "transit_count": transit_count,
            "out_delivery_count": out_delivery_count,
            "delivered_count": delivered_count,
        },
    )

@login_required
def deliveries(request):

    if request.user.role != UserRole.DRIVER:
        return HttpResponseForbidden(
            "Only drivers can access this page."
        )

    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        return redirect("drivers:complete_profile")

    shipments = (
        Shipment.objects.filter(driver=driver)
        .order_by("-created_at")
    )

    return render(
        request,
        "drivers/deliveries.html",
        {
            "shipments": shipments,
        },
    )

@login_required
def delivery_details(request, pk):

    return redirect(
        "shipments:shipment_detail",
        pk=pk,
    )

    return render(
        request,
        "drivers/update_status.html",
        {
            "shipment": shipment,
        },
    )

@login_required
def route(request):

    if request.user.role != UserRole.DRIVER:
        return HttpResponseForbidden(
            "Only drivers can access this page."
        )

    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        return redirect("drivers:complete_profile")

    shipments = Shipment.objects.filter(
        driver=driver,
    ).exclude(
        status=ShipmentStatus.DELIVERED,
    )

    return render(
        request,
        "drivers/route.html",
        {
            "shipments": shipments,
        },
    )

@login_required
def history(request):

    if request.user.role != UserRole.DRIVER:
        return HttpResponseForbidden(
            "Only drivers can access this page."
        )

    try:
        driver = request.user.driver_profile
    except Driver.DoesNotExist:
        return redirect("drivers:complete_profile")

    completed_shipments = (
        Shipment.objects.filter(
            driver=driver,
            status=ShipmentStatus.DELIVERED,
        )
        .order_by("-delivered_at")
    )

    return render(
        request,
        "drivers/history.html",
        {
            "completed_shipments": completed_shipments,

            "total_deliveries": completed_shipments.count(),

            "delivered_count": completed_shipments.count(),

            "this_month_count": completed_shipments.filter(
                delivered_at__month=timezone.now().month,
                delivered_at__year=timezone.now().year,
            ).count(),

            "total_revenue": completed_shipments.aggregate(
                total=Sum("shipping_cost")
            )["total"] or 0,
        },
    )

@login_required
def complete_profile(request):
    if request.user.role != UserRole.DRIVER:
        return HttpResponseForbidden(
            "Only drivers can complete a driver profile."
        )

    if Driver.objects.filter(user=request.user).exists():
        return redirect("drivers:dashboard")

    form = DriverForm(
    request.POST or None,
    request.FILES or None,
)

    if request.method == "POST":

        if not form.is_valid():
            print("=" * 60)
            print(form.errors)
            print(form.errors.as_json())
            print("=" * 60)

        else:
            try:
                with transaction.atomic():
                    driver = form.save(commit=False)
                    driver.user = request.user
                    driver.save()

                messages.success(
                    request,
                    "Driver profile completed successfully.",
                )

                return redirect("drivers:dashboard")

            except Exception as exc:

                print(exc)

                messages.error(
                    request,
                    f"Unable to create driver profile: {exc}",
                )
    return render(
        request,
        "drivers/complete_profile.html",
        {
            "form": form,
        },
    )

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from apps.shipments.models import Shipment, ShipmentStatus
from .models import Driver


@login_required
def toggle_availability(request):
    driver = Driver.objects.get(user=request.user)

    if driver.status == Driver.Status.ON_LEAVE:
        messages.error(
            request,
            "You are currently on leave. Please contact an administrator."
        )
        return redirect("drivers:dashboard")

    if driver.status == Driver.Status.ON_DELIVERY:
        messages.error(
            request,
            "You cannot change availability while delivering a shipment."
        )
        return redirect("drivers:dashboard")

    active_shipment = Shipment.objects.filter(
        driver=driver,
        status__in=[
            ShipmentStatus.PICKUP_ASSIGNED,
            ShipmentStatus.PICKED_UP,
            ShipmentStatus.IN_TRANSIT,
            ShipmentStatus.OUT_FOR_DELIVERY,
        ],
    ).exists()

    if active_shipment:
        messages.error(
            request,
            "You still have an active shipment."
        )
        return redirect("drivers:dashboard")

    if driver.status == Driver.Status.AVAILABLE:
        driver.status = Driver.Status.OFF_DUTY
        messages.success(
            request,
            "You are now Off Duty."
        )

    elif driver.status == Driver.Status.OFF_DUTY:
        driver.status = Driver.Status.AVAILABLE
        messages.success(
            request,
            "You are now Available."
        )

    driver.save(update_fields=["status"])

    return redirect("drivers:dashboard")