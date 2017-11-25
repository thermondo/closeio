import django
from django.conf import settings


def pytest_configure():
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        ROOT_URLCONF='djangoapp.urls',
        STATIC_URL='/static/',
        LANGUAGE_CODE='en',
        SITE_ID=1,
        MIDDLEWARE=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),
    )
    django.setup()
