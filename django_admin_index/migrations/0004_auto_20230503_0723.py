# Generated by Django 3.2.18 on 2023-05-03 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_index', '0003_auto_20200724_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appgroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='applink',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
