# Generated by Django 2.1.10 on 2020-05-16 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qna', '0003_auto_20200516_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogquestion',
            name='view_count',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='useractivity',
            name='view_count',
            field=models.IntegerField(default=0),
        ),
    ]
