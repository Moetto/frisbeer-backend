import logging

from django import forms
from django.shortcuts import render
from django.views.generic import FormView, ListView
from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet

from frisbeer.models import *
from frisbeer.serializers import RankSerializer, PlayerSerializer, PlayerInGameSerializer, GameSerializer, \
    LocationSerializer


class RankViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Rank.objects.all()
    serializer_class = RankSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerInGameViewSet(viewsets.ModelViewSet):
    queryset = GamePlayerRelation.objects.all()
    serializer_class = PlayerInGameSerializer


class GameViewSet(viewsets.ModelViewSet):
    """
    Game
    list:
    Get all games

    create:
    Start a new pending game. Continue updating game with PATCH
    """
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


def validate_players(value):
    logging.debug("Validating players")
    if len(value) != 6 or len(set(value)) != 6:
        raise ValidationError("Select exactly six different players")


class EqualTeamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['players'] = forms.MultipleChoiceField(
            choices=[(player.id, player.name) for player in list(Player.objects.all())],
            validators=[validate_players],
            widget=forms.CheckboxSelectMultiple)


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


class ScoreListView(ListView):
    model = Player
    ordering = ['-score']
