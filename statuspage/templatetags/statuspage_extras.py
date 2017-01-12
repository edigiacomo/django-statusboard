from django import template

from statuspage.models import STATUSES


register = template.Library()


def status_text(value, arg):
    return dict(STATUSES).get(int(value), arg)


@register.filter
def status_summary_text(value, arg):
    return {
        "0": "All systems are operational",
        "1": "Some systems suffer of performance issues",
        "2": "Some systems suffer of minor outage",
        "3": "Some systems suffer of major outage",
    }.get(str(value), arg)

@register.filter
def status_class(value, arg):
    return {
        "0": "success",
        "1": "info",
        "2": "warning",
        "3": "danger",
    }.get(str(value), arg)
