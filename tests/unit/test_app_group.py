# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from unittest import skipIf

import django
from django.contrib.admin import site
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.test import RequestFactory, TestCase

from django_admin_index import settings
from django_admin_index.context_processors import dashboard
from django_admin_index.models import AppGroup, ContentTypeProxy

if django.VERSION >= (1, 11):
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse


class AdminIndexAppGroupTests(TestCase):
    def setUp(self):
        # Create new group...
        self.app_group = AppGroup.objects.create(name='My group', slug='my-group')
        # ...find the content type for model User (it needs to be registered in the admin)
        self.ct_user = ContentTypeProxy.objects.get(app_label='auth', model='user')
        # ...and this content type to the new group.
        self.app_group.models.add(self.ct_user)

        self.factory = RequestFactory()

        self.superuser = self._create_user(username='superuser', is_staff=True, is_superuser=True)

    def _create_user(self, **kwargs):
        options = {
            'username': 'maykin',
            'email': 'info@maykinmedia.nl',
            'password': 'top_secret',
            'is_staff': False,
            'is_superuser': False,
        }
        options.update(kwargs)

        return User.objects._create_user(**options)

    @skipIf(django.VERSION < (1, 9), 'Django < 1.9 does not support site.get_app_list().')
    def test_as_list_structure(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)

        app = result[0]
        app_model = app['models'][0]

        original_app_list = site.get_app_list(request)
        original_app = [oa for oa in original_app_list if oa['app_label'] == 'auth'][0]
        original_app_model = [oam for oam in original_app['models'] if oam['object_name'] == 'User'][0]

        # The newly created app has no matches in the original app list.
        self.assertEqual(app['name'], self.app_group.name)
        self.assertEqual(app['app_label'], self.app_group.slug)

        # Attributes that are in the original structure as well.
        self.assertDictEqual(app_model['perms'], original_app_model['perms'])
        for key in ['name', 'object_name', 'admin_url', 'add_url']:
            self.assertEqual(app_model[key], original_app_model[key])

        # Attributes copied from the original app to the model, just for reference as to where the app originally
        # belonged to.
        for key in ['app_label', 'app_url', 'has_module_perms']:
            self.assertEqual(app_model[key], original_app[key])

    @skipIf(django.VERSION < (1, 9), 'Django < 1.9 does not support site.get_app_list().')
    def test_as_list_structure_default_options(self):
        settings.AUTO_CREATE_APP_GROUP = True
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)

        app = result[0]
        app_model = app['models'][0]

        original_app_list = site.get_app_list(request)
        original_app = [oa for oa in original_app_list if oa['app_label'] == 'auth'][0]
        original_app_model = [oam for oam in original_app['models'] if oam['object_name'] == 'User'][0]

        # The newly created app has no matches in the original app list.
        self.assertEqual(app['name'], self.app_group.name)
        self.assertEqual(app['app_label'], self.app_group.slug)

        # Attributes that are in the original structure as well.
        self.assertDictEqual(app_model['perms'], original_app_model['perms'])
        for key in ['name', 'object_name', 'admin_url', 'add_url']:
            self.assertEqual(app_model[key], original_app_model[key])

        # Attributes copied from the original app to the model, just for reference as to where the app originally
        # belonged to.
        for key in ['app_label', 'app_url', 'has_module_perms']:
            self.assertEqual(app_model[key], original_app[key])

        settings.AUTO_CREATE_APP_GROUP = False

    def test_only_match_auto_create_group_on_slug(self):
        settings.AUTO_CREATE_APP_GROUP = True
        app_group = AppGroup.objects.create(name='My group', slug='auth')
        self.assertEqual(app_group.models.count(), 0)
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)
        self.assertEqual(app_group.models.count(), 1)
        settings.AUTO_CREATE_APP_GROUP = False

    def test_as_list_without_include_remaining(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)

        app = result[0]

        self.assertEqual(app['app_label'], self.app_group.slug)
        self.assertEqual(len(app['models']), 1)

    def test_as_list_with_include_remaining(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, True)
        self.assertEqual(len(result), 2)

        self.assertSetEqual(
            set([a['app_label'] for a in result]),
            {self.app_group.slug, 'misc'}
        )

        app_my_group = [a for a in result if a['app_label'] == self.app_group.slug][0]
        self.assertEqual(len(app_my_group['models']), 1)
        self.assertSetEqual(
            set(m['object_name'] for m in app_my_group['models']),
            {'User', }
        )

        app_misc = [a for a in result if a['app_label'] == 'misc'][0]
        self.assertEqual(len(app_misc['models']), 2)
        self.assertSetEqual(
            set(m['object_name'] for m in app_misc['models']),
            {'Group', 'AppGroup', }
        )

    def test_context_anonymous(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = AnonymousUser()

        context = dashboard(request)
        self.assertIn('dashboard_app_list', context)
        self.assertEqual(len(context['dashboard_app_list']), 0)

    def test_context_user(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = self._create_user()

        context = dashboard(request)
        self.assertIn('dashboard_app_list', context)
        self.assertEqual(len(context['dashboard_app_list']), 0)

    def test_context_staff_user(self):
        request = self.factory.get(reverse('admin:index'))
        user = self._create_user(is_staff=True)
        user.user_permissions.add(*Permission.objects.all())
        request.user = user

        context = dashboard(request)
        self.assertIn('dashboard_app_list', context)
        self.assertEqual(len(context['dashboard_app_list']), 1)

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
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        context = dashboard(request)
        self.assertIn('dashboard_app_list', context)
        self.assertEqual(len(context['dashboard_app_list']), 2)

    # @override_settings(ADMIN_INDEX_SHOW_REMAINING_APPS_TO_SUPERUSERS=False)
    # def test_context_superuser_with_show_false(self):
    #     request = self.factory.get(reverse('admin:index'))
    #     request.user = self.superuser
    #
    #     context = dashboard(request)
    #     self.assertIn('dashboard_app_list', context)
    #     self.assertEqual(len(context['dashboard_app_list']), 1)
