from io import BytesIO
import os

import qrcode
import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)

from apps.accounts.models import UserRole
from apps.customers.models import Customer
from apps.drivers.models import Driver
from .forms import ShipmentForm
from .models import Shipment, ShipmentStatus, Payment, PaymentStatus
from .services import ShipmentService
from .utils import generate_qr_code, generate_barcode


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

    # ----------------------------------------------------------
    # Premium A4 document
    # ----------------------------------------------------------

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=13 * mm,
        bottomMargin=17 * mm,
        title=f"ParcelPath Payment Receipt {shipment.tracking_number}",
        author="ParcelPath",
        subject="Payment receipt",
    )

    # ----------------------------------------------------------
    # Brand palette
    # ----------------------------------------------------------

    NAVY = colors.HexColor("#102A43")
    BLUE = colors.HexColor("#1769E0")
    BLUE_DARK = colors.HexColor("#0D47A1")
    GREEN = colors.HexColor("#15966B")
    GREEN_BG = colors.HexColor("#EAF8F2")
    GREEN_BORDER = colors.HexColor("#BFE7D5")
    TEXT = colors.HexColor("#243B53")
    MUTED = colors.HexColor("#6B7C8F")
    LIGHT = colors.HexColor("#F6F9FC")
    LIGHT_BLUE = colors.HexColor("#EEF5FF")
    BORDER = colors.HexColor("#D9E2EC")
    WHITE = colors.white
    RED = colors.HexColor("#C83E4D")

    # ----------------------------------------------------------
    # Styles
    # ----------------------------------------------------------

    title_style = ParagraphStyle(
        "ReceiptTitle",
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=22,
        textColor=NAVY,
    )

    subtitle_style = ParagraphStyle(
        "ReceiptSubtitle",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=MUTED,
    )

    section_style = ParagraphStyle(
        "ReceiptSection",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10,
        textColor=NAVY,
    )

    label_style = ParagraphStyle(
        "ReceiptLabel",
        fontName="Helvetica-Bold",
        fontSize=6.8,
        leading=8,
        textColor=MUTED,
    )

    value_style = ParagraphStyle(
        "ReceiptValue",
        fontName="Helvetica-Bold",
        fontSize=8.8,
        leading=11,
        textColor=TEXT,
    )

    normal_style = ParagraphStyle(
        "ReceiptNormal",
        fontName="Helvetica",
        fontSize=7.6,
        leading=10,
        textColor=TEXT,
    )

    small_style = ParagraphStyle(
        "ReceiptSmall",
        fontName="Helvetica",
        fontSize=6.8,
        leading=8.5,
        textColor=MUTED,
    )

    right_small_style = ParagraphStyle(
        "ReceiptRightSmall",
        fontName="Helvetica",
        fontSize=6.8,
        leading=8.5,
        textColor=MUTED,
        alignment=TA_RIGHT,
    )

    amount_style = ParagraphStyle(
        "ReceiptAmount",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=27,
        textColor=NAVY,
    )

    center_small_style = ParagraphStyle(
        "ReceiptCenterSmall",
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=8,
        textColor=MUTED,
        alignment=TA_CENTER,
    )

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------

    from xml.sax.saxutils import escape

    def safe(value, fallback="-"):
        if value is None:
            return fallback
        value = str(value).strip()
        return escape(value) if value else fallback

    def money(value):
        try:
            return f"INR {float(value):,.2f}"
        except (TypeError, ValueError):
            return f"INR {safe(value)}"

    def date_text(value, fmt):
        if not value:
            return "-"
        return value.strftime(fmt)

    receipt_number = f"PP-RCP-{payment.pk:08d}"
    customer_name = (
        shipment.customer.user.get_full_name()
        or shipment.customer.user.email
    )

    paid_date = date_text(
        payment.paid_at,
        "%d %b %Y",
    )

    paid_time = date_text(
        payment.paid_at,
        "%I:%M %p",
    )

    payment_amount = money(payment.amount)
    tracking_number = safe(shipment.tracking_number)

    # ----------------------------------------------------------
    # Logo
    # ----------------------------------------------------------

    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "images",
        "logos",
        "Nav_logo.png",
    )

    if os.path.exists(logo_path):
        logo = Image(
            logo_path,
            width=40 * mm,
            height=11.5 * mm,
        )
        logo.hAlign = "LEFT"
    else:
        logo = Paragraph(
            '<font color="#1769E0" size="19"><b>ParcelPath</b></font>',
            title_style,
        )

    # ----------------------------------------------------------
    # QR code and barcode
    # ----------------------------------------------------------

    qr_image = qrcode.make(tracking_number)
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_drawing = Image(
        qr_buffer,
        width=24 * mm,
        height=24 * mm,
    )
    qr_drawing.hAlign = "CENTER"

    barcode_drawing = createBarcodeDrawing(
        "Code128",
        value=tracking_number,
        barHeight=12 * mm,
        barWidth=0.42,
    )
    barcode_drawing.width = 52 * mm
    barcode_drawing.height = 18 * mm

    # ----------------------------------------------------------
    # Page footer
    # ----------------------------------------------------------

    def draw_footer(canvas, doc):
        canvas.saveState()

        page_width, page_height = A4

        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.6)
        canvas.line(
            14 * mm,
            11 * mm,
            page_width - 14 * mm,
            11 * mm,
        )

        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(MUTED)

        canvas.drawString(
            14 * mm,
            7 * mm,
            "ParcelPath  |  Smart Logistics & Parcel Delivery",
        )

        canvas.drawRightString(
            page_width - 14 * mm,
            7 * mm,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    elements = []

    # ==========================================================
    # HEADER
    # ==========================================================

    header_meta = Table(
        [
            [
                Paragraph(
                    '<font color="#1769E0" size="7"><b>PAYMENT RECEIPT</b></font>',
                    ParagraphStyle(
                        "HeaderTag",
                        fontName="Helvetica-Bold",
                        fontSize=7,
                        textColor=BLUE,
                        alignment=TA_RIGHT,
                    ),
                )
            ],
            [
                Paragraph(
                    f"Receipt No. <b>{receipt_number}</b>",
                    right_small_style,
                )
            ],
            [
                Paragraph(
                    f"Issued {paid_date}",
                    right_small_style,
                )
            ],
        ],
        colWidths=[61 * mm],
    )

    header = Table(
        [[logo, header_meta]],
        colWidths=[102 * mm, 61 * mm],
    )

    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    elements.append(header)
    elements.append(Spacer(1, 5 * mm))

    # ==========================================================
    # PAYMENT SUCCESS / AMOUNT HERO
    # ==========================================================

    success_icon = Paragraph(
        '<font color="#15966B" size="17"><b>✓</b></font>',
        ParagraphStyle(
            "SuccessIcon",
            fontName="Helvetica-Bold",
            fontSize=17,
            textColor=GREEN,
            alignment=TA_CENTER,
        ),
    )

    success_text = Table(
        [
            [
                Paragraph(
                    "PAYMENT SUCCESSFUL",
                    ParagraphStyle(
                        "SuccessTitle",
                        fontName="Helvetica-Bold",
                        fontSize=9,
                        leading=11,
                        textColor=GREEN,
                    ),
                )
            ],
            [
                Paragraph(
                    "Your shipment payment has been securely processed.",
                    small_style,
                )
            ],
        ],
        colWidths=[102 * mm],
    )

    success_row = Table(
        [[success_icon, success_text]],
        colWidths=[17 * mm, 102 * mm],
    )

    success_row.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_BG),
                ("BOX", (0, 0), (-1, -1), 0.7, GREEN_BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )

    amount_block = Table(
        [
            [
                Paragraph(
                    "AMOUNT PAID",
                    label_style,
                ),
                Paragraph(
                    payment_amount,
                    amount_style,
                ),
                Paragraph(
                    f"Paid on {paid_date} at {paid_time}",
                    small_style,
                ),
            ]
        ],
        colWidths=[119 * mm],
    )

    amount_block.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#C8DDF2")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
            ]
        )
    )

    hero = Table(
        [[success_row], [amount_block]],
        colWidths=[167 * mm],
    )

    hero.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5 * mm),
            ]
        )
    )

    elements.append(hero)
    elements.append(Spacer(1, 4 * mm))

    # ==========================================================
    # BILLING + TRANSACTION DETAILS
    # ==========================================================

    billing = Table(
        [
            [Paragraph("BILLED TO", section_style)],
            [
                Paragraph(
                    f"<b>{safe(customer_name)}</b><br/>"
                    f"{safe(shipment.customer.user.email)}",
                    normal_style,
                )
            ],
            [Paragraph("SHIPMENT", section_style)],
            [
                Paragraph(
                    f"<b>{tracking_number}</b><br/>"
                    f"Shipment payment",
                    normal_style,
                )
            ],
        ],
        colWidths=[78 * mm],
    )

    transaction = Table(
        [
            [Paragraph("TRANSACTION DETAILS", section_style)],
            [
                Paragraph(
                    f"<b>Payment Method</b><br/>Razorpay",
                    normal_style,
                )
            ],
            [
                Paragraph(
                    f"<b>Order ID</b><br/>{safe(payment.razorpay_order_id)}",
                    normal_style,
                )
            ],
            [
                Paragraph(
                    f"<b>Payment ID</b><br/>{safe(payment.razorpay_payment_id)}",
                    normal_style,
                )
            ],
        ],
        colWidths=[78 * mm],
    )

    for card in (billing, transaction):
        card.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                    ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
                    ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

    details_row = Table(
        [[billing, transaction]],
        colWidths=[82 * mm, 82 * mm],
    )

    details_row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    elements.append(details_row)
    elements.append(Spacer(1, 4 * mm))

    # ==========================================================
    # SHIPMENT REFERENCE + TRACKING
    # ==========================================================

    shipment_reference = Table(
        [
            [
                Paragraph(
                    "SHIPMENT REFERENCE",
                    section_style,
                )
            ],
            [
                Paragraph(
                    f"<font size='15' color='#102A43'><b>{tracking_number}</b></font>",
                    ParagraphStyle(
                        "TrackingHero",
                        fontName="Helvetica-Bold",
                        fontSize=15,
                        leading=18,
                        textColor=NAVY,
                    ),
                )
            ],
            [
                Paragraph(
                    f"Shipment status: <b>{safe(shipment.get_status_display())}</b>",
                    normal_style,
                )
            ],
            [
                barcode_drawing,
            ],
            [
                Paragraph(
                    tracking_number,
                    center_small_style,
                )
            ],
        ],
        colWidths=[91 * mm],
    )

    shipment_reference.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
                ("ALIGN", (0, 3), (-1, 4), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    qr_card = Table(
        [
            [qr_drawing],
            [
                Paragraph(
                    "SCAN TO TRACK",
                    center_small_style,
                )
            ],
            [
                Paragraph(
                    "Use the QR code to open live shipment tracking.",
                    center_small_style,
                )
            ],
        ],
        colWidths=[69 * mm],
    )

    qr_card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
            ]
        )
    )

    tracking_row = Table(
        [[shipment_reference, qr_card]],
        colWidths=[95 * mm, 70 * mm],
    )

    tracking_row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    elements.append(tracking_row)
    elements.append(Spacer(1, 4 * mm))

    # ==========================================================
    # PAYMENT SUMMARY
    # ==========================================================

    summary_data = [
        [
            Paragraph("PAYMENT SUMMARY", section_style),
            Paragraph("AMOUNT", right_small_style),
        ],
        [
            Paragraph("Shipping charge", normal_style),
            Paragraph(
                money(shipment.shipping_cost),
                ParagraphStyle(
                    "SummaryAmount",
                    fontName="Helvetica-Bold",
                    fontSize=9,
                    leading=11,
                    textColor=TEXT,
                    alignment=TA_RIGHT,
                ),
            ),
        ],
        [
            Paragraph("<b>Total paid</b>", normal_style),
            Paragraph(
                f"<b>{payment_amount}</b>",
                ParagraphStyle(
                    "TotalAmount",
                    fontName="Helvetica-Bold",
                    fontSize=11,
                    leading=13,
                    textColor=GREEN,
                    alignment=TA_RIGHT,
                ),
            ),
        ],
    ]

    summary = Table(
        summary_data,
        colWidths=[119 * mm, 48 * mm],
    )

    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                ("BACKGROUND", (0, 2), (-1, 2), GREEN_BG),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
                ("LINEBELOW", (0, 0), (-1, 0), 0.7, BORDER),
                ("LINEABOVE", (0, 2), (-1, 2), 0.7, GREEN_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    elements.append(summary)
    elements.append(Spacer(1, 4 * mm))

    # ==========================================================
    # CONFIRMATION / FOOTNOTE
    # ==========================================================

    confirmation = Table(
        [
            [
                Paragraph(
                    '<font color="#15966B" size="10"><b>✓</b></font>',
                    ParagraphStyle(
                        "ConfirmIcon",
                        fontName="Helvetica-Bold",
                        fontSize=10,
                        textColor=GREEN,
                        alignment=TA_CENTER,
                    ),
                ),
                Paragraph(
                    "<b>Payment verified successfully</b><br/>"
                    "This receipt confirms that the payment shown above was "
                    "successfully processed and recorded by ParcelPath.",
                    normal_style,
                ),
            ]
        ],
        colWidths=[13 * mm, 154 * mm],
    )

    confirmation.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_BG),
                ("BOX", (0, 0), (-1, -1), 0.7, GREEN_BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
            ]
        )
    )

    elements.append(confirmation)
    elements.append(Spacer(1, 4 * mm))

    elements.append(
        Paragraph(
            "Thank you for choosing ParcelPath.",
            ParagraphStyle(
                "Thanks",
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=10,
                textColor=NAVY,
                alignment=TA_CENTER,
            ),
        )
    )

    elements.append(
        Paragraph(
            "Keep this receipt for your records. For shipment updates, scan "
            "the QR code above using your mobile device.",
            ParagraphStyle(
                "ReceiptClosing",
                fontName="Helvetica",
                fontSize=6.8,
                leading=9,
                textColor=MUTED,
                alignment=TA_CENTER,
            ),
        )
    )

    document.build(
        elements,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )

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


