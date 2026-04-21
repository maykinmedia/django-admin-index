import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admin_index", "0006_auto_20230503_1910"),
    ]

    operations = [
        migrations.AddField(
            model_name="appgroup",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                help_text="Nest this group under another group. Only two levels are supported: a group with a parent cannot have children of its own.",
                limit_choices_to={"parent__isnull": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="admin_index.appgroup",
                verbose_name="parent",
            ),
        ),
        migrations.AddConstraint(
            model_name="appgroup",
            constraint=models.CheckConstraint(
                check=models.Q(("parent", models.F("pk")), _negated=True),
                name="admin_index_appgroup_parent_not_self",
            ),
        ),
    ]
