from __future__ import absolute_import, unicode_literals

from django.conf import settings as django_settings

SHOW_REMAINING_APPS = getattr(django_settings, 'ADMIN_INDEX_SHOW_REMAINING_APPS', False)

SHOW_REMAINING_APPS_TO_SUPERUSERS = getattr(django_settings, 'ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS', True)

AUTO_CREATE_APP_GROUP = getattr(django_settings, 'ADMIN_INDEX_AUTO_CREATE_APP_GROUP', False)
