# encoding: utf-8

from __future__ import absolute_import, unicode_literals

import django
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.test import RequestFactory, TestCase

from django_admin_index.context_processors import dashboard
from django_admin_index.models import AppGroup, AppLink

if django.VERSION >= (1, 11):
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse


class AdminIndexAppLinkTests(TestCase):
    def setUp(self):
        # Create new group...
        self.app_group = AppGroup.objects.create(name="My group", slug="my-group")
        # ...and add a link to the same group.
        self.app_link = AppLink.objects.create(
            name="Support", link="https://www.maykinmedia.nl", app_group=self.app_group
        )

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

    def test_as_list_structure(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)

        app = result[0]
        app_model = app["models"][0]

        self.assertEqual(
            app_model,
            {
                "active": False,
                "name": self.app_link.name,
                "app_label": self.app_group.slug,
                "admin_url": self.app_link.link,
            },
        )

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
            set(m["name"] for m in app_my_group["models"]), {"Support",}
        )

        app_misc = [a for a in result if a["app_label"] == "misc"][0]
        self.assertEqual(len(app_misc["models"]), 3)
        self.assertSetEqual(
            set(m["object_name"] for m in app_misc["models"]),
            {"User", "Group", "AppGroup",},
        )

    def test_context_anonymous(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = AnonymousUser()

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        # The AppLink is shown to everyone. There are no permissions set.
        self.assertEqual(len(context["dashboard_app_list"]), 1)

    def test_context_user(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self._create_user()

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        # The AppLink is shown to everyone. There are no permissions set.
        self.assertEqual(len(context["dashboard_app_list"]), 1)

    def test_context_staff_user(self):
        request = self.factory.get(reverse("admin:index"))
        user = self._create_user(is_staff=True)
        user.user_permissions.add(*Permission.objects.all())
        request.user = user

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        self.assertEqual(len(context["dashboard_app_list"]), 1)

    # @override_settings(ADMIN_INDEX_SHOW_REMAINING_APPS=True)
    # def test_context_staffuser_with_show_true(self):
    #     request = self.factory.get(reverse('admin:index'))
    #     user = self._create_user(is_staff=True)
    #     user.user_permissions.add(*Permission.objects.all())
    #     request.user = user
    #
    #     context = dashboard(request)
    #     self.assertIn('dashboard_app_list', context)
    #     self.assertEqual(len(context['dashboard_app_list']), 2)

    def test_context_superuser(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        context = dashboard(request)
        self.assertIn("dashboard_app_list", context)
        self.assertEqual(len(context["dashboard_app_list"]), 2)

    # @override_settings(ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS=False)
    # def test_context_superuser_with_show_false(self):
    #     request = self.factory.get(reverse('admin:index'))
    #     request.user = self.superuser
    #
    #     context = dashboard(request)
    #     self.assertIn('dashboard_app_list', context)
    #     self.assertEqual(len(context['dashboard_app_list']), 1)

    def test_dashboard_active_link_only_delete_permission(self):
        self.app_link.link = "/admin/auth"
        self.app_link.save()

        user = self._create_user(username="test", is_staff=True)
        permission = Permission.objects.get(name="Can delete user")
        user.user_permissions.add(permission)

        request = self.factory.get(reverse("admin:index"))
        request.user = user

        result = AppGroup.objects.as_list(request, False)

        self.assertEqual(len(result), 1)

        app = result[0]
        app_model = app["models"][0]

        self.assertEqual(
            app_model,
            {
                "active": False,
                "name": self.app_link.name,
                "app_label": self.app_group.slug,
                "admin_url": self.app_link.link,
            },
        )

    def test_dashboard_active_link_only_add_permission(self):
        self.app_link.link = "/admin/auth"
        self.app_link.save()

        user = self._create_user(username="test", is_staff=True)
        permission = Permission.objects.get(name="Can add user")
        user.user_permissions.add(permission)

        request = self.factory.get(reverse("admin:auth_user_add"))
        request.user = user

        result = AppGroup.objects.as_list(request, False)

        self.assertEqual(len(result), 1)

        app = result[0]
        app_model = app["models"][0]

        self.assertEqual(
            app_model,
            {
                "active": True,
                "name": self.app_link.name,
                "app_label": self.app_group.slug,
                "admin_url": self.app_link.link,
            },
        )

    def test_dashboard_active_link_only_change_permission(self):
        self.app_link.link = "/admin/auth"
        self.app_link.save()

        user = self._create_user(username="test", is_staff=True)
        permission = Permission.objects.get(name="Can change user")
        user.user_permissions.add(permission)

        request = self.factory.get(reverse("admin:auth_user_changelist"))
        request.user = user

        result = AppGroup.objects.as_list(request, False)

        self.assertEqual(len(result), 1)

        app = result[0]
        app_model = app["models"][0]

        self.assertEqual(
            app_model,
            {
                "active": True,
                "name": self.app_link.name,
                "app_label": self.app_group.slug,
                "admin_url": self.app_link.link,
            },
        )
