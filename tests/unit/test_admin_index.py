# encoding: utf-8

from __future__ import absolute_import, unicode_literals

from unittest import skipIf

import django
from django.contrib.admin import site
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.test import RequestFactory, TestCase, override_settings
from mock import Mock, patch

from django_admin_index.apps import check_admin_index_app
from django_admin_index.compat.django18 import get_app_list
from django_admin_index.context_processors import dashboard
from django_admin_index.models import AppGroup, AppLink, ContentTypeProxy

if django.VERSION >= (1, 11):
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse


class AdminIndexTests(TestCase):
    def setUp(self):
        # Create new group...
        self.app_group = AppGroup.objects.create(name='My group', slug='my-group')
        # ...find the content type for model User (it needs to be registered in the admin)
        self.ct_user = ContentTypeProxy.objects.get(app_label='auth', model='user')
        # ...and this content type to the new group.
        self.app_group.models.add(self.ct_user)
        # ...and add a link to the same group.
        self.app_link = AppLink.objects.create(
            name='Support', link='https://www.maykinmedia.nl', app_group=self.app_group)

    def test_app_group_str(self):
        self.assertEqual(str(self.app_group), 'My group')

    def test_app_link_str(self):
        self.assertEqual(str(self.app_link), 'Support')

    def test_app_content_type_proxy_str(self):
        self.assertEqual(str(self.ct_user), 'auth.User')

    def test_installed_apps_check_success(self):
        result = check_admin_index_app([])
        self.assertEquals(len(result), 0)

    @override_settings(INSTALLED_APPS=['django.contrib.admin', 'django_admin_index'])
    def test_installed_apps_order_check(self):
        result = check_admin_index_app([])
        self.assertEquals(len(result), 1)

    @override_settings(INSTALLED_APPS=['django_admin_index'])
    def test_installed_apps_admin_check(self):
        result = check_admin_index_app([])
        self.assertEquals(len(result), 1)


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

    def test_as_list_structure_compat_django18(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)

        app = result[0]
        app_model = app['models'][0]

        original_app_list = get_app_list(site, request)
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

    @patch('django_admin_index.models.django', Mock(VERSION=(1, 8, 18, 'mock', 0)))
    def test_as_list_structure_with_django18(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)

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


class AdminIndexAppLinkTests(TestCase):
    def setUp(self):
        # Create new group...
        self.app_group = AppGroup.objects.create(name='My group', slug='my-group')
        # ...and add a link to the same group.
        self.app_link = AppLink.objects.create(
            name='Support', link='https://www.maykinmedia.nl', app_group=self.app_group)

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

    def test_as_list_structure(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = self.superuser

        result = AppGroup.objects.as_list(request, False)
        self.assertEqual(len(result), 1)

        app = result[0]
        app_model = app['models'][0]

        self.assertEqual(app_model, {
            'name': self.app_link.name,
            'app_label': self.app_group.slug,
            'admin_url': self.app_link.link,
        })

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
            set(m['name'] for m in app_my_group['models']),
            {'Support', }
        )

        app_misc = [a for a in result if a['app_label'] == 'misc'][0]
        self.assertEqual(len(app_misc['models']), 3)
        self.assertSetEqual(
            set(m['object_name'] for m in app_misc['models']),
            {'User', 'Group', 'AppGroup', }
        )

    def test_context_anonymous(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = AnonymousUser()

        context = dashboard(request)
        self.assertIn('dashboard_app_list', context)
        # The AppLink is shown to everyone. There are no permissions set.
        self.assertEqual(len(context['dashboard_app_list']), 1)

    def test_context_user(self):
        request = self.factory.get(reverse('admin:index'))
        request.user = self._create_user()

        context = dashboard(request)
        self.assertIn('dashboard_app_list', context)
        # The AppLink is shown to everyone. There are no permissions set.
        self.assertEqual(len(context['dashboard_app_list']), 1)

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


class AdminIndexIntegrationTests(TestCase):
    def setUp(self):
        self.superuser = User.objects._create_user(
            username='superuser', email='user@example.com', password='top_secret', is_staff=True, is_superuser=True)
        self.assertTrue(self.client.login(username=self.superuser.username, password='top_secret'))

        self.auth_app_list_url = reverse('admin:app_list', kwargs={'app_label': 'auth'})

    def test_app_groups_in_context(self):
        response = self.client.get(reverse('admin:index'))

        self.assertIn('dashboard_app_list', response.context)
        self.assertGreater(len(response.context['dashboard_app_list']), 0)

    def test_no_app_groups_in_context_outside_index(self):
        response = self.client.get(reverse('admin:auth_user_changelist'))

        self.assertNotIn('dashboard_app_list', response.context)

    @skipIf(django.VERSION < (1, 9), 'Django < 1.9 does not support template origins.')
    def test_app_groups_in_index(self):
        response = self.client.get(reverse('admin:index'))

        template_path = response.templates[0].origin.name.replace('\\', '/')
        self.assertTrue(template_path.endswith('django_admin_index/templates/admin/index.html'), template_path)

    def test_no_app_list_links_index(self):
        response = self.client.get(reverse('admin:index'))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_change_form(self):
        response = self.client.get(reverse('admin:auth_user_change', args=(self.superuser.pk, )))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_change_list(self):
        response = self.client.get(reverse('admin:auth_user_changelist'))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_delete_confirmation(self):
        response = self.client.get(reverse('admin:auth_user_delete', args=(self.superuser.pk, )))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_delete_selected_confirmation(self):
        response = self.client.post(reverse('admin:auth_user_changelist'), data={
            'action': 'delete_selected',
            'select_across': 0,
            'index': 0,
            '_selected_action': self.superuser.pk,
        })
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)

    def test_no_app_list_links_object_history(self):
        response = self.client.get(reverse('admin:auth_user_history', args=(self.superuser.pk, )))
        html = response.content.decode('utf-8')

        self.assertNotIn('{}"'.format(self.auth_app_list_url), html)
