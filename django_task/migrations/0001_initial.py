# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-25 16:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='id')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('started_on', models.DateTimeField(null=True, verbose_name='started on')),
                ('completed_on', models.DateTimeField(null=True, verbose_name='completed on')),
                ('verbosity', models.IntegerField(blank=True, default=None, null=True, verbose_name='verbosity')),
                ('job_id', models.CharField(blank=True, max_length=128, verbose_name='job id')),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('RECEIVED', 'RECEIVED'), ('STARTED', 'STARTED'), ('PROGESS', 'PROGESS'), ('SUCCESS', 'SUCCESS'), ('FAILURE', 'FAILURE'), ('REVOKED', 'REVOKED'), ('REJECTED', 'REJECTED'), ('RETRY', 'RETRY'), ('IGNORED', 'IGNORED'), ('REJECTED', 'REJECTED')], db_index=True, default='PENDING', max_length=128, verbose_name='status')),
                ('failure_reason', models.CharField(blank=True, max_length=256, verbose_name='failure reason')),
                ('progress', models.IntegerField(blank=True, null=True, verbose_name='progress')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_on',),
                'verbose_name': 'Task',
                'verbose_name_plural': 'All Tasks',
            },
        ),
    ]
