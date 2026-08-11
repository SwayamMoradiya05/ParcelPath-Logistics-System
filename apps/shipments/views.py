from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from reportlab.lib import colors
from apps.customers.models import Customer
from apps.drivers.models import Driver
from reportlab.lib.pagesizes import A4
from .forms import ShipmentForm
from .models import Shipment, ShipmentStatus, Payment, PaymentStatus
from .services import ShipmentService
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden,JsonResponse
from apps.accounts.models import UserRole
from reportlab.lib.styles import getSampleStyleSheet
import razorpay
from django.conf import settings
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)




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

    paid_payment = (
            Payment.objects.filter(
                shipment=shipment,
                status=PaymentStatus.PAID,
            )
            .order_by("-paid_at", "-created_at")
            .first()
        ) 

    return render(
        request,
        "shipments/shipment_detail.html",
        {
            "shipment": shipment,
            "paid_payment": paid_payment,
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

                return redirect(
                        "shipments:shipment_detail",
                        shipment.pk,
                    )

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
# Payment
# ==========================================================

@login_required
def shipment_payment(request, pk):

    shipment = get_object_or_404(
        Shipment,
        pk=pk,
        customer__user=request.user,
    )

    if shipment.status != ShipmentStatus.PENDING:
        messages.warning(
            request,
            "This shipment is not available for payment.",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )

    existing_paid_payment = Payment.objects.filter(
        shipment=shipment,
        status=PaymentStatus.PAID,
    ).first()

    if existing_paid_payment:
        messages.info(
            request,
            "This shipment has already been paid.",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )

    if shipment.shipping_cost <= 0:
        messages.error(
            request,
            "Payment cannot be processed because the shipping cost is invalid.",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )

    try:
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

        amount_paise = int(
            shipment.shipping_cost * 100
        )

        razorpay_order = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": (
                    f"shipment_{shipment.pk}"
                ),
            }
        )

        payment = Payment.objects.create(
            shipment=shipment,
            razorpay_order_id=razorpay_order["id"],
            amount=shipment.shipping_cost,
            currency="INR",
            status=PaymentStatus.CREATED,
        )

        return render(
            request,
            "shipments/payment.html",
            {
                "shipment": shipment,
                "payment": payment,
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            },
        )

    except Exception as exc:

        messages.error(
            request,
            f"Unable to start payment: {exc}",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )


@login_required
def verify_shipment_payment(request, pk):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method.",
            },
            status=405,
        )

    shipment = get_object_or_404(
        Shipment,
        pk=pk,
        customer__user=request.user,
    )

    razorpay_order_id = request.POST.get(
        "razorpay_order_id"
    )

    razorpay_payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    razorpay_signature = request.POST.get(
        "razorpay_signature"
    )

    if not all(
        [
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature,
        ]
    ):
        return JsonResponse(
            {
                "success": False,
                "message": "Incomplete payment information.",
            },
            status=400,
        )

    payment = get_object_or_404(
        Payment,
        shipment=shipment,
        razorpay_order_id=razorpay_order_id,
    )

    if payment.status == PaymentStatus.PAID:
        return JsonResponse(
            {
                "success": True,
                "message": "Payment already completed.",
            }
        )

    try:

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            )
        )

        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )

        with transaction.atomic():

            payment.razorpay_payment_id = (
                razorpay_payment_id
            )

            payment.razorpay_signature = (
                razorpay_signature
            )

            payment.status = PaymentStatus.PAID

            payment.paid_at = timezone.now()

            payment.save(
                update_fields=[
                    "razorpay_payment_id",
                    "razorpay_signature",
                    "status",
                    "paid_at",
                    "updated_at",
                ]
            )

            shipment.status = ShipmentStatus.CONFIRMED

            shipment.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Payment successful!",
                "redirect_url": (
                    f"/shipments/{shipment.pk}/"
                ),
            }
        )

    except razorpay.errors.SignatureVerificationError:

        payment.status = PaymentStatus.FAILED

        payment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Payment verification failed.",
            },
            status=400,
        )

    except Exception as exc:

        return JsonResponse(
            {
                "success": False,
                "message": str(exc),
            },
            status=400,
        )

# ==========================================================
# Payment Receipt
# ==========================================================

