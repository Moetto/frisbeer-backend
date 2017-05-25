import itertools
from operator import itemgetter
from django.utils.timezone import now
from django.db import models


class Player(models.Model):
    elo = models.IntegerField(default=1500)
    score = models.IntegerField(default=0)
    name = models.CharField(max_length=100, unique=True)
    rank = models.CharField(max_length=50, default="", blank=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    players = models.ManyToManyField(Player, related_name='Games', through='GamePlayerRelation')
    date = models.DateTimeField(default=now)
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(max_length=2500, blank=True, null=True)
    location = models.ForeignKey('Location', blank=True, null=True)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    played = models.BooleanField(default=False)

    def __str__(self):
        return "{0} {2} - {3} {1}".format(
            ", ".join(self.players.filter(team=GamePlayerRelation.Team1).values_list("name", flat=True)),
            ", ".join(self.players.filter(team=GamePlayerRelation.Team2).values_list("name", flat=True)),
            self.team1_score,
            self.team2_score,
            )

    def can_score(self):
        return self.approved and self.played and now() > self.date and self.players.count() == 6

    def create_teams(self):
        def calculate_team_elo(team):
            return int(sum([player.elo for player in team]) / len(team))

        elo_list = []
        players = set(self.players.all())
        possibilities = itertools.combinations(players, 3)
        for possibility in possibilities:
            team1 = possibility
            team2 = players - set(team1)
            elo1 = calculate_team_elo(team1)
            elo2 = calculate_team_elo(team2)
            elo_list.append((abs(elo1 - elo2), team1, team2))
        ideal_teams = sorted(elo_list, key=itemgetter(0))[0]
        self.players.filter(id__in=[player.id for player in ideal_teams[1]]).update(team=GamePlayerRelation.Team1)
        self.players.filter(id__in=[player.id for player in ideal_teams[2]]).update(team=GamePlayerRelation.Team2)
        self.save()


class GamePlayerRelation(models.Model):
    Team1 = 1
    Team2 = 2
    Unassigned = 0

    _team_choices = ((0, Unassigned), (1, Team1), (2, Team2))

    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    team = models.IntegerField(choices=_team_choices, default=Unassigned)


class Location(models.Model):
    name = models.CharField(max_length=300, unique=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)

    def __str__(self):
        return self.name
