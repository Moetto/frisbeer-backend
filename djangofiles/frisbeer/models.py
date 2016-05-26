from django.utils.timezone import now
from django.db import models


class Player(models.Model):
    elo = models.IntegerField(default=1500)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PlayerRoundRelation(models.Model):
    player = models.ForeignKey(Player)
    round = models.ForeignKey("Round")
    captain = models.BooleanField(default=False)
    team = models.IntegerField(choices=((1, "Team 1",), (2, "Team 2",)))


class Round(models.Model):
    TEAM_1_VICTORY = 1
    TEAM_2_VICTORY = 2
    team1 = models.ManyToManyField(Player, related_name="team1")
    team2 = models.ManyToManyField(Player, related_name="team2")
    winner = models.IntegerField(choices=((TEAM_1_VICTORY, "Team 1",), (TEAM_2_VICTORY, "Team 2",)))
    date = models.DateTimeField(default=now)

    def __str__(self):
        return "{} - {}".format(", ".join(self.team1.values_list("name", flat=True)), ", ".join(self.team2.values_list("name", flat=True)))
