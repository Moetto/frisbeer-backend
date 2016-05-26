from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from server.settings import ELO_K
from frisbeer.models import *


@receiver(m2m_changed, sender=Round.team2.through)
def update_elo(sender, instance, **kwargs):
    def calculate_new_elo(players, opponent_elo, win):
        for player in players:
            if win:
                actual_score = 1
            else:
                actual_score = 0
            Ra = player.elo
            Rb = opponent_elo
            Ea = 1 / (1+10**((Rb-Ra)/400))
            print("{} had an expected score of {}".format(player.name, Ea))
            print(ELO_K*(actual_score-Ea))
            new_elo = int(player.elo + ELO_K*(actual_score-Ea))
            print("Old elo was {} and new elo is {}".format(player.elo, new_elo))
            player.elo = new_elo
            player.save()

    def calculate_team_elo(team):
        # print(team)
        return sum([player.elo for player in team]) / len(team)

    if kwargs["action"] != "post_add":
        return

    if not instance.team1.exists() or not instance.team2.exists():
        return

    team1 = list(instance.team1.all())
    team2 = list(instance.team2.all())
    team2_pregame_elo = calculate_team_elo(team2)
    team1_pregame_elo = calculate_team_elo(team1)
    calculate_new_elo(team1, team2_pregame_elo, instance.winner == Round.TEAM_1_VICTORY)
    calculate_new_elo(team2, team1_pregame_elo, instance.winner == Round.TEAM_2_VICTORY)
