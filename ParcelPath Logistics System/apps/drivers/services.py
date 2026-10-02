from django.db.models import Avg, Count

from .models import Driver


class DriverService:

    @staticmethod
    def get_all():
        return Driver.objects.select_related("user").all()

    @staticmethod
    def get_available_drivers():
        return Driver.objects.select_related(
            "user"
        ).filter(
            status=Driver.Status.AVAILABLE,
            is_verified=True,
        )

    @staticmethod
    def get_driver(driver_id):
        return Driver.objects.select_related(
            "user"
        ).get(
            pk=driver_id,
        )

    @staticmethod
    def verify(driver):
        driver.is_verified = True
        driver.save(update_fields=["is_verified"])

    @staticmethod
    def unverify(driver):
        driver.is_verified = False
        driver.save(update_fields=["is_verified"])

    @staticmethod
    def update_status(driver, status):
        driver.status = status
        driver.save(update_fields=["status"])

    @staticmethod
    def increment_delivery(driver):
        driver.total_deliveries += 1
        driver.successful_deliveries += 1

        driver.save(
            update_fields=[
                "total_deliveries",
                "successful_deliveries",
            ]
        )

    @staticmethod
    def dashboard_statistics():
        queryset = Driver.objects.all()

        return {
            "total": queryset.count(),
            "available": queryset.filter(
                status=Driver.Status.AVAILABLE
            ).count(),
            "busy": queryset.filter(
                status=Driver.Status.ON_DELIVERY
            ).count(),
            "verified": queryset.filter(
                is_verified=True
            ).count(),
            "average_rating": queryset.aggregate(
                Avg("rating")
            )["rating__avg"],
            "vehicle_summary": queryset.values(
                "vehicle_type"
            ).annotate(
                total=Count("id")
            ),
        }