from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.shipments.models import Shipment

from .forms import TrackingEventForm
from .models import TrackingEvent
from .services import TrackingService


# ==========================================================
# Permission Helper
# ==========================================================

def can_manage_tracking(user):
    if user.is_superuser:
        return True

    if getattr(user, "role", None) == "ADMIN":
        return True

    if getattr(user, "role", None) == "EMPLOYEE":
        return True

    return False


# ==========================================================
# Tracking List
# ==========================================================

@login_required
def tracking_list(request):
    query = request.GET.get("q", "").strip()

    events = (
        TrackingEvent.objects
        .select_related(
            "shipment",
            "updated_by",
        )
        .order_by("-created_at")
    )

    if query:
        events = events.filter(
            Q(shipment__tracking_number__icontains=query)
            | Q(location__icontains=query)
            | Q(description__icontains=query)
            | Q(status__icontains=query)
            | Q(updated_by__first_name__icontains=query)
            | Q(updated_by__last_name__icontains=query)
        )

    paginator = Paginator(
        events,
        20,
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        "tracking/tracking_list.html",
        {
            "events": page_obj,
            "page_obj": page_obj,
            "query": query,
        },
    )

# ==========================================================
# Shipment Tracking Timeline
# ==========================================================

@login_required
def shipment_tracking(request, tracking_number):

    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "customer",
            "driver",
            "created_by",
        ),
        tracking_number=tracking_number,
    )

    if not (
        can_manage_tracking(request.user)
        or shipment.created_by == request.user
        or (
            shipment.customer
            and shipment.customer.user == request.user
        )
        or (
            shipment.driver
            and shipment.driver.user == request.user
        )
    ):
        messages.error(
            request,
            "You do not have permission to view this shipment.",
        )

        return redirect("dashboard:dashboard")

    events = (
        shipment.tracking_events
        .select_related("updated_by")
        .order_by("created_at")
    )

    return render(
        request,
        "tracking/shipment_detail.html",
        {
            "shipment": shipment,
            "events": events,
            "event_count": events.count(),
            "latest_event": events.last(),
        },
    )

# ==========================================================
# Add Tracking Event
# ==========================================================

@login_required
def add_tracking_event(request, shipment_id):

    shipment = get_object_or_404(
        Shipment.objects.select_related(
            "customer",
            "driver",
            "created_by",
        ),
        pk=shipment_id,
    )

    if not can_manage_tracking(request.user):

        messages.error(
            request,
            "Permission denied.",
        )

        return redirect(
            "tracking:shipment_tracking",
            shipment.tracking_number,
        )

    form = TrackingEventForm(
        request.POST or None,
    )

    if request.method == "POST":

        if form.is_valid():

            try:

                with transaction.atomic():

                    event = form.save(
                        commit=False,
                    )

                    event.shipment = shipment
                    event.updated_by = request.user

                    event.save()

                    TrackingService.update_shipment_status(
                        shipment,
                        event.status,
                    )

                messages.success(
                    request,
                    "Tracking event added successfully.",
                )

                return redirect(
                    "tracking:shipment_tracking",
                    shipment.tracking_number,
                )

            except Exception as exc:

                messages.error(
                    request,
                    str(exc),
                )

    return render(
        request,
        "tracking/add_tracking.html",
        {
            "shipment": shipment,
            "form": form,
        },
    )

def public_tracking(request):

    tracking_number = request.GET.get(
        "tracking_number",
        ""
    ).strip()

    shipment = None
    tracking_events = []

    print("=" * 50)
    print("Tracking Number:", tracking_number)

    if tracking_number:

        shipment = Shipment.objects.filter(
            tracking_number=tracking_number
        ).first()

        print("Shipment:", shipment)

        if shipment:

            tracking_events = shipment.tracking_events.order_by(
                "created_at"
            )

            print("Events:", tracking_events.count())

    return render(
        request,
        "tracking/search.html",
        {
            "shipment": shipment,
            "tracking_events": tracking_events,
        },
    )