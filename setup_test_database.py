import os
import sys
import random

from django.db import IntegrityError

sys.path.append(os.path.join(os.path.dirname(__file__), 'djangofiles'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "server.settings")

import django

django.setup()

from frisbeer.models import *
from django.contrib.auth.models import User

Player.objects.all().delete()
players = set()
for name in (
        "jsloth", "T3mu", "Runtu", "ivanhoe_", "lepikko", "Paju", "Gertrud", "Meea",
        "GamesNate", "zibda", "Jellu", "koops", "Himish"):
    player = Player(name=name)
    player.save()
    players.add(player)

Game.objects.all().delete()
for i in range(10):
    g = Game(name="Testipeli{}".format(i))
    g.save()
    t1 = set(random.sample(players, 3))
    g.team1 = t1
    g.team2 = random.sample(players - t1, 3)
    g.team1_score = random.randint(0, 2)
    g.team2_score = 2 if g.team1_score < 2 else random.randint(0, 1)
    g.approved = random.choice([True, False])
    g.save()

try:
    admin = User.objects.create_superuser(username="admin", password="adminpassu", email="")
    admin.save()
except IntegrityError:
    pass
