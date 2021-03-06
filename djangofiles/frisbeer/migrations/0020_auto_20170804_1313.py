# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-04 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frisbeer', '0019_merge_20170607_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='game',
            name='played',
        ),
        migrations.AddField(
            model_name='game',
            name='state',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Ready'), (2, 'Played'), (3, 'Approved')], default=0, help_text="0: pending - the game has been proposed but is still missing players. 1: ready - the game can be played now. Setting this state creates teams. 2: played - the game has been played and results are in. 4: approved - admin has approved the game and it's results are used in calculating ranks."),
        ),
        migrations.AlterField(
            model_name='game',
            name='team1_score',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2)], default=0),
        ),
        migrations.AlterField(
            model_name='game',
            name='team2_score',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2)], default=0),
        ),
    ]
