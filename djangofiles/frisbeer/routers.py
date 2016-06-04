from rest_framework import routers
from frisbeer.views import PlayerViewSet, GameViewSet

router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
