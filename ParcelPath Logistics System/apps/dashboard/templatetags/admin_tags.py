import builtins

from django import template


register = template.Library()


@register.filter(name="getattr")
def get_attribute(value, name):
    try:
        if value is None:
            return ""

        result = builtins.getattr(value, name, "")

        if result is None:
            return ""

        return result

    except Exception:
        return ""