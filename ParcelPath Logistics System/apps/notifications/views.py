from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


# ==========================================================
# Notification List
# ==========================================================

@login_required
def notification_list(request):

    query = request.GET.get(
        "q",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    notifications = (
        Notification.objects.filter(
            user=request.user,
        )
        .order_by("-created_at")
    )

    if query:

        notifications = notifications.filter(
            Q(title__icontains=query)
            | Q(message__icontains=query)
        )

    if status == "read":

        notifications = notifications.filter(
            is_read=True,
        )

    elif status == "unread":

        notifications = notifications.filter(
            is_read=False,
        )

    paginator = Paginator(
        notifications,
        20,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {

        "notifications": page_obj,

        "page_obj": page_obj,

        "query": query,

        "selected_status": status,

        "unread_count": Notification.unread_count(
            request.user,
        ),

    }

    return render(
        request,
        "notifications/list.html",
        context,
    )


# ==========================================================
# Read Notification
# ==========================================================

@login_required
def notification_read(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    notification.mark_as_read()

    if notification.has_action:

        return redirect(
            notification.action_url,
        )

    return redirect(
        "notifications:list",
    )


# ==========================================================
# Delete Notification
# ==========================================================

@login_required
def notification_delete(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        try:

            with transaction.atomic():

                notification.delete()

            messages.success(
                request,
                "Notification deleted successfully.",
            )

            return redirect(
                "notifications:list",
            )

        except Exception as exc:

            messages.error(
                request,
                str(exc),
            )

    return render(
        request,
        "notifications/delete.html",
        {
            "notification": notification,
        },
    )


# ==========================================================
# Mark All as Read
# ==========================================================

@login_required
def mark_all_read(request):

    updated = Notification.mark_all_as_read(
        request.user,
    )

    if updated:

        messages.success(
            request,
            f"{updated} notification(s) marked as read.",
        )

    else:

        messages.info(
            request,
            "No unread notifications.",
        )

    return redirect(
        "notifications:list",
    )


# ==========================================================
# Delete All Notifications
# ==========================================================

@login_required
def delete_all_notifications(request):

    if request.method == "POST":

        deleted, _ = Notification.objects.filter(
            user=request.user,
        ).delete()

        messages.success(
            request,
            f"{deleted} notification(s) deleted.",
        )

    return redirect(
        "notifications:list",
    )