from __future__ import unicode_literals
from django.utils.timezone import now
from django.db import models


class Player(models.Model):
    elo = models.IntegerField(default=1500)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Team(models.Model):
    captain = models.ForeignKey(Player, related_name='captain')
    player1 = models.ForeignKey(Player, related_name='player1')
    player2 = models.ForeignKey(Player, related_name='player2')

    def __str__(self):
        return "{} - {} - {}".format(self.captain.name, self.player1.name, self.player2.name)


class Round(models.Model):
    team1 = models.ForeignKey(Team, related_name='team1')
    team2 = models.ForeignKey(Team, related_name='team2')
    winner = models.ForeignKey(Team, related_name='winning_team')
    date = models.DateTimeField(default=now)

    def __str__(self):
        return "{} - {}".format(self.team1, self.team2)
