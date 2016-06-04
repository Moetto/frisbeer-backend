from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from server.settings import ELO_K
from frisbeer.models import *


@receiver(m2m_changed, sender=Game.team2.through)
@receiver(m2m_changed, sender=Game.team1.through)
def update_elo(sender, instance, **kwargs):
    print("Updating elos (mabby)")

    def calculate_elo_change(player, opponent_elo, win):
        if win:
            actual_score = 1
        else:
            actual_score = 0
        Ra = player.elo
        Rb = opponent_elo
        Ea = 1 / (1+10**((Rb-Ra)/400))
        return ELO_K*(actual_score-Ea)

    def calculate_team_elo(team):
        return sum([player.elo for player in team]) / len(team)

    if kwargs["action"] != "post_add":
        return

    if not instance.team1.exists() or not instance.team2.exists():
        return

    games = Game.objects.all().order_by("date")
    Player.objects.all().update(elo=1500)

    for game in games:
        team1 = list(game.team1.all())
        team2 = list(game.team2.all())
        team2_pregame_elo = calculate_team_elo(team2)
        team1_pregame_elo = calculate_team_elo(team1)
        for player in team1:
            player_elo_change = 0
            player_elo_change += game.team1_score * calculate_elo_change(player, team2_pregame_elo, True)
            player_elo_change += game.team2_score * calculate_elo_change(player, team2_pregame_elo, False)
            player.elo += player_elo_change
            player.save()
        for player in team2:
            player_elo_change = 0
            player_elo_change += game.team2_score * calculate_elo_change(player, team1_pregame_elo, True)
            player_elo_change += game.team1_score * calculate_elo_change(player, team1_pregame_elo, False)
            player.elo += player_elo_change
            player.save()
