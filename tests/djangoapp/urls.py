from django.conf.urls import include, url

urlpatterns = [
    url(r'^closeio/hook/', include('closeio.contrib.django.urls')),
]
