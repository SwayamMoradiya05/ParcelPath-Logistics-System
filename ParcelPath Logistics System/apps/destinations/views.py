from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DestinationForm
from .models import Destination


@login_required
def destination_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    destinations = Destination.objects.all().order_by(
        "city",
        "name",
    )

    if query:
        destinations = destinations.filter(
            Q(name__icontains=query)
            | Q(city__icontains=query)
            | Q(state__icontains=query)
            | Q(country__icontains=query)
            | Q(destination_code__icontains=query)
            | Q(postal_code__icontains=query)
        )

    if status == "active":
        destinations = destinations.filter(
            is_active=True,
        )

    elif status == "inactive":
        destinations = destinations.filter(
            is_active=False,
        )

    paginator = Paginator(
        destinations,
        20,
    )

    page = request.GET.get("page")
    destinations = paginator.get_page(page)

    return render(
        request,
        "destinations/destination_list.html",
        {
            "destinations": destinations,
            "query": query,
            "selected_status": status,
        },
    )


@login_required
def destination_detail(request, pk):
    destination = get_object_or_404(
        Destination,
        pk=pk,
    )

    return render(
        request,
        "destinations/destination_detail.html",
        {
            "destination": destination,
        },
    )


@login_required
def destination_create(request):
    form = DestinationForm(
        request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            destination = form.save()

        messages.success(
            request,
            "Destination created successfully.",
        )

        return redirect(
            "destinations:detail",
            destination.pk,
        )

    return render(
        request,
        "destinations/destination_form.html",
        {
            "form": form,
        },
    )


@login_required
def destination_update(request, pk):
    destination = get_object_or_404(
        Destination,
        pk=pk,
    )

    form = DestinationForm(
        request.POST or None,
        instance=destination,
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            form.save()

        messages.success(
            request,
            "Destination updated successfully.",
        )

        return redirect(
            "destinations:detail",
            destination.pk,
        )

    return render(
        request,
        "destinations/destination_form.html",
        {
            "form": form,
            "destination": destination,
        },
    )


@login_required
def destination_delete(request, pk):
    destination = get_object_or_404(
        Destination,
        pk=pk,
    )

    if request.method == "POST":
        destination.delete()

        messages.success(
            request,
            "Destination deleted successfully.",
        )

        return redirect(
            "destinations:list",
        )

    return render(
        request,
        "destinations/destination_confirm_delete.html",
        {
            "destination": destination,
        },
    )