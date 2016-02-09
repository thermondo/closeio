from django.conf.urls import url

from .views import CloseIOWebHook

urlpatterns = [
    url(r'^$', CloseIOWebHook.as_view(), name='closeio_webhook'),
]
