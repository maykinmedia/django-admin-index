from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig
from django.core.checks import Tags, Warning, register
from django.utils.translation import ugettext_lazy as _

__all__ = ['AdminIndexConfig']


class AdminIndexConfig(AppConfig):
    """Default configuration for the django_admin_index app."""

    name = 'django_admin_index'
    label = 'admin_index'
    verbose_name = _('Admin Index')

    def ready(self):
        register(check_admin_index_app, Tags.compatibility)


def check_admin_index_app(app_configs, **kwargs):
    from django.conf import settings
    issues = []
    try:
        if settings.INSTALLED_APPS.index(AdminIndexConfig.name) > \
                settings.INSTALLED_APPS.index('django.contrib.admin'):
            issues.append(
                Warning('You should put \'{}\' before \'django.contrib.admin\' in your INSTALLED_APPS.'.format(
                    AdminIndexConfig.name
                ))
            )
    except ValueError:
        issues.append(
            Warning('You are missing \'django.contrib.admin\' in your INSTALLED_APPS.')
        )

    return issues
