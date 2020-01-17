from __future__ import absolute_import, unicode_literals

from django.contrib.admin import site

from .conf import settings
from .models import AppGroup


def dashboard(request):
    if hasattr(request, "user") and hasattr(request, "path"):  # noqa
        # Get the new app_list.
        app_list = AppGroup.objects.as_list(
            request, settings.show_remaining_apps(request.user.is_superuser)
        )

        # Use default app_list if there were no groups and no "misc" section.
        if not app_list:
            app_list = site.get_app_list(request)

        return {
            "dashboard_app_list": app_list,
            "admin_index_settings": settings.as_dict(),
        }

    return {}
