from django.db.models.signals import post_save
from django.dispatch import receiver

from server.settings import ELO_K
from frisbeer.models import *


@receiver(post_save, sender=Round)
def update_elo(sender, instance, **kwargs):
    def calculate_new_elo(team, opponent_elo, win):
        for player in [team.captain, team.player1, team.player2]:
            if win:
                actual_score = 1
            else:
                actual_score = 0
            Ra = player.elo
            Rb = opponent_elo
            Ea = 1 / (1+10**((Rb-Ra)/400))
            print("{} had an expected score of {}".format(player.name, Ea))
            new_elo = int(player.elo + ELO_K*(actual_score-Ea))
            print("Old elo was {} and new elo is {}".format(player.elo, new_elo))
            player.elo = new_elo
            player.save()

    def calculate_team_elo(team):
        return sum([team.captain.elo, team.player1.elo, team.player2.elo]) / 3

    team2_pregame_elo = calculate_team_elo(instance.team2)
    team1_pregame_elo = calculate_team_elo(instance.team1)
    calculate_new_elo(instance.team1, team2_pregame_elo, instance.winner == instance.team1)
    calculate_new_elo(instance.team2, team1_pregame_elo, instance.winner == instance.team2)
