# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-11 15:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import frisbeer.models


class Migration(migrations.Migration):

    dependencies = [
        ('frisbeer', '0027_auto_20180424_1833'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='game',
            name='season',
            field=models.ForeignKey(default=frisbeer.models.Season.current, null=True, on_delete=django.db.models.deletion.SET_NULL, to='frisbeer.Season'),
        ),
    ]