# Generated by Django 4.2.16 on 2024-10-09 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_delete_calories_delete_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='description_text',
            field=models.CharField(default='No description', max_length=200),
        ),
    ]
