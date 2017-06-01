from rest_framework import routers
from frisbeer.views import *

router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet)
#router.register(r'games2', PlayerInGameViewSet)
router.register(r'locations', LocationViewSet)
