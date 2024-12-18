from django.contrib.admin import site
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F, Prefetch
from django.urls import reverse
from django.utils.text import capfirst
from django.utils.translation import get_language, gettext_lazy as _

from ordered_model.models import OrderedModel, OrderedModelManager, OrderedModelQuerySet

from .conf import settings
from .translations import TranslationsMixin


class AppGroupQuerySet(OrderedModelQuerySet):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def as_list(self, request, include_remaining=True):
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

        # Create new list based on our groups, using the model_dicts constructed above.  # noqa
        result = []
        app_list = self.annotate(
            localized_name=F(f"translations__{language_code}"),
        ).prefetch_related(
            "models",
            Prefetch(
                "applink_set",
                queryset=AppLink.objects.annotate(
                    localized_name=F(f"translations__{language_code}"),
                ),
            ),
        )
        active_app = request.path == reverse("admin:index")
        for app in app_list:
            models = []
            active = False
            for model in app.models.all():
                key = "{}.{}".format(model.app_label, model.model)
                o = model_dicts.get(key)
                if o:
                    models.append(o)
                    added.append(key)
                    if o["active"]:
                        active = True

            for app_link in app.applink_set.all():
                models.append(
                    {
                        "name": app_link.localized_name or app_link.name,
                        "app_label": app.slug,
                        "admin_url": app_link.link,
                        "active": request.path.startswith(app_link.link),
                        "view_only": True,
                    }
                )
                active = request.path.startswith(app_link.link)

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
    def get_by_natural_key(self, app_group, link):
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
    models = models.ManyToManyField(ContentTypeProxy, blank=True)

    objects = AppGroupManager.from_queryset(AppGroupQuerySet)()

    class Meta(OrderedModel.Meta):
        verbose_name = _("application group")
        verbose_name_plural = _("application groups")

    def natural_key(self):
        return (self.slug,)

    def __str__(self):
        return self.name


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
