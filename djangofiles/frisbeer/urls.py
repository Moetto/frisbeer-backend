from django.conf.urls import url, include

from frisbeer import views
from frisbeer.routers import router

urlpatterns = [
    url('^API/', include(router.urls)),
    url('teams', views.TeamCreateView.as_view(), name="team_select")
]
