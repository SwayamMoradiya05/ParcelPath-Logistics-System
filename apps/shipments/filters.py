from django.db.models import Q

from .models import Shipment


class ShipmentFilter:

    @staticmethod
    def filter_queryset(request):
        queryset = Shipment.objects.select_related(
            "customer",
            "driver",
        )

        status = request.GET.get("status")
        tracking = request.GET.get("tracking")
        customer = request.GET.get("customer")

        if status:
            queryset = queryset.filter(
                status=status,
            )

        if tracking:
            queryset = queryset.filter(
                tracking_number__icontains=tracking,
            )

        if customer:
            queryset = queryset.filter(
                Q(customer__user__first_name__icontains=customer)
                | Q(customer__user__last_name__icontains=customer)
                | Q(customer__customer_id__icontains=customer)
            )

        return queryset.order_by("-created_at")