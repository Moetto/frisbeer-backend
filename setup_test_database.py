import os
import sys

sys.path.append('djangofiles')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "server.settings")

import django
django.setup()

from frisbeer.models import *
Player.objects.all().delete()
for name in ("jsloth", "T3mu", "Runtu", "ivanhoe_", "lepikko", "Paju"):
    player = Player(name=name)
    player.save()

team1 = Team(captain=Player.objects.get(name="jsloth"), player1=Player.objects.get(name="T3mu"), player2=Player.objects.get(name="Runtu"))
team1.save()
team2 = Team(captain=Player.objects.get(name="ivanhoe_"), player1=Player.objects.get(name="lepikko"), player2=Player.objects.get(name="Paju"))
team2.save()
