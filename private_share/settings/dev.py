from .common import *

DEBUG = True

SECRET_KEY = os.getenv("DEV_DJANGO_SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DEV_DATABASE_NAME"),
        "HOST": os.getenv("DEV_DATABASE_HOST"),
        "PORT": os.getenv("DEV_DATABASE_PORT"),
        "USER": os.getenv("DEV_DATABASE_USER"),
        "PASSWORD": os.getenv("DEV_DATABASE_PASSWORD"),
    }
}
