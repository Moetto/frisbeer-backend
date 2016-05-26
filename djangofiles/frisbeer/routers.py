from rest_framework import routers
from frisbeer.views import PlayerViewSet, RoundViewSet

router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'rounds', RoundViewSet)
