import closeio.urls

from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^closeio/hook/', include(closeio.urls)),
)
