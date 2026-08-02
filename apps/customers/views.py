from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from apps.shipments.models import Shipment, ShipmentStatus
from apps.accounts.models import UserRole

from .forms import CustomerForm
from .models import Customer
from django.shortcuts import get_object_or_404
from apps.customers.models import Customer


def can_manage_customer(user, customer=None):
    """
    Returns True if the user can manage the customer.
    """

    if not user.is_authenticated:
        return False

    if user.role == UserRole.ADMIN:
        return True

    if customer and customer.user == user:
        return True

    return False


@login_required
def customer_list(request):
    search = request.GET.get("search", "").strip()

    customers = (
        Customer.objects.select_related("user")
        .only(
            "id",
            "customer_id",
            "company_name",
            "city",
            "state",
            "is_verified",
            "total_shipments",
            "completed_shipments",
            "cancelled_shipments",
            "user__first_name",
            "user__last_name",
            "user__email",
        )
        .order_by(
            "user__first_name",
            "user__last_name",
        )
    )

    if request.user.role != UserRole.ADMIN:
        customers = customers.filter(
            user=request.user,
        )

    if search:
        customers = customers.filter(
            Q(customer_id__icontains=search)
            | Q(company_name__icontains=search)
            | Q(city__icontains=search)
            | Q(state__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__email__icontains=search)
        )

    paginator = Paginator(customers, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "customers/customer_list.html",
        {
            "page_obj": page_obj,
            "customers": page_obj,
            "search": search,
            "total_customers": customers.count(),
        },
    )


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(
        Customer.objects.select_related("user"),
        pk=pk,
    )

    if not can_manage_customer(
        request.user,
        customer,
    ):
        return HttpResponseForbidden(
            "You do not have permission to view this customer."
        )

    return render(
        request,
        "customers/customer_detail.html",
        {
            "customer": customer,
        },
    )

@login_required
def customer_create(request):
    if request.user.role != UserRole.CUSTOMER:
        return HttpResponseForbidden(
            "Only customers can create a customer profile."
        )

    existing_customer = Customer.objects.filter(
        user=request.user
    ).first()

    if existing_customer:
        messages.warning(
            request,
            "You already have a customer profile."
        )

        return redirect(
            "customers:customer_detail",
            existing_customer.pk,
        )

    form = CustomerForm(
        request.POST or None,
        request.FILES or None,
    )

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    customer = form.save(commit=False)
                    customer.user = request.user
                    customer.save()

                messages.success(
                    request,
                    "Customer profile created successfully.",
                )

                return redirect(
                    "customers:customer_detail",
                    customer.pk,
                )

            except Exception:
                messages.error(
                    request,
                    "Unable to create customer profile."
                )

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "is_create": True,
        },
    )


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(
    Customer,
    pk=pk,
    user=request.user,
)

    if not can_manage_customer(
        request.user,
        customer,
    ):
        return HttpResponseForbidden(
            "You do not have permission to update this customer."
        )

    form = CustomerForm(
        request.POST or None,
        request.FILES or None,
        instance=customer,
    )

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

                messages.success(
                    request,
                    "Customer updated successfully.",
                )

                return redirect(
                    "customers:customer_detail",
                    customer.pk,
                )

            except Exception:
                messages.error(
                    request,
                    "Unable to update customer."
                )

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "customer": customer,
            "is_create": False,
        },
    )


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(
    Customer,
    pk=pk,
    user=request.user,
)

    if not can_manage_customer(
        request.user,
        customer,
    ):
        return HttpResponseForbidden(
            "You do not have permission to delete this customer."
        )

    if request.method == "POST":
        try:
            with transaction.atomic():
                customer.delete()

            messages.success(
                request,
                "Customer deleted successfully.",
            )

            return redirect(
                "customers:customer_list",
            )

        except Exception:
            messages.error(
                request,
                "Unable to delete customer."
            )

            return redirect(
                "customers:customer_detail",
                customer.pk,
            )

    return render(
        request,
        "customers/customer_confirm_delete.html",
        {
            "customer": customer,
        },
    )

@login_required


@login_required
def dashboard(request):

    if request.user.role != UserRole.CUSTOMER:
        return HttpResponseForbidden("Access denied.")

    customer = get_object_or_404(
        Customer,
        user=request.user,
    )

    shipments = Shipment.objects.filter(
        customer=customer
    ).order_by("-created_at")

    total_shipments = shipments.count()

    pending_shipments = shipments.filter(
        status=ShipmentStatus.PENDING
    ).count()

    in_transit_shipments = shipments.filter(
        status__in=[
            ShipmentStatus.CONFIRMED,
            ShipmentStatus.PICKUP_ASSIGNED,
            ShipmentStatus.PICKED_UP,
            ShipmentStatus.IN_TRANSIT,
            ShipmentStatus.OUT_FOR_DELIVERY,
        ]
    ).count()

    delivered_shipments = shipments.filter(
        status=ShipmentStatus.DELIVERED
    ).count()

    recent_shipments = shipments[:10]

    return render(
        request,
        "customers/dashboard.html",
        {
            "customer": customer,
            "total_shipments": total_shipments,
            "pending_shipments": pending_shipments,
            "in_transit_shipments": in_transit_shipments,
            "delivered_shipments": delivered_shipments,
            "recent_shipments": recent_shipments,
        },
    )