from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig, apps
from django.core.checks import Error, Tags, Warning, register
from django.utils.translation import ugettext_lazy as _

__all__ = ["AdminIndexConfig"]


class AdminIndexConfig(AppConfig):
    """Default configuration for the django_admin_index app."""

    name = "django_admin_index"
    label = "admin_index"
    verbose_name = _("Admin Index")

    def ready(self):
        register(check_admin_index_app, Tags.compatibility)
        register(check_admin_index_context_processor, Tags.compatibility)
        register(check_request_context_processor, Tags.compatibility)


def check_admin_index_app(app_configs, **kwargs):
    from django.conf import settings

    issues = []
    app_config_names = [app_config.name for app_config in apps.get_app_configs()]

    try:
        if app_config_names.index(AdminIndexConfig.name) > app_config_names.index(
            "django.contrib.admin"
        ):
            issues.append(
                Warning(
                    "You should put '{}' before 'django.contrib.admin' in your INSTALLED_APPS.".format(
                        AdminIndexConfig.name
                    )
                )
            )
    except ValueError:
        issues.append(
            Warning("You are missing 'django.contrib.admin' in your INSTALLED_APPS.")
        )

    return issues


def check_admin_index_context_processor(app_configs, **kwargs):
    from django.conf import settings

    issues = []
    context_procesor = "{}.context_processors.dashboard".format(AdminIndexConfig.name)

    for engine in settings.TEMPLATES:
        if "OPTIONS" in engine and "context_processors" in engine["OPTIONS"]:
            if context_procesor in engine["OPTIONS"]["context_processors"]:
                issues.append(
                    Error(
                        "You should remove '{}' from your TEMPLATES.OPTIONS.context_processors.".format(
                            context_procesor
                        )
                    )
                )
                break

    return issues


def check_request_context_processor(app_configs, **kwargs):
    from django.conf import settings

    issues = []
    found = False
    context_procesor = "django.template.context_processors.request"

    for engine in settings.TEMPLATES:
        if "OPTIONS" in engine and "context_processors" in engine["OPTIONS"]:
            if context_procesor in engine["OPTIONS"]["context_processors"]:
                found = True
                break

    if not found:
        issues.append(
            Warning(
                "You are missing '{}' in your TEMPLATES.OPTIONS.context_processors.".format(
                    context_procesor
                )
            )
        )

    return issues
