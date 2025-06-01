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

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    }
}
