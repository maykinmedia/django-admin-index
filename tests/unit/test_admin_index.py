# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from django.test import TestCase, override_settings

from django_admin_index.apps import (
    check_admin_index_app,
    check_admin_index_context_processor,
    check_request_context_processor,
)
from django_admin_index.models import AppGroup, AppLink, ContentTypeProxy


class AdminIndexTests(TestCase):
    def setUp(self):
        # Create new group...
        self.app_group = AppGroup.objects.create(name="My group", slug="my-group")
        # ...find the content type for model User (it needs to be registered in the admin)
        self.ct_user = ContentTypeProxy.objects.get(app_label="auth", model="user")
        # ...and this content type to the new group.
        self.app_group.models.add(self.ct_user)
        # ...and add a link to the same group.
        self.app_link = AppLink.objects.create(
            name="Support", link="https://www.maykinmedia.nl", app_group=self.app_group
        )

    def test_app_group_str(self):
        self.assertEqual(str(self.app_group), "My group")

    def test_app_link_str(self):
        self.assertEqual(str(self.app_link), "Support")

    def test_app_content_type_proxy_str(self):
        self.assertEqual(str(self.ct_user), "auth.User")

    def test_check_admin_index_app_success(self):
        result = check_admin_index_app([])
        self.assertEqual(len(result), 0)

    @override_settings(
        INSTALLED_APPS=["django_admin_index", "django.contrib.admin.apps.AdminConfig"]
    )
    def test_check_admin_index_app_with_custom_admin_success(self):
        result = check_admin_index_app([])
        self.assertEqual(len(result), 0)

    @override_settings(INSTALLED_APPS=["django.contrib.admin", "django_admin_index"])
    def test_check_admin_index_app_after_admin_app(self):
        result = check_admin_index_app([])
        self.assertEqual(len(result), 1)

    @override_settings(
        INSTALLED_APPS=["django.contrib.admin.apps.AdminConfig", "django_admin_index"]
    )
    def test_check_admin_index_app_after_admin_app_with_custom_admin(self):
        result = check_admin_index_app([])
        self.assertEqual(len(result), 1)

    @override_settings(INSTALLED_APPS=["django_admin_index"])
    def test_check_admin_index_app_missing(self):
        result = check_admin_index_app([])
        self.assertEqual(len(result), 1)

    @override_settings(TEMPLATES=[{"OPTIONS": {"context_processors": []}}])
    def test_check_admin_index_context_process_present(self):
        result = check_admin_index_context_processor([])
        self.assertEqual(len(result), 0)

    @override_settings(
        TEMPLATES=[
            {
                "OPTIONS": {
                    "context_processors": [
                        "django_admin_index.context_processors.dashboard"
                    ]
                }
            }
        ]
    )
    def test_check_admin_index_context_process_present(self):
        result = check_admin_index_context_processor([])
        self.assertEqual(len(result), 1)

    @override_settings(TEMPLATES=[{}])
    def test_check_admin_index_context_process_no_options(self):
        result = check_admin_index_context_processor([])
        self.assertEqual(len(result), 0)

    @override_settings(TEMPLATES=[{"OPTIONS": {}}])
    def test_check_admin_index_context_process_no_context_processors(self):
        result = check_admin_index_context_processor([])
        self.assertEqual(len(result), 0)

    @override_settings(TEMPLATES=[{"OPTIONS": {"context_processors": []}}])
    def test_check_request_context_process_missing(self):
        result = check_request_context_processor([])
        self.assertEqual(len(result), 1)

    @override_settings(
        TEMPLATES=[
            {
                "OPTIONS": {
                    "context_processors": ["django.template.context_processors.request"]
                }
            }
        ]
    )
    def test_check_request_context_process_present(self):
        result = check_request_context_processor([])
        self.assertEqual(len(result), 0)

    @override_settings(TEMPLATES=[{}])
    def test_check_request_context_process_no_options(self):
        result = check_request_context_processor([])
        self.assertEqual(len(result), 1)

    @override_settings(TEMPLATES=[{"OPTIONS": {}}])
    def test_check_request_context_process_no_context_processors(self):
        result = check_request_context_processor([])
        self.assertEqual(len(result), 1)
