from django.conf.urls import url, include
from rest_framework.authtoken.views import obtain_auth_token

from frisbeer import views
from frisbeer.routers import router

urlpatterns = [
    url(r'^API/token-auth', obtain_auth_token, name="obtain_auth"),
    url(r'^API/', include(router.urls)),
    url(r'teams', views.TeamCreateView.as_view(), name="team_select")
]
