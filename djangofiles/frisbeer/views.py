import itertools
from operator import itemgetter

from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views.generic import FormView, ListView
from rest_framework import serializers, viewsets

from frisbeer.models import *


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('id', 'name', 'rank', 'score')
        read_only_fields = ('score', 'rank')


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayersValidator:
    def __call__(self, values):
        players = values.get("players", None)
        if not players or len(players) != 6:
            raise ValidationError("Round requires exactly six players")


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game

    def validate(self, attrs):
        su = super().validate(attrs)

        team1 = su.get("team1")
        if team1 is None:
            try:
                team1 = self.instance.team1.all()
            except AttributeError:
                raise ValidationError("Both teams are required. Team 1 is missing")
        team1 = set(team1)

        team2 = su.get("team2")
        if team2 is None:
            try:
                team2 = self.instance.team2.all()
            except AttributeError:
                raise ValidationError("Both teams are required. Team 2 is missing")
        team2 = set(team2)

        if len(team1) != 3 or len(team2) != 3:
            raise ValidationError("Teams must consist of exactly three players")

        if team1.intersection(team2):
            raise ValidationError("Teams can't contain same players")
        return su


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location

    def validate(self, attrs):
        su = super().validate(attrs)
        try:
            longitude = su.get("longitude", self.instance.longitude)
        except AttributeError:
            longitude = None

        try:
            latitude = su.get("latitude", self.instance.latitude)
        except AttributeError:
            latitude = None

        if latitude is not None and (latitude > 90 or latitude < -90):
            raise ValidationError("Latitude must be between -90 and 90")
        if longitude is not None and (longitude > 180 or longitude < -180):
            raise ValidationError("Longitude must be between -180 and 180")
        if (longitude is None and latitude is not None) or (longitude is not None and latitude is None):
            raise ValidationError("If longitude is provided then latitude is required and vice versa. Both can be null.")

        return su


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


def validate_players(value):
    print("Validating players")
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


from frisbeer import signals
