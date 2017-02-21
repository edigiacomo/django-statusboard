from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.views import redirect_to_login


class PermissionRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if self.permission_required:
            if not self.request.user.has_perm(self.permission_required):
                return redirect_to_login(self.request.get_full_path())

        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
