from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils.translation import override

from django_admin_index.models import AppGroup, AppLink, ContentTypeProxy


class NestedAppGroupValidationTests(TestCase):
    def setUp(self):
        self.parent = AppGroup.objects.create(name="Parent", slug="parent")
        self.child = AppGroup.objects.create(
            name="Child", slug="child", parent=self.parent
        )

    def test_top_level_and_child_are_valid(self):
        self.parent.clean()
        self.child.clean()

    def test_group_cannot_be_its_own_parent(self):
        self.parent.parent = self.parent

        with self.assertRaises(ValidationError) as cm:
            self.parent.clean()

        self.assertIn("parent", cm.exception.message_dict)

    def test_only_two_levels_of_nesting(self):
        grandchild = AppGroup(name="Grandchild", slug="grandchild", parent=self.child)

        with self.assertRaises(ValidationError) as cm:
            grandchild.clean()

        self.assertIn("parent", cm.exception.message_dict)

    def test_group_with_children_cannot_be_nested(self):
        other = AppGroup.objects.create(name="Other", slug="other")
        self.parent.parent = other

        with self.assertRaises(ValidationError) as cm:
            self.parent.clean()

        self.assertIn("parent", cm.exception.message_dict)

    def test_save_rejects_invalid_parent(self):
        with self.assertRaises(ValidationError):
            AppGroup.objects.create(
                name="Grandchild", slug="grandchild", parent=self.child
            )
        self.assertFalse(AppGroup.objects.filter(slug="grandchild").exists())

    def test_database_rejects_self_parent(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            AppGroup.objects.filter(pk=self.parent.pk).update(parent=self.parent.pk)

    def test_deleting_parent_keeps_children(self):
        self.parent.delete()
        self.child.refresh_from_db()

        self.assertIsNone(self.child.parent)

    def _top_level(self):
        return list(
            AppGroup.objects.filter(parent__isnull=True)
            .order_by("order")
            .values_list("name", "order")
        )

    def test_deleting_parent_appends_children_to_top_level(self):
        AppGroup.objects.create(name="Other", slug="other")
        second = AppGroup.objects.create(
            name="Second child", slug="second-child", parent=self.parent
        )

        self.parent.delete()

        self.assertEqual(
            self._top_level(), [("Other", 0), ("Child", 1), ("Second child", 2)]
        )
        # ordering keeps working among the promoted groups
        AppGroup.objects.get(pk=second.pk).up()
        self.assertEqual(
            self._top_level(), [("Other", 0), ("Second child", 1), ("Child", 2)]
        )

    def test_bulk_deleting_parent_appends_children_to_top_level(self):
        AppGroup.objects.create(name="Other", slug="other")

        # the admin "delete selected" action deletes through a queryset
        AppGroup.objects.filter(pk=self.parent.pk).delete()

        self.assertEqual(self._top_level(), [("Other", 0), ("Child", 1)])


class NestedAppGroupAsListTests(TestCase):
    def setUp(self):
        self.parent = AppGroup.objects.create(name="Parent", slug="parent")
        self.child = AppGroup.objects.create(
            name="Child", slug="child", parent=self.parent
        )
        self.ct_user = ContentTypeProxy.objects.get(app_label="auth", model="user")
        self.ct_group = ContentTypeProxy.objects.get(app_label="auth", model="group")
        self.child.models.add(self.ct_user)

        self.factory = RequestFactory()
        self.superuser = User.objects._create_user(
            username="superuser",
            email="info@maykinmedia.nl",
            password="top_secret",
            is_staff=True,
            is_superuser=True,
        )

    def _as_list(self, path=None, include_remaining=False):
        request = self.factory.get(path or reverse("admin:index"))
        request.user = self.superuser
        return AppGroup.objects.as_list(request, include_remaining)

    def test_child_group_is_nested_under_parent(self):
        result = self._as_list()

        self.assertEqual(len(result), 1)
        parent = result[0]
        self.assertEqual(parent["app_label"], "parent")
        self.assertEqual(parent["models"], [])
        self.assertEqual(len(parent["children"]), 1)
        child = parent["children"][0]
        self.assertEqual(child["name"], "Child")
        self.assertEqual(child["app_label"], "child")
        self.assertEqual([m["object_name"] for m in child["models"]], ["User"])

    def test_parent_own_models_are_listed_next_to_children(self):
        self.parent.models.add(self.ct_group)

        result = self._as_list()

        parent = result[0]
        self.assertEqual([m["object_name"] for m in parent["models"]], ["Group"])
        self.assertEqual(
            [m["object_name"] for m in parent["children"][0]["models"]], ["User"]
        )

    def test_model_in_parent_and_child_is_only_shown_in_child(self):
        self.parent.models.add(self.ct_user)

        result = self._as_list()

        parent = result[0]
        self.assertEqual(parent["models"], [])
        self.assertEqual(
            [m["object_name"] for m in parent["children"][0]["models"]], ["User"]
        )

    def test_empty_child_group_is_omitted(self):
        self.child.models.clear()
        self.parent.models.add(self.ct_group)

        result = self._as_list()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["children"], [])

    def test_parent_without_content_is_omitted(self):
        self.child.models.clear()

        result = self._as_list()

        self.assertEqual(result, [])

    def test_child_models_are_not_in_miscellaneous(self):
        result = self._as_list(include_remaining=True)

        misc = [app for app in result if app["app_label"] == "misc"]
        self.assertEqual(len(misc), 1)
        self.assertNotIn("User", [m["object_name"] for m in misc[0]["models"]])

    def test_active_child_marks_parent_active(self):
        result = self._as_list(path=reverse("admin:auth_user_changelist"))

        parent = result[0]
        self.assertTrue(parent["active"])
        self.assertTrue(parent["children"][0]["active"])

    def test_inactive_child(self):
        self.parent.models.add(self.ct_group)

        result = self._as_list(path=reverse("admin:auth_group_changelist"))

        parent = result[0]
        self.assertTrue(parent["active"])
        self.assertFalse(parent["children"][0]["active"])

    def test_app_link_in_child_group(self):
        AppLink.objects.create(app_group=self.child, name="Support", link="/support/")

        result = self._as_list(path="/support/tickets/")

        child = result[0]["children"][0]
        self.assertEqual([m["name"] for m in child["models"]], ["Support", "Users"])
        self.assertEqual(child["models"][0]["app_label"], "child")
        self.assertTrue(child["active"])
        self.assertTrue(result[0]["active"])

    def test_app_link_in_parent_and_child_is_only_shown_in_child(self):
        AppLink.objects.create(app_group=self.parent, name="Support", link="/support/")
        AppLink.objects.create(app_group=self.child, name="Support", link="/support/")

        result = self._as_list()

        parent = result[0]
        self.assertEqual(parent["models"], [])
        self.assertEqual(
            [m["name"] for m in parent["children"][0]["models"]], ["Support", "Users"]
        )

    def test_children_are_ordered_among_siblings(self):
        AppGroup.objects.create(name="Other", slug="other")
        second = AppGroup.objects.create(
            name="Second child", slug="second-child", parent=self.parent
        )
        second.models.add(self.ct_group)

        result = self._as_list()
        self.assertEqual(
            [c["name"] for c in result[0]["children"]], ["Child", "Second child"]
        )

        second.top()

        result = self._as_list()
        self.assertEqual(
            [c["name"] for c in result[0]["children"]], ["Second child", "Child"]
        )
        # order values are relative to the parent, not global
        self.assertEqual(
            list(self.parent.children.values_list("order", flat=True)), [0, 1]
        )

    def test_localized_names(self):
        self.parent.translations = {"nl": "Ouder"}
        self.parent.save()
        self.child.translations = {"nl": "Kind"}
        self.child.save()

        with override("nl"):
            result = self._as_list()

        self.assertEqual(result[0]["name"], "Ouder")
        self.assertEqual(result[0]["children"][0]["name"], "Kind")

    def test_localized_name_falls_back_to_name(self):
        self.child.translations = {"en": "Child EN"}
        self.child.save()

        with override("nl"):
            result = self._as_list()

        self.assertEqual(result[0]["children"][0]["name"], "Child")

    def test_grandchild_from_unvalidated_data_is_shown_as_top_level(self):
        grandchild = AppGroup.objects.create(name="Grandchild", slug="grandchild")
        grandchild.models.add(self.ct_group)
        # bypass validation, as fixtures or raw updates would
        AppGroup.objects.filter(pk=grandchild.pk).update(parent=self.child)

        result = self._as_list()

        self.assertEqual([app["name"] for app in result], ["Parent", "Grandchild"])
        self.assertEqual([c["name"] for c in result[0]["children"]], ["Child"])
        self.assertNotIn("children", result[1])
        self.assertEqual([m["object_name"] for m in result[1]["models"]], ["Group"])

    def test_child_of_filtered_out_parent_is_shown_as_top_level(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        result = AppGroup.objects.exclude(pk=self.parent.pk).as_list(request, False)

        self.assertEqual([app["name"] for app in result], ["Child"])
        self.assertEqual([m["object_name"] for m in result[0]["models"]], ["User"])

    def test_number_of_queries_is_constant(self):
        request = self.factory.get(reverse("admin:index"))
        request.user = self.superuser

        with CaptureQueriesContext(connection) as ctx:
            AppGroup.objects.as_list(request, False)
        num_queries = len(ctx)

        for i in range(3):
            child = AppGroup.objects.create(
                name=f"Child {i}", slug=f"child-{i}", parent=self.parent
            )
            child.models.add(self.ct_group)
            AppLink.objects.create(app_group=child, name="Link", link=f"/link-{i}/")

        with self.assertNumQueries(num_queries):
            AppGroup.objects.as_list(request, False)


class NestedAppGroupIntegrationTests(TestCase):
    def setUp(self):
        self.parent = AppGroup.objects.create(name="Parent group", slug="parent")
        self.child = AppGroup.objects.create(
            name="Child group", slug="child", parent=self.parent
        )
        self.child.models.add(
            ContentTypeProxy.objects.get(app_label="auth", model="user")
        )
        User.objects._create_user(
            username="superuser",
            email="user@example.com",
            password="top_secret",
            is_staff=True,
            is_superuser=True,
        )
        self.assertTrue(self.client.login(username="superuser", password="top_secret"))

    def test_index_page_renders_nested_groups(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Parent group")
        self.assertContains(response, "Child group")
        self.assertContains(response, reverse("admin:auth_user_changelist"))
        self.assertContains(response, "djai-dropdown-menu__submenu")
        self.assertContains(response, "djai-app-group-table--nested")
        # application groups have no app index page, so captions are not links
        self.assertNotContains(response, 'href="#"')
        self.assertNotContains(response, 'href=""')

    def test_changelist_keeps_children_under_their_parent(self):
        AppGroup.objects.create(name="Child 2", slug="child-2", parent=self.parent)
        other = AppGroup.objects.create(name="Other", slug="other")
        AppGroup.objects.create(name="Other child", slug="other-child", parent=other)
        first = AppGroup.objects.create(name="First", slug="first")
        first.top()

        response = self.client.get(reverse("admin:admin_index_appgroup_changelist"))

        self.assertEqual(
            [group.name for group in response.context["cl"].result_list],
            ["First", "Parent group", "Child group", "Child 2", "Other", "Other child"],
        )

    def test_admin_rejects_nesting_below_two_levels(self):
        response = self.client.post(
            reverse("admin:admin_index_appgroup_add"),
            {
                "name": "Grandchild",
                "slug": "grandchild",
                "translations": "{}",
                "parent": self.child.pk,
                "applink_set-TOTAL_FORMS": "0",
                "applink_set-INITIAL_FORMS": "0",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(AppGroup.objects.filter(slug="grandchild").exists())
        self.assertIn("parent", response.context["adminform"].form.errors)
