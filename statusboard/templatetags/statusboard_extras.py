from django import template
from django import forms
from django.utils.translation import ugettext as _

from statusboard.models import SERVICE_STATUSES


register = template.Library()


def service_status_text(value, arg):
    return dict(SERVICE_STATUSES).get(int(value), arg)


@register.filter
def service_status_summary_text(value, arg):
    return {
        "0": _("All systems are operational"),
        "1": _("Some systems suffer of performance issues"),
        "2": _("Some systems suffer of minor outage"),
        "3": _("Some systems suffer of major outage"),
    }.get(str(value), arg)


@register.filter
def service_status_class(value, arg):
    return {
        "0": "success",
        "1": "info",
        "2": "warning",
        "3": "danger",
    }.get(str(value), arg)


@register.filter
def service_status_glyphicon(value, arg):
    return {
        "0": "glyphicon-ok-sign",
        "1": "glyphicon-info-sign",
        "2": "glyphicon-exclamation-sign",
        "3": "glyphicon-exclamation-sign",
    }.get(str(value), arg)


@register.filter
def incident_status_class(value, arg):
    return {
        "0": "danger",
        "1": "warning",
        "2": "info",
        "3": "success",
    }.get(str(value), arg)


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)
