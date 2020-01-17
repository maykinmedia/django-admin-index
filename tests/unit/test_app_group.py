# encoding: utf-8

from __future__ import absolute_import, unicode_literals

import django
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.test import RequestFactory, TestCase, override_settings

from django_admin_index.conf import settings
from django_admin_index.context_processors import dashboard
from django_admin_index.models import AppGroup, ContentTypeProxy

if django.VERSION >= (1, 11):
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse


class AdminIndexAppGroupTests(TestCase):
    def setUp(self):
        # Create new group...
        self.app_group = AppGroup.objects.create(name="My group", slug="my-group")
        # ...find the content type for model User (it needs to be registered in the admin)
        self.ct_user = ContentTypeProxy.objects.get(app_label="auth", model="user")
        # ...and this content type to the new group.
        self.app_group.models.add(self.ct_user)

        # ...find the content type for model Group (it needs to be registered in the admin) and don't do anything
        # with it
        self.ct_group = ContentTypeProxy.objects.get(app_label="auth", model="group")

        self.factory = RequestFactory()

        self.superuser = self._create_user(
            username="superuser", is_staff=True, is_superuser=True
        )

    def _create_user(self, **kwargs):
        options = {
            "username": "maykin",
            "email": "info@maykinmedia.nl",
            "password": "top_secret",
            "is_staff": False,
            "is_superuser": False,
        }
        options.update(kwargs)

        return User.objects._create_user(**options)

    @override_settings(ADMIN_INDEX_AUTO_CREATE_APP_GROUP=True)
    def test_only_create_group_when_enabled(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        self.assertEqual(AppGroup.objects.count(), 1)
        AppGroup.objects.as_list(request, False)
        self.assertEqual(AppGroup.objects.count(), 3)

    def test_dont_create_group_when_disabled(self):
        self.assertFalse(settings.AUTO_CREATE_APP_GROUP)

        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        self.assertEqual(AppGroup.objects.count(), 1)
        AppGroup.objects.as_list(request, False)
        self.assertEqual(AppGroup.objects.count(), 1)

    @override_settings(ADMIN_INDEX_AUTO_CREATE_APP_GROUP=True)
    def test_dont_update_existing_groups(self):
        # Create an "auth` group. The Group model should not be added. It would be if there was no group yet.
        app_group = AppGroup.objects.create(name="My group", slug="auth")
        self.assertEqual(app_group.models.count(), 0)

        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        AppGroup.objects.as_list(request, False)
        self.assertEqual(app_group.models.count(), 0)

    def test_as_list_without_include_remaining(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)

        app = result[0]

        self.assertEqual(app["app_label"], self.app_group.slug)
        self.assertEqual(len(app["models"]), 1)

    def test_as_list_with_include_remaining(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, True)
        self.assertEqual(len(result), 2)

        self.assertSetEqual(
            set([a["app_label"] for a in result]), {self.app_group.slug, "misc"}
        )

        app_my_group = [a for a in result if a["app_label"] == self.app_group.slug][0]
        self.assertEqual(len(app_my_group["models"]), 1)
        self.assertSetEqual(
            set(m["object_name"] for m in app_my_group["models"]), {"User",}
        )

        app_misc = [a for a in result if a["app_label"] == "misc"][0]
        self.assertEqual(len(app_misc["models"]), 2)
        self.assertSetEqual(
            set(m["object_name"] for m in app_misc["models"]), {"Group", "AppGroup",}
        )

    def test_context_anonymous(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = AnonymousUser()

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        self.assertEqual(len(context["dashboard_app_list"]), 0)

    def test_context_user(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self._create_user()

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        self.assertEqual(len(context["dashboard_app_list"]), 0)

    def test_context_staff_user_with_show_false(self):
        self.assertFalse(settings.SHOW_REMAINING_APPS)

        request = self.factory.get(reverse("admin:index"))
        user = self._create_user(is_staff=True)
        user.user_permissions.add(*Permission.objects.all())
        request.user = user

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        self.assertEqual(len(context["dashboard_app_list"]), 1)

    @override_settings(ADMIN_INDEX_SHOW_REMAINING_APPS=True)
    def test_context_staffuser_with_show_true(self):
        request = self.factory.get(reverse("admin:index"))
        user = self._create_user(is_staff=True)
        user.user_permissions.add(*Permission.objects.all())
        request.user = user

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        self.assertEqual(len(context["dashboard_app_list"]), 2)

    def test_context_superuser_with_show_true(self):
        self.assertTrue(settings.SHOW_REMAINING_APPS_TO_SUPERUSERS)

        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        self.assertEqual(len(context["dashboard_app_list"]), 2)

    @override_settings(ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS=False)
    def test_context_superuser_with_show_false(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        self.assertEqual(len(context["dashboard_app_list"]), 1)
