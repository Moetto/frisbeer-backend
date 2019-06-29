from rest_framework import routers
from frisbeer.views import *

router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'games', GameViewSet, 'games')
router.register(r'locations', LocationViewSet)
router.register(r'ranks', RankViewSet)
router.register(r'teams', TeamViewSet)
