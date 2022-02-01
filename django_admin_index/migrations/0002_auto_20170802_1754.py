# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_index", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="applink",
            unique_together=set([("app_group", "link")]),
        ),
    ]
