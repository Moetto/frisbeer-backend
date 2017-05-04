from django.utils.timezone import now
from django.db import models


class Player(models.Model):
    elo = models.IntegerField(default=1500)
    score = models.IntegerField(default=0)
    name = models.CharField(max_length=100, unique=True)
    rank = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.name


class Game(models.Model):
    team1 = models.ManyToManyField(Player, related_name="team1")
    team2 = models.ManyToManyField(Player, related_name="team2")
    date = models.DateTimeField(default=now)
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(max_length=2500, blank=True, null=True)
    location = models.ForeignKey('Location', blank=True, null=True)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)

    def __str__(self):
        return "{0} {2} - {3} {1}".format(", ".join(self.team1.values_list("name", flat=True)),
                                          ", ".join(self.team2.values_list("name", flat=True)),
                                          self.team1_score,
                                          self.team2_score,
                                          )


class Location(models.Model):
    name = models.CharField(max_length=300, unique=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)

    def __str__(self):
        return self.name