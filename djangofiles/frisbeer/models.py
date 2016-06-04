from django.utils.timezone import now
from django.db import models


class Player(models.Model):
    elo = models.IntegerField(default=1500)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Game(models.Model):
    team1 = models.ManyToManyField(Player, related_name="team1")
    team2 = models.ManyToManyField(Player, related_name="team2")
    date = models.DateTimeField(default=now)
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(max_length=2500, blank=True, null=True)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)

    def __str__(self):
        return "{} - {}".format(", ".join(self.team1.values_list("name", flat=True)), ", ".join(self.team2.values_list("name", flat=True)))
