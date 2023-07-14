# Generated by Django 3.2.18 on 2023-05-03 17:10

from django.db import migrations, models

import django_admin_index.translations


class Migration(migrations.Migration):
    dependencies = [
        ("admin_index", "0004_auto_20230503_0723"),
    ]

    operations = [
        migrations.AddField(
            model_name="appgroup",
            name="translations",
            field=models.JSONField(
                default=dict,
                help_text='A JSON-object that uses the Django language code as key and the localized name as value. If no translation can be found for the active language, the name is used as fallback. Example: {"en": "File", "nl": "Bestand"}',
                validators=[
                    django_admin_index.translations.validate_translation_json_format
                ],
                verbose_name="translations",
            ),
        ),
        migrations.AddField(
            model_name="applink",
            name="translations",
            field=models.JSONField(
                default=dict,
                help_text='A JSON-object that uses the Django language code as key and the localized name as value. If no translation can be found for the active language, the name is used as fallback. Example: {"en": "File", "nl": "Bestand"}',
                validators=[
                    django_admin_index.translations.validate_translation_json_format
                ],
                verbose_name="translations",
            ),
        ),
    ]