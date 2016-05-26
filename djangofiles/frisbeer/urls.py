from django.conf.urls import url, include

from frisbeer.routers import router

urlpatterns = [
    url('^API/', include(router.urls)),
]
