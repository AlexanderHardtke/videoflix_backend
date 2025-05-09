# Generated by Django 5.2 on 2025-05-04 13:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoflix_db', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofil',
            old_name='preferredSize',
            new_name='preferred_size',
        ),
        migrations.AddField(
            model_name='userprofil',
            name='sound_volume',
            field=models.CharField(default=50, max_length=3),
        ),
        migrations.AddField(
            model_name='video',
            name='file1080p',
            field=models.FileField(blank=True, max_length=99, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='video',
            name='file120p',
            field=models.FileField(blank=True, max_length=99, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='video',
            name='file360p',
            field=models.FileField(blank=True, max_length=99, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='video',
            name='file720p',
            field=models.FileField(blank=True, max_length=99, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='video',
            name='image',
            field=models.FileField(blank=True, max_length=99, null=True, upload_to='images/'),
        ),
        migrations.AddField(
            model_name='video',
            name='name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.CreateModel(
            name='WatchedVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watched_until', models.DurationField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='videoflix_db.video')),
            ],
        ),
    ]
