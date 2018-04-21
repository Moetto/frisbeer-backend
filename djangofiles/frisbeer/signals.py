from collections import OrderedDict, defaultdict
from math import exp

import logging
from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from server import settings

from frisbeer.models import *

from scipy.stats import zscore


@receiver(m2m_changed, sender=Game.players.through)
@receiver(m2m_changed, sender=Game.players.through)
@receiver(post_save, sender=Game)
def update_statistics(sender, instance, **kwargs):

    update_elo()
    update_score()

    if not instance or not instance.can_score():
        logging.debug("Game was saved, but hasn't been played yet. Sender %s, instance %s", sender, instance)
        return

    calculate_ranks(instance)


def update_elo():
    """
    Calculate new elos for all players. 
    
    Update is done for all players because matches are possibly added in non-chronological order
    """
    logging.info("Updating elos (mabby)")

    def calculate_elo_change(player, opponent_elo, win):
        if win:
            actual_score = 1
        else:
            actual_score = 0
        Ra = player
        Rb = opponent_elo
        Ea = 1 / (1 + 10 ** ((Rb - Ra) / 400))
        return settings.ELO_K * (actual_score - Ea)

    def calculate_team_elo(team):
        return sum([player.elo for player in team]) / len(team)

    games = Game.objects.filter(state=Game.APPROVED).order_by("date")


    Player.objects.all().update(elo=1500)

    def _elo_decay():
        # Halves the distance from median elo for all players
        Player.objects.all().update(elo=(F('elo')-1500)/2 + 1500)

    season = 2017
    for game in games:
        # Perform elo decay before first game of 2018
        if game.date.year == 2018 and season == 2017:
            _elo_decay()
            season = "2018"
        team1 = [r.player for r in list(game.gameplayerrelation_set.filter(team=1))]
        team2 = [r.player for r in list(game.gameplayerrelation_set.filter(team=2))]
        team2_pregame_elo = calculate_team_elo(team2)
        team1_pregame_elo = calculate_team_elo(team1)
        for player in team1:
            player_elo_change = 0
            player_elo_change += game.team1_score * calculate_elo_change(team1_pregame_elo, team2_pregame_elo, True)
            player_elo_change += game.team2_score * calculate_elo_change(team1_pregame_elo, team2_pregame_elo, False)
            player.elo += player_elo_change
            logging.debug("{0} elo changed {1:0.2f}".format(player.name, player_elo_change))
            player.save()
        for player in team2:
            player_elo_change = 0
            player_elo_change += game.team2_score * calculate_elo_change(team2_pregame_elo, team1_pregame_elo, True)
            player_elo_change += game.team1_score * calculate_elo_change(team2_pregame_elo, team1_pregame_elo, False)
            player.elo += player_elo_change
            logging.debug("{0} elo changed {1:0.2f}".format(player.name, player_elo_change))
            player.save()

    # First game not even played yet -> decay
    if season == 2017:
        _elo_decay()


def update_score():
    logging.info("Updating scores (mabby)")

    season = Season.current()
    games = Game.objects.filter(season_id=season.id, state=Game.APPROVED)

    if not games:
        Player.objects.all().update(score=0)

    players = {}
    for game in games:
        team1 = [r.player for r in game.gameplayerrelation_set.filter(team=1)]
        team2 = [r.player for r in game.gameplayerrelation_set.filter(team=2)]
        for team in [team1, team2]:
            for player in team:
                if not player in players:
                    players[player] = defaultdict(int)
                players[player]['games'] += 1
                players[player]['wins'] += game.team1_score if team is team1 else game.team2_score
                players[player]['rounds'] += game.team1_score + game.team2_score

    for player, data in players.items():
        old_score = player.score
        player.score = season.score(games_played=data['games'],
                     rounds_played=data['rounds'],
                     rounds_won=data['wins'])
        if old_score != player.score:
            logging.debug("{} old score: {}, new score {}".format(player.name, old_score, player.score))
            player.save()


def calculate_ranks(game):
    logging.info("Calculating new ranks")
    players = Player.objects.all()
    ranks = list(Rank.objects.all())

    rank_distribution = OrderedDict()
    step = 6 / (len(ranks) - 2)
    for i in range(len(ranks) - 2):
        rank_distribution[-3 + i * step] = ranks[i]

    player_list = []
    season = Season.current()
    for player in players:
        s1 = player.gameplayerrelation_set.filter(team=1, game__season_id=season.id).aggregate(Sum('game__team1_score'))[
            "game__team1_score__sum"] or 0
        s2 = player.gameplayerrelation_set.filter(team=2, game__season_id=season.id).aggregate(Sum('game__team2_score'))[
            "game__team2_score__sum"] or 0
        s1 = s1 if s1 else 0
        s2 = s2 if s2 else 0
        if s1 + s2 > 4:
            player_list.append(player)

    if not player_list:
        logging.debug("No players with four round victories")
        for player in players:
            player.rank = None
            player.save()
        return

    scores = [player.score for player in player_list]
    if len(set(scores)) == 1:
        logging.debug("Only one player {} with rank".format(player_list[0]))
        z_scores = [0.0 for i in range(len(player_list))]
    else:
        z_scores = zscore(scores)
        logging.debug("Players: {}".format(player_list))
        logging.debug("Z_scores: {}".format(z_scores))


    for i in range(len(player_list)):
        player = player_list[i]
        if player not in list(game.players.all()):
            logging.debug("Not setting rank for %s because he didn't play", player)
            continue
        player_z_score = z_scores[i]
        player = player_list[i]
        rank = None
        for required_z_score in rank_distribution.keys():
            if player_z_score > required_z_score:
                rank = rank_distribution[required_z_score]
            else:
                break
        logging.debug("Setting rank {} for {}".format(rank, player.name))
        player.rank = rank
        player.save()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
