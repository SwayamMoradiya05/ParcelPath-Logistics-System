from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.customers.models import Customer
from apps.drivers.models import Driver

from .forms import ShipmentForm
from .models import Shipment, ShipmentStatus
from .services import ShipmentService
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden,JsonResponse
from apps.accounts.models import UserRole





# ==========================================================
# Permission Helper
# ==========================================================
def can_manage_shipment(user, shipment=None):

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.role == UserRole.ADMIN:
        return True

    if shipment is None:
        return False

    # Customer who owns the shipment
    if (
        user.role == UserRole.CUSTOMER
        and shipment.customer
        and shipment.customer.user == user
    ):
        return True

    # Driver assigned to the shipment
    if (
        user.role == UserRole.DRIVER
        and shipment.driver
        and shipment.driver.user == user
    ):
        return True

    # Creator of the shipment (optional)
    if shipment.created_by == user:
        return True

    return False

# ==========================================================
# Shipment List
# ==========================================================

@login_required
def shipment_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    shipments = (
        Shipment.objects
        .select_related(
            "customer",
            "driver",
            "created_by",
        )
        .order_by("-created_at")
    )

    if query:
        shipments = shipments.filter(
            Q(tracking_number__icontains=query)
            | Q(sender_name__icontains=query)
            | Q(receiver_name__icontains=query)
            | Q(sender_phone__icontains=query)
            | Q(receiver_phone__icontains=query)
            | Q(customer__company_name__icontains=query)
            | Q(customer__user__first_name__icontains=query)
            | Q(customer__user__last_name__icontains=query)
            | Q(driver__user__first_name__icontains=query)
            | Q(driver__user__last_name__icontains=query)
        )

    if status:
        shipments = shipments.filter(
            status=status
        )

    if not (
        request.user.is_superuser
        or getattr(request.user, "role", None) == "ADMIN"
    ):
        shipments = shipments.filter(
            created_by=request.user
        )

    paginator = Paginator(
        shipments,
        20,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        "shipments/list.html",
        {
            "page_obj": page_obj,
            "shipments": page_obj,
            "query": query,
            "selected_status": status,
            "status_choices": ShipmentStatus.choices,
        },
    )


# ==========================================================
# Shipment Detail
# ==========================================================

@login_required
def shipment_detail(request, pk):

    if request.user.role == UserRole.ADMIN:

        shipment = get_object_or_404(
            Shipment,
            pk=pk,
        )

    elif request.user.role == UserRole.CUSTOMER:

        shipment = get_object_or_404(
            Shipment,
            pk=pk,
            customer__user=request.user,
        )

    elif request.user.role == UserRole.DRIVER:

        shipment = get_object_or_404(
            Shipment,
            pk=pk,
            driver__user=request.user,
        )

    else:
        return HttpResponseForbidden(
            "Permission denied."
        )

    if not can_manage_shipment(
        request.user,
        shipment,
    ):
        messages.error(
            request,
            "You do not have permission to view this shipment.",
        )
        return redirect("shipments:shipment_list")

    return render(
        request,
        "shipments/shipment_detail.html",
        {
            "shipment": shipment,
        },
    )


@login_required
def shipment_label(request, pk):

    shipment = get_object_or_404(
        Shipment,
        pk=pk,
    )

    tracking_url = request.build_absolute_uri(
    f"/shipments/track/{shipment.tracking_number}/"
)

    qr_code = generate_qr_code(
        tracking_url,
    )

    barcode = generate_barcode(
        shipment.tracking_number,
    )

    return render(
        request,
        "shipments/label.html",
        {
            "shipment": shipment,
            "qr_code": qr_code,
            "barcode": barcode,
        },
    )
# ==========================================================
# Public Tracking
# ==========================================================

def track_shipment(request, tracking_number):
    if request.user.is_authenticated:
        if request.user.role == UserRole.ADMIN:
            shipment = get_object_or_404(
                Shipment,
                tracking_number=tracking_number,
            )
        else:
            shipment = get_object_or_404(
                Shipment,
                tracking_number=tracking_number,
                customer__user=request.user,
            )
    else:
        shipment = get_object_or_404(
            Shipment,
            tracking_number=tracking_number,
        )

    return render(
        request,
        "tracking/public_tracking.html",
        {
            "shipment": shipment,
            "generated_at": timezone.now(),
        },
    )

# ==========================================================
# Create Shipment
# ==========================================================

