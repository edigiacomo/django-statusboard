# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 21:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statusboard', '0015_merge_20170222_2058'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='position',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
