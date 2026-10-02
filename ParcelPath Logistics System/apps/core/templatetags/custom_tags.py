from django import template

register = template.Library()


@register.filter
def yes_no(value):
    return "Yes" if value else "No"


@register.filter
def badge_class(status):
    mapping = {
        "Pending": "warning",
        "In Transit": "info",
        "Delivered": "success",
        "Cancelled": "danger",
        "Failed": "danger",
        "Active": "success",
        "Inactive": "secondary",
    }

    return mapping.get(status, "primary")


@register.simple_tag
def app_name():
    return "ParcelPath"