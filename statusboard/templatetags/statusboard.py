# Copyright (C) 2017 Emanuele Di Giacomo <emanuele@digiacomo.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from __future__ import absolute_import

from django import template
from django import forms
from django.utils.translation import gettext as _


register = template.Library()


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
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)
