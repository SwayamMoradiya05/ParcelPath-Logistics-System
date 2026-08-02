from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from apps.drivers.models import Driver

from .forms import RouteForm
from .models import Route, RouteShipment


# ==========================================================
# Permission Helper
# ==========================================================

def can_manage_route(user):
    if user.is_superuser:
        return True

    if getattr(user, "role", None) == "ADMIN":
        return True

    return False


# ==========================================================
# Route List
# ==========================================================

@login_required
def route_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    routes = (
        Route.objects.select_related(
            "driver",
            "driver__user",
        )
        .order_by("-created_at")
    )

    if query:
        routes = routes.filter(
            Q(route_code__icontains=query)
            | Q(name__icontains=query)
            | Q(origin__icontains=query)
            | Q(destination__icontains=query)
            | Q(driver__user__first_name__icontains=query)
            | Q(driver__user__last_name__icontains=query)
        )

    if status:
        routes = routes.filter(
            status=status,
        )

    paginator = Paginator(
        routes,
        20,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(
        page_number,
    )

    return render(
        request,
        "routes/route_list.html",
        {
            "routes": page_obj,
            "page_obj": page_obj,
            "query": query,
            "selected_status": status,
        },
    )


# ==========================================================
# Route Detail
# ==========================================================

@login_required
def route_detail(request, pk):
    route = get_object_or_404(
        Route.objects.select_related(
            "driver",
            "driver__user",
        ).prefetch_related(
            Prefetch(
                "route_shipments",
                queryset=RouteShipment.objects.select_related(
                    "shipment",
                ).order_by(
                    "stop_number",
                ),
            )
        ),
        pk=pk,
    )

    if not can_manage_route(request.user):
        messages.error(
            request,
            "You do not have permission to view this route.",
        )

        return redirect(
            "routes:route_list",
        )

    return render(
        request,
        "routes/route_detail.html",
        {
            "route": route,
            "total_shipments": route.total_shipments,
            "delivered_shipments": route.delivered_shipments,
            "pending_shipments": route.pending_shipments,
            "completion_percentage": route.completion_percentage,
        },
    )
from django.db import transaction


# ==========================================================
# Create Route
# ==========================================================

@login_required
def route_create(request):
    form = RouteForm(
        request.POST or None,
    )

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    route = form.save()

                messages.success(
                    request,
                    "Route created successfully.",
                )

                return redirect(
                    "routes:route_detail",
                    route.pk,
                )

            except Exception as exc:
                messages.error(
                    request,
                    f"Error creating route: {exc}",
                )

    return render(
        request,
        "routes/route_form.html",
        {
            "form": form,
            "title": "Create Route",
        },
    )


# ==========================================================
# Update Route
# ==========================================================

@login_required
def route_update(request, pk):
    route = get_object_or_404(
        Route.objects.select_related(
            "driver",
            "driver__user",
        ),
        pk=pk,
    )

    if not can_manage_route(request.user):
        messages.error(
            request,
            "You do not have permission to update this route.",
        )

        return redirect(
            "routes:route_list",
        )

    form = RouteForm(
        request.POST or None,
        instance=route,
    )

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

                messages.success(
                    request,
                    "Route updated successfully.",
                )

                return redirect(
                    "routes:route_detail",
                    route.pk,
                )

            except Exception as exc:
                messages.error(
                    request,
                    f"Error updating route: {exc}",
                )

    return render(
        request,
        "routes/route_form.html",
        {
            "form": form,
            "route": route,
            "title": "Update Route",
        },
    )
from django.db import transaction


# ==========================================================
# Delete Route
# ==========================================================

@login_required
def route_delete(request, pk):
    route = get_object_or_404(
        Route.objects.select_related(
            "driver",
        ),
        pk=pk,
    )

    if not can_manage_route(request.user):
        messages.error(
            request,
            "You do not have permission to delete this route.",
        )

        return redirect(
            "routes:route_list",
        )

    if request.method == "POST":
        try:
            with transaction.atomic():
                route.delete()

            messages.success(
                request,
                "Route deleted successfully.",
            )

            return redirect(
                "routes:route_list",
            )

        except Exception as exc:
            messages.error(
                request,
                f"Error deleting route: {exc}",
            )

    return render(
        request,
        "routes/route_confirm_delete.html",
        {
            "route": route,
        },
    )


# ==========================================================
# Assign Driver
# ==========================================================

@login_required
def assign_driver(request, pk):
    route = get_object_or_404(
        Route.objects.select_related(
            "driver",
        ),
        pk=pk,
    )

    if not can_manage_route(request.user):
        messages.error(
            request,
            "Permission denied.",
        )

        return redirect(
            "routes:route_detail",
            route.pk,
        )

    if request.method == "POST":
        driver = get_object_or_404(
            Driver,
            pk=request.POST.get("driver"),
            is_verified=True,
            status=Driver.Status.AVAILABLE,
        )

        try:
            with transaction.atomic():
                route.assign_driver(driver)

            messages.success(
                request,
                "Driver assigned successfully.",
            )

        except Exception as exc:
            messages.error(
                request,
                f"Error assigning driver: {exc}",
            )

        return redirect(
            "routes:route_detail",
            route.pk,
        )

    drivers = (
        Driver.objects.filter(
            is_verified=True,
            status=Driver.Status.AVAILABLE,
        )
        .select_related("user")
        .order_by("user__first_name")
    )

    return render(
        request,
        "routes/assign_driver.html",
        {
            "route": route,
            "drivers": drivers,
        },
    )


# ==========================================================
# Route Workflow
# ==========================================================
from .models import RouteStatus
@login_required
def update_status(request, pk, status):
    route = get_object_or_404(
        Route,
        pk=pk,
    )

    if not can_manage_route(request.user):
        messages.error(
            request,
            "Permission denied.",
        )

        return redirect(
            "routes:route_detail",
            route.pk,
        )

    try:
        with transaction.atomic():

            if status == RouteStatus.ASSIGNED:
                if route.driver:
                    route.assign_driver(
                        route.driver,
                    )

            elif status == RouteStatus.STARTED:
                route.start_route()

            elif status == RouteStatus.COMPLETED:
                route.complete_route()

            elif status == RouteStatus.CANCELLED:
                route.cancel_route()

            else:
                messages.error(
                    request,
                    "Invalid route status.",
                )

                return redirect(
                    "routes:route_detail",
                    route.pk,
                )

        messages.success(
            request,
            "Route status updated successfully.",
        )

    except Exception as exc:
        messages.error(
            request,
            f"Error updating route: {exc}",
        )

    return redirect(
        "routes:route_detail",
        route.pk,
    )