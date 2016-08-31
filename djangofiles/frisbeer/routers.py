from rest_framework import routers
from frisbeer.views import PlayerViewSet, GameViewSet, LocationViewSet

router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
router.register(r'locations', LocationViewSet)