# ==========================================================
# PREMIUM SHIPMENT PDF
# ==========================================================

@login_required
def shipment_label_pdf(request, pk):

    shipment = get_object_or_404(
        Shipment,
        pk=pk,
    )

    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="ParcelPath_Shipment_'
        f'{shipment.tracking_number}.pdf"'
    )

    # ------------------------------------------------------
    # DOCUMENT
    # ------------------------------------------------------

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=16 * mm,
        bottomMargin=15 * mm,
        title=f"ParcelPath Shipment {shipment.tracking_number}",
        author="ParcelPath",
    )

    # ------------------------------------------------------
    # COLORS
    # ------------------------------------------------------

    NAVY = colors.HexColor("#0B2341")
    BLUE = colors.HexColor("#1769E0")
    BLUE_DARK = colors.HexColor("#0D47A1")
    CYAN = colors.HexColor("#0891B2")

    GREEN = colors.HexColor("#0F9D68")
    GREEN_BG = colors.HexColor("#E8F7F0")

    ORANGE = colors.HexColor("#E8890C")
    RED = colors.HexColor("#D64545")

    TEXT = colors.HexColor("#19344D")
    MUTED = colors.HexColor("#6B7F92")

    BORDER = colors.HexColor("#D8E3ED")
    LIGHT = colors.HexColor("#F4F8FC")
    LIGHT_BLUE = colors.HexColor("#EAF3FC")

    WHITE = colors.white

    # ------------------------------------------------------
    # STYLES
    # ------------------------------------------------------

    title_style = ParagraphStyle(
        "PremiumTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        textColor=NAVY,
        spaceAfter=3,
    )

    subtitle_style = ParagraphStyle(
        "PremiumSubtitle",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=MUTED,
    )

    section_style = ParagraphStyle(
        "Section",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=NAVY,
    )

    label_style = ParagraphStyle(
        "Label",
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=MUTED,
    )

    value_style = ParagraphStyle(
        "Value",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=TEXT,
    )

    normal_style = ParagraphStyle(
        "NormalPremium",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT,
    )

    small_style = ParagraphStyle(
        "Small",
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=MUTED,
    )

    center_small_style = ParagraphStyle(
        "CenterSmall",
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=MUTED,
        alignment=TA_CENTER,
    )

    right_value_style = ParagraphStyle(
        "RightValue",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=TEXT,
        alignment=TA_RIGHT,
    )

    # ------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------

    def safe_value(value, fallback="-"):

        if value is None:
            return fallback

        value = str(value).strip()

        return value if value else fallback

    def format_date(value, fmt):

        if not value:
            return "-"

        return value.strftime(fmt)

    # ------------------------------------------------------
    # LOGO
    # ------------------------------------------------------

    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "images",
        "logos",
        "Nav_logo.png",
    )

    if os.path.exists(logo_path):

        logo = Image(
            logo_path,
            width=42 * mm,
            height=12 * mm,
        )

        logo.hAlign = "LEFT"

    else:

        logo = Paragraph(
            "<b><font color='#1769E0' size='20'>ParcelPath</font></b>",
            title_style,
        )

    # ------------------------------------------------------
    # TRACKING NUMBER
    # ------------------------------------------------------

    tracking_number = safe_value(
        shipment.tracking_number
    )


    # ------------------------------------------------------
    # TRACKING BARCODE
    # ------------------------------------------------------
    # Use createBarcodeDrawing() instead of adding Code128
    # directly to a Drawing. Code128 is a Flowable and cannot
    # be added to a ReportLab Drawing/Group.

    barcode_drawing = createBarcodeDrawing(
        "Code128",
        value=tracking_number,
        barHeight=12 * mm,
        barWidth=0.42,
        humanReadable=True,
    )

    barcode_drawing.width = 58 * mm
    barcode_drawing.height = 18 * mm


    # ------------------------------------------------------
    # QR CODE
    # ------------------------------------------------------
    # Generate the QR as a PNG image. This avoids ReportLab
    # Drawing/UserNode compatibility problems completely.

    qr_image = qrcode.make(
        tracking_number
    )

    qr_buffer = BytesIO()

    qr_image.save(
        qr_buffer,
        format="PNG",
    )

    qr_buffer.seek(0)

    qr_drawing = Image(
        qr_buffer,
        width=25 * mm,
        height=25 * mm,
    )

    qr_drawing.hAlign = "CENTER"

    # ------------------------------------------------------
    # STORY
    # ------------------------------------------------------

    elements = []

    # ======================================================
    # HEADER
    # ======================================================

    header_right = Table(
        [
            [
                Paragraph(
                    "<font size='7' color='#6B7F92'>SHIPMENT DOCUMENT</font>",
                    ParagraphStyle(
                        "headerSmall",
                        fontName="Helvetica-Bold",
                        fontSize=7,
                        textColor=MUTED,
                        alignment=TA_RIGHT,
                    ),
                )
            ],
            [
                Paragraph(
                    "<b>Smart Logistics & Parcel Delivery</b>",
                    ParagraphStyle(
                        "headerSub",
                        fontName="Helvetica",
                        fontSize=7.5,
                        textColor=MUTED,
                        alignment=TA_RIGHT,
                    ),
                )
            ],
        ],
        colWidths=[62 * mm],
    )

    header_table = Table(
        [
            [
                logo,
                header_right,
            ]
        ],
        colWidths=[
            105 * mm,
            62 * mm,
        ],
    )

    header_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "RIGHT",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    elements.append(
        header_table
    )

    elements.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # ======================================================
    # BLUE HEADER STRIP
    # ======================================================

    tracking_box = Table(
        [
            [
                Paragraph(
                    "<font color='#B9D9FF' size='7'>TRACKING NUMBER</font>",
                    ParagraphStyle(
                        "trackingLabel",
                        fontName="Helvetica-Bold",
                        fontSize=7,
                        textColor=colors.HexColor("#B9D9FF"),
                    ),
                ),
                Paragraph(
                    "<font color='#FFFFFF' size='8'>SHIPMENT STATUS</font>",
                    ParagraphStyle(
                        "statusLabel",
                        fontName="Helvetica-Bold",
                        fontSize=8,
                        textColor=WHITE,
                        alignment=TA_RIGHT,
                    ),
                ),
            ],
            [
                Paragraph(
                    f"<font color='#FFFFFF' size='18'><b>{tracking_number}</b></font>",
                    ParagraphStyle(
                        "trackingNumber",
                        fontName="Helvetica-Bold",
                        fontSize=18,
                        textColor=WHITE,
                    ),
                ),
                Paragraph(
                    f"<font color='#FFFFFF'><b>"
                    f"{safe_value(shipment.get_status_display())}"
                    f"</b></font>",
                    ParagraphStyle(
                        "statusValue",
                        fontName="Helvetica-Bold",
                        fontSize=9,
                        textColor=WHITE,
                        alignment=TA_RIGHT,
                    ),
                ),
            ],
        ],
        colWidths=[
            105 * mm,
            62 * mm,
        ],
        rowHeights=[
            8 * mm,
            13 * mm,
        ],
    )

    tracking_box.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    NAVY,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    NAVY,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
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
        tracking_box
    )

    elements.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # ======================================================
    # SENDER / RECEIVER
    # ======================================================

    sender_content = [
        [
            Paragraph(
                "FROM / SENDER",
                label_style,
            )
        ],
        [
            Paragraph(
                f"<b>{safe_value(shipment.sender_name)}</b>",
                value_style,
            )
        ],
        [
            Paragraph(
                f"Phone: {safe_value(shipment.sender_phone)}",
                normal_style,
            )
        ],
        [
            Paragraph(
                safe_value(shipment.sender_address),
                normal_style,
            )
        ],
    ]

    receiver_content = [
        [
            Paragraph(
                "TO / RECEIVER",
                label_style,
            )
        ],
        [
            Paragraph(
                f"<b>{safe_value(shipment.receiver_name)}</b>",
                value_style,
            )
        ],
        [
            Paragraph(
                f"Phone: {safe_value(shipment.receiver_phone)}",
                normal_style,
            )
        ],
        [
            Paragraph(
                safe_value(shipment.receiver_address),
                normal_style,
            )
        ],
    ]

    sender_table = Table(
        sender_content,
        colWidths=[79 * mm],
    )

    receiver_table = Table(
        receiver_content,
        colWidths=[79 * mm],
    )

    for table in [
        sender_table,
        receiver_table,
    ]:

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        LIGHT,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        BORDER,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5 * mm,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        3 * mm,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        3 * mm,
                    ),
                ]
            )
        )

    address_table = Table(
        [
            [
                sender_table,
                receiver_table,
            ]
        ],
        colWidths=[
            82 * mm,
            82 * mm,
        ],
    )

    address_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    elements.append(
        address_table
    )

    elements.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # ======================================================
    # SHIPMENT DETAILS HEADER
    # ======================================================

    elements.append(
        Table(
            [
                [
                    Paragraph(
                        "SHIPMENT DETAILS",
                        section_style,
                    ),
                    Paragraph(
                        "PARCEL INFORMATION",
                        ParagraphStyle(
                            "rightSection",
                            fontName="Helvetica-Bold",
                            fontSize=7,
                            textColor=BLUE,
                            alignment=TA_RIGHT,
                        ),
                    ),
                ]
            ],
            colWidths=[
                125 * mm,
                42 * mm,
            ],
            style=TableStyle(
                [
                    (
                        "LINEBELOW",
                        (0, 0),
                        (-1, -1),
                        1,
                        BLUE,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        2 * mm,
                    ),
                ]
            ),
        )
    )

    elements.append(
        Spacer(
            1,
            3 * mm,
        )
    )

    # ======================================================
    # SHIPMENT INFORMATION
    # ======================================================

    dimensions = (
        f"{safe_value(shipment.length)} × "
        f"{safe_value(shipment.width)} × "
        f"{safe_value(shipment.height)} cm"
    )

    details = [
        [
            Paragraph("PACKAGE TYPE", label_style),
            Paragraph("WEIGHT", label_style),
            Paragraph("DIMENSIONS", label_style),
        ],
        [
            Paragraph(
                safe_value(shipment.package_type),
                value_style,
            ),
            Paragraph(
                f"{safe_value(shipment.weight)} Kg",
                value_style,
            ),
            Paragraph(
                dimensions,
                value_style,
            ),
        ],
        [
            Paragraph("EXPECTED DELIVERY", label_style),
            Paragraph("CREATED ON", label_style),
            Paragraph("DECLARED VALUE", label_style),
        ],
        [
            Paragraph(
                format_date(
                    shipment.expected_delivery,
                    "%d %b %Y",
                ),
                value_style,
            ),
            Paragraph(
                format_date(
                    shipment.created_at,
                    "%d %b %Y, %I:%M %p",
                ),
                value_style,
            ),
            Paragraph(
                f"₹{safe_value(shipment.declared_value)}",
                value_style,
            ),
        ],
    ]

    details_table = Table(
        details,
        colWidths=[
            55 * mm,
            55 * mm,
            57 * mm,
        ],
    )

    details_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
            ]
        )
    )

    elements.append(
        details_table
    )

    elements.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # ======================================================
    # PAYMENT / SHIPPING SUMMARY
    # ======================================================

    shipping_cost = safe_value(
        shipment.shipping_cost
    )

    summary_left = Table(
        [
            [
                Paragraph(
                    "SHIPPING CHARGE",
                    label_style,
                )
            ],
            [
                Paragraph(
                    f"<font size='18' color='#0B2341'>"
                    f"<b>₹{shipping_cost}</b>"
                    f"</font>",
                    ParagraphStyle(
                        "price",
                        fontName="Helvetica-Bold",
                        fontSize=18,
                        textColor=NAVY,
                    ),
                )
            ],
            [
                Paragraph(
                    "Final shipping amount associated with this shipment.",
                    small_style,
                )
            ],
        ],
        colWidths=[93 * mm],
    )

    summary_left.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_BLUE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#C8DDF2"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3 * mm,
                ),
            ]
        )
    )

    summary_right = Table(
        [
            [
                qr_drawing,
                barcode_drawing,
            ],
            [
                Paragraph(
                    "SCAN TO IDENTIFY",
                    center_small_style,
                ),
                Paragraph(
                    "TRACKING BARCODE",
                    center_small_style,
                ),
            ],
        ],
        colWidths=[
            32 * mm,
            58 * mm,
        ],
    )

    summary_right.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    1 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    1 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    1 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    1 * mm,
                ),
            ]
        )
    )

    payment_row = Table(
        [
            [
                summary_left,
                summary_right,
            ]
        ],
        colWidths=[
            95 * mm,
            70 * mm,
        ],
    )

    payment_row.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    elements.append(
        payment_row
    )

    elements.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # ======================================================
    # DELIVERY NOTICE
    # ======================================================

    notice = Table(
        [
            [
                Paragraph(
                    "<b>DELIVERY INFORMATION</b>",
                    ParagraphStyle(
                        "noticeTitle",
                        fontName="Helvetica-Bold",
                        fontSize=8,
                        textColor=GREEN,
                    ),
                )
            ],
            [
                Paragraph(
                    "Please retain this document for shipment "
                    "identification and tracking. Shipment status "
                    "may change as the parcel moves through the "
                    "ParcelPath delivery network.",
                    ParagraphStyle(
                        "noticeText",
                        fontName="Helvetica",
                        fontSize=7.5,
                        leading=10,
                        textColor=TEXT,
                    ),
                )
            ],
        ],
        colWidths=[
            167 * mm
        ],
    )

    notice.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    GREEN_BG,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#B7E4CF"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5 * mm,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5 * mm,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2.5 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2.5 * mm,
                ),
            ]
        )
    )

    elements.append(
        notice
    )

    elements.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    # ======================================================
    # FOOTER INFORMATION
    # ======================================================

    footer_table = Table(
        [
            [
                Paragraph(
                    "<b>ParcelPath</b><br/>"
                    "<font size='7'>Smart Logistics & Parcel Delivery</font>",
                    ParagraphStyle(
                        "footerBrand",
                        fontName="Helvetica",
                        fontSize=8,
                        leading=10,
                        textColor=NAVY,
                    ),
                ),
                Paragraph(
                    "SHIPMENT DOCUMENT<br/>"
                    "<font size='7'>"
                    "Generated automatically by ParcelPath"
                    "</font>",
                    ParagraphStyle(
                        "footerRight",
                        fontName="Helvetica",
                        fontSize=7,
                        leading=10,
                        textColor=MUTED,
                        alignment=TA_RIGHT,
                    ),
                ),
            ]
        ],
        colWidths=[
            90 * mm,
            77 * mm,
        ],
    )

    footer_table.setStyle(
        TableStyle(
            [
                (
                    "LINEABOVE",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4 * mm,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
            ]
        )
    )

    elements.append(
        footer_table
    )

    # ======================================================
    # BUILD PDF
    # ======================================================

    document.build(
        elements
    )

    return response