# Generated by Django 3.2.18 on 2023-05-03 17:10

from django.conf import settings
from django.db import migrations


def copy_fallback_name_to_translations(apps, _):
    AppGroup = apps.get_model("admin_index", "AppGroup")
    AppLink = apps.get_model("admin_index", "AppLink")

    if not settings.LANGUAGE_CODE:
        return

    for app_group in AppGroup.objects.all():
        app_group.translations = {settings.LANGUAGE_CODE: app_group.name}
        app_group.save()

    for app_link in AppLink.objects.all():
        app_link.translations = {settings.LANGUAGE_CODE: app_link.name}
        app_link.save()


class Migration(migrations.Migration):
    dependencies = [
        ("admin_index", "0005_auto_20230503_1910"),
    ]

    operations = [
        migrations.RunPython(
            copy_fallback_name_to_translations, migrations.RunPython.noop
        ),
    ]
