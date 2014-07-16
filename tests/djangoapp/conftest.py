from django.conf import settings


def pytest_configure():
    settings.configure(
        INSTALLED_APPS=[],
        ROOT_URLCONF='djangoapp.urls',
        STATIC_URL='/static/',
        LANGUAGE_CODE='en',
        SITE_ID=1,
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ),
    )
