from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    profile_pic = models.URLField(blank=True, null=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = []
    REQUIRED_FIELDS = []
