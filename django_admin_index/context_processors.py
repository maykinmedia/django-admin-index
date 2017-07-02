from django.urls import reverse

from . import settings
from .models import AppGroup


def dashboard(request):
    if hasattr(request, 'user') and hasattr(request, 'path') and request.path == reverse('admin:index'):
        show_remaining_apps = settings.SHOW_REMAINING_APPS or \
            (settings.SHOW_REMAINING_APPS_TO_SUPERUSERS and request.user.is_superuser)

        app_list = AppGroup.objects.as_list(request, show_remaining_apps)

        return {
            'dashboard_app_list': app_list,
        }

    return {}
