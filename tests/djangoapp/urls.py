from django.conf.urls import include, patterns, url

from closeio.contrib.django import urls

urlpatterns = patterns(
    '',
    url(r'^closeio/hook/', include(urls)),
)
