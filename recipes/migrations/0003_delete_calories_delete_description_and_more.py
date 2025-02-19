# Generated by Django 4.2.16 on 2024-10-09 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_calories_description_rename_question_title_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Calories',
        ),
        migrations.DeleteModel(
            name='Description',
        ),
        migrations.AddField(
            model_name='title',
            name='calories_text',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='title',
            name='description_text',
            field=models.CharField(default='none', max_length=200),
            preserve_default=False,
        ),
    ]
