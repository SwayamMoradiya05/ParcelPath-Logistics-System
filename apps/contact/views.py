from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm, ContactReplyForm
from .models import Contact, ContactStatus


@login_required
def contact_list(request):
    contacts = Contact.objects.all().order_by("-created_at")

    if not request.user.is_superuser:
        contacts = contacts.filter(user=request.user)

    status = request.GET.get("status")

    if status:
        contacts = contacts.filter(status=status)

    paginator = Paginator(contacts, 15)
    page = request.GET.get("page")
    contacts = paginator.get_page(page)

    return render(
        request,
        "contact/contact_list.html",
        {
            "contacts": contacts,
            "selected_status": status,
        },
    )


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(
        Contact,
        pk=pk,
    )

    if not request.user.is_superuser and contact.user != request.user:
        messages.error(
            request,
            "You don't have permission to view this request.",
        )

        return redirect(
            "contact:list",
        )

    return render(
        request,
        "contact/contact_detail.html",
        {
            "contact": contact,
        },
    )


@login_required
def contact_create(request):
    form = ContactForm(
        request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            contact = form.save(
                commit=False,
            )

            contact.user = request.user
            contact.save()

        messages.success(
            request,
            "Your request has been submitted successfully.",
        )

        return redirect(
            "contact:detail",
            contact.pk,
        )

    return render(
        request,
        "contact/contact_form.html",
        {
            "form": form,
        },
    )


@login_required
def contact_reply(request, pk):
    if not request.user.is_superuser:
        messages.error(
            request,
            "Permission denied.",
        )

        return redirect(
            "contact:list",
        )

    contact = get_object_or_404(
        Contact,
        pk=pk,
    )

    form = ContactReplyForm(
        request.POST or None,
        instance=contact,
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            reply = form.save(
                commit=False,
            )

            reply.replied_by = request.user

            if reply.status == ContactStatus.RESOLVED:
                reply.resolve(
                    reply.admin_reply,
                    request.user,
                )
            else:
                reply.save()

        messages.success(
            request,
            "Reply saved successfully.",
        )

        return redirect(
            "contact:detail",
            contact.pk,
        )

    return render(
        request,
        "contact/contact_reply.html",
        {
            "form": form,
            "contact": contact,
        },
    )


@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(
        Contact,
        pk=pk,
    )

    if not request.user.is_superuser and contact.user != request.user:
        messages.error(
            request,
            "Permission denied.",
        )

        return redirect(
            "contact:list",
        )

    if request.method == "POST":
        contact.delete()

        messages.success(
            request,
            "Contact request deleted successfully.",
        )

        return redirect(
            "contact:list",
        )

    return render(
        request,
        "contact/contact_confirm_delete.html",
        {
            "contact": contact,
        },
    )