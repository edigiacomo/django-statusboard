# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-16 11:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statusboard', '0008_servicegroup_collapse'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicegroup',
            name='position',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
