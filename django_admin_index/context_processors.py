from __future__ import absolute_import, unicode_literals

import django

from . import settings
from .models import AppGroup

if django.VERSION >= (1, 11):
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse


def dashboard(request):
    if hasattr(request, 'user') and hasattr(request, 'path') and request.path == reverse('admin:index'):  # noqa
        show_remaining_apps = settings.SHOW_REMAINING_APPS or \
            (settings.SHOW_REMAINING_APPS_TO_SUPERUSERS and request.user.is_superuser)  # noqa

        app_list = AppGroup.objects.as_list(request, show_remaining_apps)

        return {
            'dashboard_app_list': app_list,
        }

    return {}
