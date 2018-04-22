import itertools
from operator import itemgetter
from math import exp
from datetime import date

from django.utils.timezone import now
from django.db import models



class Rank(models.Model):
    name = models.CharField(max_length=100, blank=True, unique=True)
    image_url = models.CharField(max_length=1000, blank=True)
    numerical_value = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    elo = models.IntegerField(default=1500)
    score = models.IntegerField(default=0)
    name = models.CharField(max_length=100, unique=True)
    rank = models.ForeignKey(Rank, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Season(models.Model):
    ALGORITHM_2017 = '2017'
    ALGORITHM_2018 = '2018'
    ALGORITHM_CHOICES = (
        (ALGORITHM_2017, '2017'),
        (ALGORITHM_2018, '2018')
    )

    name = models.CharField(max_length=255, unique=True)
    start_date = models.DateField(default=now)
    end_date = models.DateField(null=True, blank=True)
    score_algorithm = models.CharField(max_length=255, choices=ALGORITHM_CHOICES)

    def __str__(self):
        return self.name

    @staticmethod
    def current():
        return Season.objects.filter(start_date__lte=date.today()).order_by('-start_date').first()

    def score(self, *args, **kwargs):
        def score_2017(games_played, rounds_played, rounds_won):
            win_rate = rounds_won / rounds_played if rounds_played != 0 else 0
            return int(win_rate * (1 - exp(-games_played / 4)) * 1000)

        def score_2018(games_played, rounds_played, rounds_won):
            win_rate = rounds_won / rounds_played if rounds_played != 0 else 0
            return int(rounds_won + win_rate * (1 /(1+ exp(3- games_played / 2.5))) * 1000)

        if self.score_algorithm == Season.ALGORITHM_2017:
            return score_2017(*args, **kwargs)
        else:
            return score_2018(*args, **kwargs)


class Game(models.Model):
    PENDING = 0
    READY = 1
    PLAYED = 2
    APPROVED = 3

    game_state_choices = ((PENDING, "Pending"),
                          (READY, "Ready"),
                          (PLAYED, "Played"),
                          (APPROVED, "Approved"))

    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True)

    players = models.ManyToManyField(Player, related_name='games', through='GamePlayerRelation')
    date = models.DateTimeField(default=now)
    name = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField(max_length=2500, blank=True, null=True)
    location = models.ForeignKey('Location', blank=True, null=True)
    team1_score = models.IntegerField(default=0, choices=((0, 0), (1, 1), (2, 2)))
    team2_score = models.IntegerField(default=0, choices=((0, 0), (1, 1), (2, 2)))
    state = models.IntegerField(choices=game_state_choices, default=PENDING,
                                help_text="0: pending - the game has been proposed but is still missing players. "
                                          "1: ready - the game can be played now. Setting this state creates teams. "
                                          "2: played - the game has been played and results are in. "
                                          "4: approved - admin has approved the game and "
                                          "it's results are used in calculating ranks.")

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return "{0} {2} - {3} {1}".format(
            ", ".join(
                self.players.filter(gameplayerrelation__team=GamePlayerRelation.Team1).values_list("name", flat=True)),
            ", ".join(
                self.players.filter(gameplayerrelation__team=GamePlayerRelation.Team2).values_list("name", flat=True)),
            self.team1_score,
            self.team2_score,
        )

    def can_score(self):
        return self.state >= Game.APPROVED

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
        self.gameplayerrelation_set\
            .filter(player__id__in=[player.id for player in ideal_teams[1]]).update(team=GamePlayerRelation.Team1)
        self.gameplayerrelation_set \
            .filter(player__id__in=[player.id for player in ideal_teams[2]]).update(team=GamePlayerRelation.Team2)
        print(ideal_teams[0])
        self.save()


class GamePlayerRelation(models.Model):
    Team1 = 1
    Team2 = 2
    Unassigned = 0

    class Meta:
        unique_together = (("player", "game"),)

    _team_choices = ((0, Unassigned), (1, Team1), (2, Team2))

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    team = models.IntegerField(choices=_team_choices, default=Unassigned)


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)

    def __str__(self):
        return self.name
