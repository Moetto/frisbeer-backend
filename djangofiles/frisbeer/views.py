import logging

from django import forms
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView
from rest_framework import viewsets, mixins
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError, APIException, PermissionDenied
from rest_framework.viewsets import GenericViewSet

from frisbeer.models import *
from frisbeer.serializers import RankSerializer, PlayerSerializer, PlayerInGameSerializer, GameSerializer, \
    LocationSerializer, TeamSerializer


class RankViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Rank.objects.all()
    serializer_class = RankSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerInGameViewSet(viewsets.ModelViewSet):
    queryset = GamePlayerRelation.objects.all()
    serializer_class = PlayerInGameSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


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

    @detail_route(methods=['post'])
    def add_player(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        body = request.data
        player_id = body.get("id", None)
        if player_id is None:
            return HttpResponseBadRequest("Set player in body with key id")
        player = get_object_or_404(Player, pk=body["id"])
        with transaction.atomic():
            relation = GamePlayerRelation(game=game, player=player)
            relation.save()
            if GamePlayerRelation.objects.filter(game=game).count() > 6:
                raise APIException(detail="Game is already full", code=400)
        return redirect(reverse("frisbeer:games-detail", args=[pk]))

    @detail_route(methods=['post'])
    def remove_player(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        body = request.data
        player = get_object_or_404(Player, pk=body['id'])
        get_object_or_404(GamePlayerRelation, game=game, player=player).delete()
        return redirect(reverse("frisbeer:games-detail", args=[pk]))

    @detail_route(methods=['post'])
    def create_teams(self, request, pk=None):
        game = get_object_or_404(Game, pk=pk)
        if GamePlayerRelation.objects.filter(game=game).count() != 6:
            raise APIException("Game needs 6 players before teams can be created", code=400)
        force = request.data.get("re_create", False)
        game.create_teams()
        game.state = Game.READY
        game.save()
        print("Created")
        return redirect(reverse("frisbeer:games-detail", args=[pk]))

    def destroy(self, request, *args, **kwargs):
        if request.user and not request.user.is_superuser and self.get_object().players.count() > 0:
            raise PermissionDenied("Only admins can delete games with players in them")
        return super().destroy(request, *args, **kwargs)


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
