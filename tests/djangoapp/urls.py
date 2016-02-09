from django.conf.urls import include, url

from closeio.contrib.django import urls

urlpatterns = [
    url(r'^closeio/hook/', include(urls)),
]
