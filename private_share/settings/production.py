from .common import *

DEBUG = False

SECRET_KEY = "django-insecure-+auxcbt(50bliklu1u5fsn9#$%_t-2u(z%*8te4fo(rl*jk-&i"

ALLOWED_HOSTS = ["http://localhost:8000"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DATABASE_NAME"),
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
    }
}
