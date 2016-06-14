from collections import OrderedDict

from django.db.models import F
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from server.settings import ELO_K
from frisbeer.models import *

from scipy.stats import norm, zscore

ranks = ["Klipsu I", "Klipsu II", "Klipsu III", "Klipsu IV", "Klipsu Mestari", "Klipsu Eliitti Mestari",
         "Kultapossu I", "Kultapossu II", "Kultapossu III", "Kultapossu Mestari", "Mestari Heittäjä I",
         "Mestari Heittäjä II", "Mestari Heittäjä Eliitti", "Arvostettu Jallu Mestari", "Legendaarinen Nalle",
         "Legendaarinen Nalle Mestari", "Korkein Ykkösluokan Mestari", "Urheileva Alkoholisti"]

rank_distribution = OrderedDict()
step = 1 / len(ranks)
for i in range(18):
    rank_distribution[norm.ppf(step * i)] = ranks[i]


@receiver(m2m_changed, sender=Game.team2.through)
@receiver(m2m_changed, sender=Game.team1.through)
@receiver(post_save, sender=Game)
def update_statistics(sender, instance, **kwargs):
    update_elo(instance)
    calculate_ranks()


def update_elo(instance):
    print("Updating elos (mabby)")

    def calculate_elo_change(player, opponent_elo, win):
        if win:
            actual_score = 1
        else:
            actual_score = 0
        Ra = player.elo
        Rb = opponent_elo
        Ea = 1 / (1 + 10 ** ((Rb - Ra) / 400))
        return ELO_K * (actual_score - Ea)

    def calculate_team_elo(team):
        return sum([player.elo for player in team]) / len(team)

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


def calculate_ranks():
    all_players = Player.objects.all()
    players = []
    for player in all_players:
        if player.team1.filter(team1_score=2).count() \
                + player.team2.filter(team2_score=2).count() >= 3:
            players.append(player)

    scores = [player.elo for player in players]
    z_scores = zscore(scores)

    for i in range(len(players)):
        player_z_score = z_scores[i]
        for required_z_score in rank_distribution.keys():
            if player_z_score > required_z_score:
                players[i].rank = rank_distribution[required_z_score]
            else:
                break
    for player in players:
        player.save()
