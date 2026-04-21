from collections import defaultdict
from typing import Any

from django.contrib.admin import site
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Prefetch
from django.http import HttpRequest
from django.urls import reverse
from django.utils.text import capfirst
from django.utils.translation import get_language, gettext_lazy as _

from ordered_model.models import OrderedModel, OrderedModelManager, OrderedModelQuerySet

from .conf import settings
from .translations import TranslationsMixin


def _model_key(model_dict: dict[str, Any]) -> str:
    """
    Return a key that identifies an entry in the app list.

    Entries are either a Django model (identified by app label and object name)
    or an AppLink (identified by its URL).
    """
    if "object_name" in model_dict:
        return "{}.{}".format(
            model_dict["app_label"], model_dict["object_name"].lower()
        )
    return "link:{}".format(model_dict["admin_url"])


def _collect_group_models(
    group: "AppGroup",
    model_dicts: dict[str, dict[str, Any]],
    added: list[str],
    request: HttpRequest,
) -> tuple[list[dict[str, Any]], bool]:
    """Return (models_list, is_active) for a single AppGroup's models and applinks."""
    models = []
    active = False
    for ct in group.models.all():
        key = "{}.{}".format(ct.app_label, ct.model)
        o = model_dicts.get(key)
        if o:
            models.append(o)
            added.append(key)
            if o["active"]:
                active = True
    for app_link in group.applink_set.all():
        link_active = request.path.startswith(app_link.link)
        models.append(
            {
                "name": app_link.localized_name or app_link.name,
                "app_label": group.slug,
                "admin_url": app_link.link,
                "active": link_active,
                "view_only": True,
            }
        )
        if link_active:
            active = True
    return models, active


def _build_tree(
    groups: list["AppGroup"],
) -> tuple[list["AppGroup"], dict[int, list["AppGroup"]]]:
    """
    Split groups into top-level groups and a mapping of parent pk to child groups.

    Groups are validated to be nested at most two levels deep (see
    AppGroup.validate_parent), but data loaded from fixtures or created without
    validation may violate this. Rather than silently dropping such groups, a
    group whose parent is missing (e.g. filtered out of the queryset), itself, or
    nested itself, is treated as a top-level group.
    """
    by_pk = {group.pk: group for group in groups}

    def has_valid_parent(group: "AppGroup") -> bool:
        parent = by_pk.get(group.parent_id)
        return parent is not None and parent.pk != group.pk and parent.parent_id is None

    top_level = []
    children_of = defaultdict(list)
    for group in groups:
        if group.parent_id is None or not has_valid_parent(group):
            top_level.append(group)
        else:
            children_of[group.parent_id].append(group)
    return top_level, children_of


class AppGroupQuerySet(OrderedModelQuerySet):
    def get_by_natural_key(self, slug: str) -> "AppGroup":
        return self.get(slug=slug)

    def as_list(
        self, request: HttpRequest, include_remaining: bool = True
    ) -> list[dict[str, Any]]:
        # Convert to convenient dict
        model_dicts = {}

        original_app_list = site.get_app_list(request)

        for app in original_app_list:
            for model in app["models"]:
                key = "{}.{}".format(
                    app["app_label"], model["object_name"].lower()
                )  # noqa
                model_dict = model.copy()

                # If the user lacks create/read/update permissions, these
                # variables are None in the model_dict
                if model_dict.get("admin_url"):
                    active = request.path.startswith(model_dict["admin_url"])
                elif model_dict.get("add_url"):
                    active = request.path.startswith(model_dict["add_url"])
                else:
                    active = False

                model_dict.update(
                    {
                        "app_label": app["app_label"],
                        "app_name": app["name"],
                        "app_url": app["app_url"],
                        "has_module_perms": app["has_module_perms"],
                        "active": active,
                    }
                )
                model_dicts[key] = model_dict

        added = []

        language_code = get_language()

        # Create new list based on our groups, using the model_dicts constructed above.
        result = []
        # Prefetch with an annotated queryset so the cache key matches the
        # annotated queryset; plain .annotate() calls in _collect_group_models
        # would bypass the cache and cause an extra query per group.
        applink_qs = AppLink.objects.annotate(
            localized_name=F(f"translations__{language_code}")
        )
        groups = list(
            self.annotate(
                localized_name=F(f"translations__{language_code}")
            ).prefetch_related(
                "models",
                Prefetch("applink_set", queryset=applink_qs),
            )
        )
        top_level_groups, children_of = _build_tree(groups)
        active_app = request.path == reverse("admin:index")
        for app in top_level_groups:
            child_groups = children_of[app.pk]
            if child_groups:
                children = []
                child_claimed_keys = set()
                parent_active = False
                for child in child_groups:
                    child_models, child_active = _collect_group_models(
                        child, model_dicts, added, request
                    )
                    if child_models:
                        children.append(
                            {
                                "name": child.localized_name or child.name,
                                "app_label": child.slug,
                                "models": sorted(child_models, key=lambda m: m["name"]),
                                "active": child_active,
                            }
                        )
                        if child_active:
                            parent_active = True
                        child_claimed_keys.update(_model_key(m) for m in child_models)

                # Show parent's own models only if not already shown in a child group.
                parent_models_raw = _collect_group_models(
                    app, model_dicts, added, request
                )[0]
                parent_models = [
                    m
                    for m in parent_models_raw
                    if _model_key(m) not in child_claimed_keys
                ]
                if any(m.get("active") for m in parent_models):
                    parent_active = True

                if parent_models or children:
                    result.append(
                        {
                            "name": app.localized_name or app.name,
                            "app_label": app.slug,
                            "models": sorted(parent_models, key=lambda m: m["name"]),
                            "children": children,
                            "active": parent_active,
                        }
                    )
                    if parent_active:
                        active_app = True

            else:
                models, active = _collect_group_models(app, model_dicts, added, request)
                if models:
                    result.append(
                        {
                            "name": app.localized_name or app.name,
                            "app_label": app.slug,
                            "models": sorted(models, key=lambda m: m["name"]),
                            "active": active,
                        }
                    )
                    if active:
                        active_app = True

        other = [model_dicts[k] for k in model_dicts if k not in added]

        if settings.AUTO_CREATE_APP_GROUP:
            new_apps = False
            for model in other:
                app_group, created = AppGroup.objects.get_or_create(
                    slug=model["app_label"], defaults={"name": model["app_name"]}
                )
                if created:
                    new_apps = True
                    contenttype = ContentTypeProxy.objects.get(
                        app_label=model["app_label"], model=model["object_name"].lower()
                    )
                    app_group.models.add(contenttype)

            # If apps are created, rerender the list.
            if new_apps:
                return self.as_list(request, include_remaining)

        elif other and include_remaining:
            result.append(
                {
                    "name": _("Miscellaneous"),
                    "app_label": "misc",
                    "models": sorted(other, key=lambda m: m["name"]),
                    "active": not active_app,
                }
            )

        return result


