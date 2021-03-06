# Generated by Django 2.1.10 on 2020-05-16 19:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qna', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_url', models.URLField()),
                ('view_count', models.PositiveIntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalog_questions', to='qna.Question')),
            ],
        ),
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_viewed_at', models.DateTimeField()),
                ('view_count', models.IntegerField()),
                ('catalog_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qna.CatalogQuestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='useraskedquestion',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_asked_questions', to='qna.Question'),
        ),
    ]
