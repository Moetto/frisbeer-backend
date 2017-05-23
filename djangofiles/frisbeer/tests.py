from os import path
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import Signal
from django.test import TestCase

# Create your tests here.
from frisbeer.models import Player, Game
from frisbeer.signals import calculate_ranks, update_elo

from frisbeer.signals import create_auth_token, update_statistics

post_save.disconnect(update_statistics)
m2m_changed.disconnect(update_statistics)


class RankingTestCase(TestCase):
    fixtures = [path.join(path.dirname(path.abspath(__file__)), 'testdata.json')]

    def test_calculate_ranks(self):
        update_elo()
        # calculate_ranks(Game.objects.all()[0])
        self.assertEqual(4, Player.objects.filter(rank="").count())
        self.assertEqual(2, Player.objects.filter(rank__regex=".+").count())
        for player in Player.objects.all():
            print("{} - {}".format(player.name, player.rank))
