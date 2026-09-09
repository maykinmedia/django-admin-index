from django.contrib import admin
from django.db.models import F
from django.db.models.functions import Coalesce

from ordered_model.admin import OrderedModelAdmin

from .models import AppGroup, AppLink


class AppLinkInline(admin.TabularInline):
    model = AppLink
    fields = (
        "name",
        "translations",
        "link",
    )
    fk_name = "app_group"
    extra = 0


@admin.register(AppGroup)
class AppGroupAdmin(OrderedModelAdmin):
    list_display = (
        "name",
        "parent",
        "move_up_down_links",
    )
    fields = (
        "parent",
        "name",
        "translations",
        "slug",
        "models",
    )
    list_filter = ("parent",)
    # Group order is relative to the parent, so keep child groups directly under
    # their parent in the flat changelist: sort by the parent's order (or the own
    # order for top-level groups), then parent before children, then siblings.
    ordering = (
        Coalesce("parent__order", "order"),
        F("parent").asc(nulls_first=True),
        "order",
    )
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("models",)
    inlines = (AppLinkInline,)
