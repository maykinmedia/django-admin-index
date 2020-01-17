from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from .models import AppGroup, AppLink


class AppLinkInline(admin.TabularInline):
    model = AppLink
    fields = (
        "name",
        "link",
    )
    fk_name = "app_group"
    extra = 0


@admin.register(AppGroup)
class AppGroupAdmin(OrderedModelAdmin):
    list_display = (
        "name",
        "move_up_down_links",
    )
    fields = (
        "name",
        "slug",
        "models",
    )
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("models",)
    inlines = (AppLinkInline,)
