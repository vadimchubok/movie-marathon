from .base import *


SECRET_KEY = os.environ.get("DJANGO-SECRET-KEY", "django-insecure-3arref*e3qso0dc$kt%@a3uzna8r&rwwxs7f0pvgz-6ca#6*c$")
ALLOWED_HOSTS = ["127.0.0.1"]
DEBUG = os.environ.get("DJANGO_DEBUG", "") != "False"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