@login_required
def shipment_create(request):
    form = ShipmentForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    customer = get_object_or_404(
                        Customer,
                        user=request.user,
                    )

                    shipment = form.save(commit=False)
                    shipment.customer = customer
                    shipment.created_by = request.user
                    shipment.status = ShipmentStatus.PENDING

                    shipment.save()
                    form.save_m2m()

                    customer.increment_total_shipments()

                messages.success(
                    request,
                    "Shipment created successfully.",
                )

                return redirect("shipments:shipment_list")

            except Exception as e:
                messages.error(
                    request,
                    str(e),
                )

        else:
            print("=" * 60)
            print(form.errors)
            print(form.non_field_errors())
            print("=" * 60)

    messages.error(
        request,
        "Please correct the errors below.",
    )

    return render(
        request,
        "shipments/create.html",
        {
            "form": form,
            "title": "Create Shipment",
        },
    )
# ==========================================================
# Update Shipment
# ==========================================================

@login_required
def shipment_update(request, pk):
    if request.user.role == UserRole.ADMIN:
        shipment = get_object_or_404(
        Shipment,
        pk=pk,
    )
    else:
        shipment = get_object_or_404(
        Shipment,
        pk=pk,
        customer__user=request.user,
    )

    if not can_manage_shipment(
        request.user,
        shipment,
    ):
        messages.error(
            request,
            "You do not have permission to update this shipment.",
        )

        return redirect(
            "shipments:shipment_list",
        )

    form = ShipmentForm(
        request.POST or None,
        instance=shipment,
    )

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

                messages.success(
                    request,
                    "Shipment updated successfully.",
                )

                return redirect(
                    "shipments:shipment_detail",
                    shipment.pk,
                )

            except Exception as exc:
                messages.error(
                    request,
                    f"Error updating shipment: {exc}",
                )

    return render(
        request,
        "shipments/shipment_form.html",
        {
            "form": form,
            "shipment": shipment,
            "title": "Update Shipment",
        },
    )


# ==========================================================
# Delete Shipment
# ==========================================================

@login_required
def shipment_delete(request, pk):
    if request.user.role == UserRole.ADMIN:
        shipment = get_object_or_404(
        Shipment,
        pk=pk,
    )
    else:
        shipment = get_object_or_404(
        Shipment,
        pk=pk,
        customer__user=request.user,
    )

    if not can_manage_shipment(
        request.user,
        shipment,
    ):
        messages.error(
            request,
            "You do not have permission to delete this shipment.",
        )

        return redirect(
            "shipments:shipment_list",
        )

    if request.method == "POST":
        try:
            with transaction.atomic():
                shipment.delete()

            messages.success(
                request,
                "Shipment deleted successfully.",
            )

            return redirect(
                "shipments:shipment_list",
            )

        except Exception as exc:
            messages.error(
                request,
                f"Error deleting shipment: {exc}",
            )

    return render(
        request,
        "shipments/shipment_confirm_delete.html",
        {
            "shipment": shipment,
        },
    )
# ==========================================================
# Assign Driver
# ==========================================================


@login_required
def assign_driver(request, pk):
    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "customer",
            "driver",
            "created_by",
        ),
        pk=pk,
    )

    if not can_manage_shipment(
        request.user,
        shipment,
    ):
        messages.error(
            request,
            "You do not have permission to assign a driver.",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )

    # Prevent assigning a driver twice
    if shipment.driver:
        messages.warning(
            request,
            "A driver has already been assigned to this shipment.",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )

    if request.method == "POST":

        driver_id = request.POST.get("driver")

        if not driver_id:
            messages.error(
                request,
                "Please select a driver.",
            )

            return redirect(
                "shipments:assign_driver",
                shipment.pk,
            )

        driver = get_object_or_404(
            Driver.objects.select_related("user"),
            pk=driver_id,
            status=Driver.Status.AVAILABLE,
            is_verified=True,
        )

        try:
            ShipmentService.assign_driver(
                shipment,
                driver,
            )

            messages.success(
                request,
                f"Driver '{driver.user.full_name or driver.user.email}' assigned successfully.",
            )

            return redirect(
                "shipments:shipment_detail",
                shipment.pk,
            )

        except Exception as exc:

            messages.error(
                request,
                f"Error assigning driver: {exc}",
            )

    drivers = (
        Driver.objects.filter(
            status=Driver.Status.AVAILABLE,
            is_verified=True,
        )
        .select_related("user")
        .order_by(
        "user__first_name",
        "user__last_name",
        "vehicle_number",
)
    )

    return render(
        request,
        "shipments/assign_driver.html",
        {
            "shipment": shipment,
            "drivers": drivers,
        },
    )
# ==========================================================
# Shipment Status Update
# ==========================================================

