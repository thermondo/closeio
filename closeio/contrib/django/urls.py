from django.conf.urls import patterns, url

from .views import CloseIOWebHook

urlpatterns = patterns(
    '',
    url(r'^$', CloseIOWebHook.as_view(), name='closeio_webhook'),
)
