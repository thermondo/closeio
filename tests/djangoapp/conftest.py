from django.conf import settings


def pytest_configure():
    settings.configure(
        INSTALLED_APPS=[],
        ROOT_URLCONF='djangoapp.urls',
        STATIC_URL='/static/',
        LANGUAGE_CODE='en',
        SITE_ID=1,
    )
