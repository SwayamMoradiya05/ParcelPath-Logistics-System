from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from apps.core.views import contact

urlpatterns = [
    # Django Admin (Development Only)
    path("admin/", admin.site.urls),

    # Landing Pages
    path(
        "",
        TemplateView.as_view(template_name="home/index.html"),
        name="home",
    ),

    path(
        "about/",
        TemplateView.as_view(template_name="home/about.html"),
        name="about",
    ),

    path(
        "services/",
        TemplateView.as_view(template_name="home/services.html"),
        name="services",
    ),

    path(
        "destinations/",
        TemplateView.as_view(template_name="home/destinations.html"),
        name="destinations",
    ),

    path(
        "pricing/",
        TemplateView.as_view(template_name="home/pricing.html"),
        name="pricing",
    ),

    path(
        "faq/",
        TemplateView.as_view(template_name="home/faq.html"),
        name="faq",
    ),

    path(
        "contact/",
        contact,
        name="contact",
    ),

    path(
        "track/",
        include("apps.tracking.urls"),
    ),

    # Applications
    path("accounts/", include("apps.accounts.urls")),
    path("customers/", include("apps.customers.urls")),
    path("drivers/", include("apps.drivers.urls")),
    path("shipments/", include("apps.shipments.urls")),
    path("tracking/", include("apps.tracking.urls")),
    path("routes/", include("apps.routes.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("contact-us/", include("apps.contact.urls")),
    path("locations/", include("apps.destinations.urls")),
]

handler403 = "apps.core.views.error_403"
handler404 = "apps.core.views.error_404"
handler500 = "apps.core.views.error_500"

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )