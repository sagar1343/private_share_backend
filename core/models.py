from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    profile_pic = models.URLField(blank=True, null=True)
    
    USERNAME_FIELD = "email"
    EMAIL_FIELD = []
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
