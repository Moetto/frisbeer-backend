# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-23 19:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frisbeer', '0014_auto_20170523_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='rank',
            name='numerical_value',
            field=models.IntegerField(default=0, unique=True),
            preserve_default=False,
        ),
    ]
