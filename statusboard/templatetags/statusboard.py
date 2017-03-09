from __future__ import unicode_literals
from __future__ import absolute_import

from django import template
from django import forms
from django.utils.translation import ugettext as _

from statusboard.models import Service
from statusboard.models import SERVICE_STATUSES


register = template.Library()


def service_status_text(value, arg):
    return dict(SERVICE_STATUSES).get(int(value), arg)


@register.filter
def service_status_summary_text(value, arg):
    return {
        "0": _("All systems are operational"),
        "1": _("Some systems are experiencing performance issues"),
        "2": _("Some systems are experiencing partial outages"),
        "3": _("Some systems are experiencing major outages"),
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
