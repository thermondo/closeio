from django.conf.urls import patterns, include, url

from closeio.contrib.django import urls

urlpatterns = patterns(
    '',
    url(r'^closeio/hook/', include(urls)),
)
