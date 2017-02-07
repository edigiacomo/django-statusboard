# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-25 06:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('statusboard', '0002_incident'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncidentUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('status', models.IntegerField(choices=[(0, 'Investigating'), (1, 'Identified'), (2, 'Watching'), (3, 'Fixed')])),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='incident',
            name='description',
        ),
        migrations.RemoveField(
            model_name='incident',
            name='occurred',
        ),
        migrations.RemoveField(
            model_name='incident',
            name='status',
        ),
        migrations.AddField(
            model_name='incidentupdate',
            name='incident',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', related_query_name='update', to='statusboard.Incident'),
        ),
    ]