@login_required
def payment_receipt(request, pk):

    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "customer",
            "customer__user",
        ),
        pk=pk,
    )

    if request.user.is_superuser or request.user.role == UserRole.ADMIN:
        pass

    elif (
        request.user.role == UserRole.CUSTOMER
        and shipment.customer.user == request.user
    ):
        pass

    else:
        return HttpResponseForbidden(
            "You do not have permission to view this receipt."
        )

    payment = (
        Payment.objects.filter(
            shipment=shipment,
            status=PaymentStatus.PAID,
        )
        .order_by("-paid_at", "-created_at")
        .first()
    )

    if not payment:
        messages.error(
            request,
            "Payment receipt is not available because this shipment has not been paid.",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )

    return render(
        request,
        "shipments/payment_receipt.html",
        {
            "shipment": shipment,
            "payment": payment,
        },
    )


@login_required
def payment_receipt_pdf(request, pk):

    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "customer",
            "customer__user",
        ),
        pk=pk,
    )

    if request.user.is_superuser or request.user.role == UserRole.ADMIN:
        pass

    elif (
        request.user.role == UserRole.CUSTOMER
        and shipment.customer.user == request.user
    ):
        pass

    else:
        return HttpResponseForbidden(
            "You do not have permission to download this receipt."
        )

    payment = (
        Payment.objects.filter(
            shipment=shipment,
            status=PaymentStatus.PAID,
        )
        .order_by("-paid_at", "-created_at")
        .first()
    )

    if not payment:
        messages.error(
            request,
            "Payment receipt is not available because this shipment has not been paid.",
        )

        return redirect(
            "shipments:shipment_detail",
            shipment.pk,
        )

    response = HttpResponse(
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'attachment; filename="ParcelPath_Payment_Receipt_'
        f'{shipment.tracking_number}.pdf"'
    )

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    elements = []

    # ======================================================
    # Header
    # ======================================================

    elements.append(
        Paragraph(
            "<b><font size='24'>ParcelPath</font></b>",
            styles["Title"],
        )
    )

    elements.append(
        Paragraph(
            "Payment Receipt",
            styles["Heading2"],
        )
    )

    elements.append(
        Spacer(
            1,
            20,
        )
    )

    # ======================================================
    # Receipt Number
    # ======================================================

    receipt_number = (
        f"PP-RCP-{payment.pk:08d}"
    )

    # ======================================================
    # Receipt Details
    # ======================================================

    customer_name = (
        shipment.customer.user.get_full_name()
        or shipment.customer.user.email
    )

    payment_date = (
        payment.paid_at.strftime(
            "%d %B %Y, %I:%M %p"
        )
        if payment.paid_at
        else "-"
    )

    data = [
        ["Receipt Number", receipt_number],
        ["Payment Date", payment_date],
        ["Customer", customer_name],
        ["Email", shipment.customer.user.email],
        ["Tracking Number", shipment.tracking_number],
        ["Amount Paid", f"₹ {payment.amount}"],
        ["Currency", payment.currency],
        ["Payment Method", "Razorpay"],
        [
            "Razorpay Order ID",
            payment.razorpay_order_id or "-",
        ],
        [
            "Razorpay Payment ID",
            payment.razorpay_payment_id or "-",
        ],
        ["Payment Status", "PAID"],
    ]

    table = Table(
        data,
        colWidths=[
            160,
            330,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#f2f4f7"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#333333"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#cccccc"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    elements.append(table)

    elements.append(
        Spacer(
            1,
            30,
        )
    )

    elements.append(
        Paragraph(
            "<b>Payment Status: PAID</b>",
            styles["Heading3"],
        )
    )

    elements.append(
        Spacer(
            1,
            15,
        )
    )

    elements.append(
        Paragraph(
            "Thank you for choosing ParcelPath.",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            "This receipt confirms that the above shipment payment "
            "was successfully processed.",
            styles["Normal"],
        )
    )

    document.build(elements)

    return response

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

        return redirect("drivers:dashboard")

    # ===================================================
    # Show upload page before marking Delivered
    # ===================================================

    if (
        current_status == ShipmentStatus.OUT_FOR_DELIVERY
        and request.method == "GET"
    ):
        return render(
            request,
            "shipments/driver_update_status.html",
            {
                "shipment": shipment,
            },
        )

    if (
        current_status == ShipmentStatus.OUT_FOR_DELIVERY
        and request.method == "POST"
    ):

        if not request.FILES.get("proof_of_delivery"):

            messages.error(
                request,
                "Please upload Proof of Delivery.",
            )

            return render(
                request,
                "shipments/driver_update_status.html",
                {
                    "shipment": shipment,
                },
            )

        shipment.proof_of_delivery = request.FILES["proof_of_delivery"]

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

    return redirect("drivers:dashboard")


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