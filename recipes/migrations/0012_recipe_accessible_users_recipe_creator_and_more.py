# Generated by Django 5.1.1 on 2024-11-01 20:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0011_alter_recipefile_file"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="accessible_users",
            field=models.ManyToManyField(
                blank=True,
                related_name="accessible_recipes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="pub_date",
            field=models.DateField(verbose_name="date published"),
        ),
    ]
