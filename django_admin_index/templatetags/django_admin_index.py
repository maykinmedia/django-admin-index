from django.contrib.admin import site
from django.core.exceptions import ImproperlyConfigured
from django.template import Library
from django.utils.module_loading import import_string

from ..conf import settings
from ..models import AppGroup

register = Library()


@register.simple_tag(takes_context=True)
def dashboard_app_list(context):
    try:
        request = context["request"]
    except KeyError:
        raise ImproperlyConfigured(
            "Django admin index requires 'django.template.context_processors.request' to be configured."
        )

    # Get the new app_list.
    app_list = AppGroup.objects.as_list(
        request, settings.show_remaining_apps(request.user.is_superuser)
    )

    # Use default app_list if there were no groups and no "misc" section.
    if not app_list:
        app_list = site.get_app_list(request)

    return app_list


@register.simple_tag()
def admin_index_settings():
    return settings.as_dict()


@register.simple_tag
def display_dropdown_menu(request):
    func = import_string(settings.DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION)
    return func(request)
