# Generated by Django 4.2.16 on 2024-10-09 01:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_title_description_text'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Title',
            new_name='Recipe',
        ),
    ]
