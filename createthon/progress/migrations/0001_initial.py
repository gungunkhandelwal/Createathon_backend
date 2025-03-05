# Generated by Django 5.1.6 on 2025-03-05 17:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('challenges', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('points_required', models.IntegerField()),
                ('badge_icon', models.ImageField(blank=True, null=True, upload_to='uploads/achievements/')),
            ],
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earned_at', models.DateTimeField(auto_now_add=True)),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='progress.achievement')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'achievement')},
            },
        ),
        migrations.CreateModel(
            name='UserProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('started', 'Started'), ('submitted', 'Submitted'), ('completed', 'Completed')], default='started', max_length=20)),
                ('attempts', models.IntegerField(default=0)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('submission_code', models.TextField(blank=True)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenges.challenge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'challenge')},
            },
        ),
    ]
