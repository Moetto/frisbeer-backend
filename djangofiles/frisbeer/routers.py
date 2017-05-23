from rest_framework import routers
from frisbeer.views import PlayerViewSet, GameViewSet, LocationViewSet, RankViewSet

router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'ranks', RankViewSet)