@login_required
def update_status(request, pk, status):
    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "customer",
            "driver",
            "created_by",
        ),
        pk=pk,
    )

    if not can_manage_shipment(
        request.user,
        shipment,
    ):
        messages.error(
            request,
            "Permission denied.",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )

    try:
        ShipmentService.update_status(
            shipment,
            status,
        )

        messages.success(
            request,
            "Shipment status updated successfully.",
        )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to update shipment: {exc}",
        )

    return redirect(
        "shipments:shipment_detail",
        shipment.pk,
    )


# ==========================================================
# Available Drivers
# ==========================================================

@login_required
def driver_update_status(request, pk):

    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "driver",
            "customer",
        ),
        pk=pk,
    )

    if request.user.role != "DRIVER":
        return HttpResponseForbidden(
            "Only drivers can update shipment status."
        )

    if shipment.driver != request.user.driver_profile:
        return HttpResponseForbidden(
            "This shipment is not assigned to you."
        )

    next_status = {
        ShipmentStatus.PICKUP_ASSIGNED: ShipmentStatus.PICKED_UP,
        ShipmentStatus.PICKED_UP: ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.IN_TRANSIT: ShipmentStatus.OUT_FOR_DELIVERY,
        ShipmentStatus.OUT_FOR_DELIVERY: ShipmentStatus.DELIVERED,
    }

    current_status = shipment.status

    if current_status not in next_status:

        messages.warning(
            request,
            "Shipment cannot be updated from its current status.",
        )

        return redirect(
            "drivers:dashboard",
        )

    try:

        ShipmentService.update_status(
            shipment,
            next_status[current_status],
        )

        messages.success(
            request,
            f"Shipment status updated to {shipment.get_status_display()}.",
        )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to update shipment: {exc}",
        )

    return redirect(
        "drivers:dashboard",
    )


@login_required
@login_required
def available_drivers(request):
    """
    Return all verified drivers that are currently available.
    """

    if not request.user.is_superuser and request.user.role != UserRole.ADMIN:
        return HttpResponseForbidden(
            "You do not have permission to access this resource."
        )

    drivers = (
        Driver.objects.filter(
            is_verified=True,
            status=Driver.Status.AVAILABLE,
        )
        .select_related("user")
        .order_by("user__first_name", "user__last_name")
    )

    data = [
        ...
    ]

    return JsonResponse(data, safe=False)

from .utils import generate_qr_code, generate_barcode

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

@login_required
def shipment_label_pdf(request, pk):

    shipment = get_object_or_404(
        Shipment,
        pk=pk,
    )

    response = HttpResponse(
        content_type="application/pdf",
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="ParcelPath_Label_'
        f'{shipment.tracking_number}.pdf"'
    )

    document = SimpleDocTemplate(
        response,
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b><font size=20>ParcelPath</font></b>",
            styles["Title"],
        )
    )

    elements.append(
        Paragraph(
            "Smart Logistics & Parcel Delivery",
            styles["Normal"],
        )
    )

    elements.append(
        Spacer(
            1,
            20,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Tracking Number:</b> "
            f"{shipment.tracking_number}",
            styles["Heading2"],
        )
    )

    elements.append(
        Spacer(
            1,
            15,
        )
    )

    data = [

        [
            "Sender",
            shipment.sender_name,
        ],

        [
            "Sender Phone",
            shipment.sender_phone,
        ],

        [
            "Sender Address",
            shipment.sender_address,
        ],

        [
            "Receiver",
            shipment.receiver_name,
        ],

        [
            "Receiver Phone",
            shipment.receiver_phone,
        ],

        [
            "Receiver Address",
            shipment.receiver_address,
        ],

        [
            "Package Type",
            shipment.package_type,
        ],

        [
            "Weight",
            f"{shipment.weight} Kg",
        ],

        [
            "Dimensions",
            (
                f"{shipment.length} × "
                f"{shipment.width} × "
                f"{shipment.height} cm"
            ),
        ],

        [
            "Declared Value",
            f"₹{shipment.declared_value}",
        ],

        [
            "Shipping Cost",
            f"₹{shipment.shipping_cost}",
        ],

        [
            "Status",
            shipment.get_status_display(),
        ],

        [
            "Expected Delivery",
            (
                shipment.expected_delivery.strftime(
                    "%d %b %Y"
                )
                if shipment.expected_delivery
                else "-"
            ),
        ],

        [
            "Created On",
            shipment.created_at.strftime(
                "%d %b %Y %I:%M %p"
            ),
        ],

    ]

    table = Table(
        data,
        colWidths=[
            170,
            320,
        ],
    )

    table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#2563EB"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.white,
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica",
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

            ]

        )

    )

    elements.append(
        table,
    )

    elements.append(
        Spacer(
            1,
            30,
        )
    )

    elements.append(
        Paragraph(
            "Generated by ParcelPath Logistics",
            styles["Italic"],
        )
    )

    document.build(
        elements,
    )

    return response