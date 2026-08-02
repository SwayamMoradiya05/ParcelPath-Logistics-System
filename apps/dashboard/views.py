from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import redirect
from apps.customers.models import Customer
from apps.drivers.models import Driver
from apps.notifications.models import Notification
from apps.routes.models import Route
from apps.shipments.models import Shipment, ShipmentStatus
from apps.tracking.models import TrackingEvent
from apps.shipments.services import ShipmentService
from apps.accounts.models import UserRole

@login_required
def dashboard(request):

    if request.user.is_superuser or request.user.is_staff or request.user.role == UserRole.ADMIN:
        today = timezone.now()

        stats = ShipmentService.dashboard_statistics()

        total_customers = Customer.objects.count()

        total_drivers = Driver.objects.count()

        verified_drivers = Driver.objects.filter(
            is_verified=True,
        ).count()

        available_drivers = Driver.objects.filter(
            status=Driver.Status.AVAILABLE,
        ).count()

        active_routes = Route.objects.count()

        monthly_shipments = Shipment.objects.filter(
            created_at__gte=today - timedelta(days=30),
        ).count()

        recent_shipments = (
            Shipment.objects.select_related(
                "customer",
                "driver",
            )
            .order_by("-created_at")[:10]
        )

        recent_tracking = (
            TrackingEvent.objects.select_related(
                "shipment",
            )
            .order_by("-created_at")[:10]
        )

        recent_notifications = (
            Notification.objects.filter(
                user=request.user,
            )
            .order_by("-created_at")[:10]
        )

        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()

        context = {
            **stats,
            "total_customers": total_customers,
            "total_drivers": total_drivers,
            "verified_drivers": verified_drivers,
            "available_drivers": available_drivers,
            "active_routes": active_routes,
            "monthly_shipments": monthly_shipments,
            "recent_shipments": recent_shipments,
            "recent_tracking": recent_tracking,
            "recent_notifications": recent_notifications,
            "unread_notifications": unread_notifications,
        }

        return render(
            request,
            "dashboard/dashboard.html",
            context,
        )

    if request.user.role == UserRole.CUSTOMER:
        return redirect("customers:dashboard")

    if request.user.role == UserRole.DRIVER:
        return redirect("drivers:dashboard")

    return redirect("home")