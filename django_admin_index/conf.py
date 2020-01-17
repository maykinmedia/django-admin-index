from __future__ import absolute_import, unicode_literals

from django.conf import settings as django_settings


class Settings:
    @property
    def SHOW_REMAINING_APPS(self):
        return getattr(django_settings, "ADMIN_INDEX_SHOW_REMAINING_APPS", False)

    @property
    def SHOW_REMAINING_APPS_TO_SUPERUSERS(self):
        return getattr(
            django_settings, "ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS", True
        )

    def show_remaining_apps(self, is_superuser):
        if self.SHOW_REMAINING_APPS:
            return True

        return settings.SHOW_REMAINING_APPS_TO_SUPERUSERS and is_superuser

    @property
    def AUTO_CREATE_APP_GROUP(self):
        return getattr(django_settings, "ADMIN_INDEX_AUTO_CREATE_APP_GROUP", False)

    @property
    def SHOW_MENU(self):
        return getattr(django_settings, "ADMIN_INDEX_SHOW_MENU", True)

    @property
    def HIDE_APP_INDEX_PAGES(self):
        return getattr(django_settings, "ADMIN_INDEX_HIDE_APP_INDEX_PAGES", True)

    def as_dict(self):
        """
        Returns a `dict` with all settings.

        :return: A `dict` with settings.
        """
        return {k: getattr(self, k) for k in dir(self) if k.upper() == k}


settings = Settings()
