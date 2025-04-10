from .common import *

DEBUG = True

SECRET_KEY = "django-insecure-+auxcbt(50bliklu1u5fsn9#$%_t-2u(z%*8te4fo(rl*jk-&i"

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