class AppLinkQuerySet(OrderedModelQuerySet):
    def get_by_natural_key(self, app_group: "AppGroup", link: str) -> "AppLink":
        return self.get(app_group=app_group, link=link)


class AppGroupManager(OrderedModelManager):
    pass


class AppLinkManager(OrderedModelManager):
    pass


class ContentTypeProxy(ContentType):
    class Meta:
        proxy = True
        ordering = ("app_label", "model")

    def __str__(self):
        return "{}.{}".format(self.app_label, capfirst(self.model))


class AppGroup(TranslationsMixin, OrderedModel):
    name = models.CharField(_("name"), max_length=200)
    slug = models.SlugField(_("slug"), unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        # Only narrows the admin dropdown to top-level groups. The two-level rule
        # itself is enforced by validate_parent() and, for self-parenting, by the
        # check constraint in Meta.
        limit_choices_to={"parent__isnull": True},
        verbose_name=_("parent"),
        help_text=_(
            "Nest this group under another group. Only two levels are supported: "
            "a group with a parent cannot have children of its own."
        ),
    )
    models = models.ManyToManyField(ContentTypeProxy, blank=True)

    objects = AppGroupManager.from_queryset(AppGroupQuerySet)()

    # Top-level groups are ordered among each other, child groups among their siblings.
    order_with_respect_to = "parent"

    class Meta(OrderedModel.Meta):
        verbose_name = _("application group")
        verbose_name_plural = _("application groups")
        constraints = [
            models.CheckConstraint(
                check=~models.Q(parent=models.F("pk")),
                name="admin_index_appgroup_parent_not_self",
            ),
        ]

    def natural_key(self):
        return (self.slug,)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.validate_parent()

    def save(self, *args, **kwargs):
        # The admin form validates through clean(); also guard programmatic use.
        self.validate_parent()
        super().save(*args, **kwargs)

    def validate_parent(self):
        """
        Raise a ValidationError if nesting this group under its parent is invalid.

        Only two levels are supported: a group can have a parent, but not a
        grandparent, and a group with children cannot be nested itself.
        """
        if self.parent_id is None:
            return
        if self.pk is not None and self.parent_id == self.pk:
            raise ValidationError(
                {"parent": _("An application group cannot be its own parent.")}
            )
        if self.parent.parent_id is not None:
            raise ValidationError(
                {
                    "parent": _(
                        "Only two levels of nesting are supported: the selected "
                        "parent is itself nested under another group."
                    )
                }
            )
        if self.pk is not None and self.children.exists():
            raise ValidationError(
                {
                    "parent": _(
                        "This application group has child groups and cannot be "
                        "nested under another group."
                    )
                }
            )


class AppLink(TranslationsMixin, OrderedModel):
    app_group = models.ForeignKey(AppGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    link = models.CharField(max_length=200)

    objects = AppLinkManager.from_queryset(AppLinkQuerySet)()

    class Meta(OrderedModel.Meta):
        verbose_name = _("application link")
        verbose_name_plural = _("application links")
        unique_together = (("app_group", "link"),)

    def natural_key(self):
        return (self.app_group, self.link)

    def __str__(self):
        return self.name
