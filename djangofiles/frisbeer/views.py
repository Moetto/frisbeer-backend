import itertools
from operator import itemgetter

from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views.generic import FormView
from rest_framework import serializers, viewsets

from frisbeer.models import *


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'elo')
        read_only_fields = ('elo',)


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayersValidator:
    def __call__(self, values):
        players = values.get("players", None)
        if not players or len(players) != 6:
            raise ValidationError("Round requires exactly six players")


class GamePlayerValidator:
    def __call__(self, values):
        team1 = set(values["team1"])
        team2 = set(values["team2"])
        if len(team1) != 3 or len(team2) != 3:
            raise ValidationError("Teams must consist of exactly three players")

        if team1.intersection(team2):
            raise ValidationError("Teams can't contain same players")


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        validators = [
            GamePlayerValidator()
        ]


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


def validate_players(value):
    print("Validating players")
    if len(value) != 6 or len(set(value)) != 6:
        raise ValidationError("Select exactly six different players")


class EqualTeamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['players'] = forms.MultipleChoiceField(
            choices=[(player.id, player.name) for player in list(Player.objects.all())],
            validators=[validate_players])


class TeamCreateView(FormView):
    template_name = "frisbeer/team_select_form.html"
    form_class = EqualTeamForm

    def form_valid(self, form):
        def calculate_team_elo(team):
            return int(sum([player.elo for player in team]) / len(team))

        elo_list = []
        players = set(Player.objects.filter(id__in=form.cleaned_data["players"]))
        possibilities = itertools.combinations(players, 3)
        for possibility in possibilities:
            team1 = possibility
            team2 = players - set(team1)
            elo1 = calculate_team_elo(team1)
            elo2 = calculate_team_elo(team2)
            elo_list.append((abs(elo1 - elo2), team1, team2))
        ideal_teams = sorted(elo_list, key=itemgetter(0))[0]
        teams = {
            "team1": ideal_teams[1],
            "team1_elo": calculate_team_elo(ideal_teams[1]),
            "team2": ideal_teams[2],
            "team2_elo": calculate_team_elo(ideal_teams[2]),
        }

        return render(self.request, 'frisbeer/team_select_form.html', {"form": form, "teams": teams})


from frisbeer import signals
