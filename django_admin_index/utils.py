from django_admin_index.conf import settings


def should_display_dropdown_menu(request):
    return settings.SHOW_MENU and request.user.is_authenticated and request.user.is_staff
