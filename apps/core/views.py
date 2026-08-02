from django.shortcuts import render


def error_403(request, exception):
    return render(
        request,
        "errors/403.html",
        status=403,
    )


def error_404(request, exception):
    return render(
        request,
        "errors/404.html",
        status=404,
    )


def error_500(request):
    return render(
        request,
        "errors/500.html",
        status=500,
    )

from django.contrib import messages
from django.shortcuts import redirect, render

from apps.contact.forms import ContactForm


def contact(request):

    form = ContactForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            contact = form.save(commit=False)

            if request.user.is_authenticated:
                contact.user = request.user

            contact.save()

            messages.success(
                request,
                "Your message has been sent successfully. We will contact you soon."
            )

            return redirect("contact")

    return render(
        request,
        "home/contact.html",
        {
            "form": form,
        },
    )