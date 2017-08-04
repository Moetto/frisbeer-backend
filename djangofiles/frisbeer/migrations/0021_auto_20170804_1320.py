# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-04 13:20
from __future__ import unicode_literals

from django.db import migrations


def set_approved(apps, schema_editor):
    Game = apps.get_model('frisbeer', 'Game')
    Game.objects.update(state=3)


class Migration(migrations.Migration):

    dependencies = [
        ('frisbeer', '0020_auto_20170804_1313'),
    ]

    operations = [
        migrations.RunPython(set_approved),
    ]
