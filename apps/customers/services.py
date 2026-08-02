from django.db.models import Count, Q

from .models import Customer


class CustomerService:

    @staticmethod
    def get_all():
        return (
            Customer.objects.select_related("user")
            .order_by("user__first_name", "user__last_name")
        )

    @staticmethod
    def get_by_id(pk):
        return (
            Customer.objects.select_related("user")
            .filter(pk=pk)
            .first()
        )

    @staticmethod
    def get_by_customer_id(customer_id):
        return (
            Customer.objects.select_related("user")
            .filter(customer_id=customer_id)
            .first()
        )

    @staticmethod
    def get_dashboard_statistics():
        queryset = Customer.objects.all()

        return {
            "total_customers": queryset.count(),
            "verified_customers": queryset.filter(
                is_verified=True
            ).count(),
            "unverified_customers": queryset.filter(
                is_verified=False
            ).count(),
            "cities": (
                queryset.values("city")
                .annotate(total=Count("id"))
                .order_by("-total")
            ),
        }

    @staticmethod
    def search(keyword):
        if not keyword:
            return CustomerService.get_all()

        return (
            Customer.objects.select_related("user")
            .filter(
                Q(customer_id__icontains=keyword)
                | Q(company_name__icontains=keyword)
                | Q(city__icontains=keyword)
                | Q(state__icontains=keyword)
                | Q(user__first_name__icontains=keyword)
                | Q(user__last_name__icontains=keyword)
                | Q(user__email__icontains=keyword)
            )
            .distinct()
            .order_by("user__first_name")
        )

    @staticmethod
    def verify(customer):
        customer.verify()

    @staticmethod
    def unverify(customer):
        customer.unverify()

    @staticmethod
    def get_verified():
        return (
            Customer.objects.select_related("user")
            .filter(is_verified=True)
        )

    @staticmethod
    def get_unverified():
        return (
            Customer.objects.select_related("user")
            .filter(is_verified=False)
        )

    @staticmethod
    def get_recent(limit=10):
        return (
            Customer.objects.select_related("user")
            .order_by("-created_at")[:limit]
        )

    @staticmethod
    def get_top_customers(limit=10):
        return (
            Customer.objects.select_related("user")
            .order_by("-completed_shipments")[:limit]
        )