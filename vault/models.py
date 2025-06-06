from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.
class Collection(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PrivateFile(models.Model):
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="private_files/")
    password = models.CharField(max_length=255, null=True, blank=True)
    max_download_count = models.PositiveSmallIntegerField(default=3, validators=[MinValueValidator(limit_value=1)])
    download_count = models.PositiveSmallIntegerField(default=0)
    expiration_time = models.DateTimeField(null=True, blank=True)
    last_notification_sent = models.DateTimeField(null=True, blank=True)
    collections = models.ManyToManyField(Collection)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def is_protected(self):
        return bool(self.password)

    def check_file_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.file_name


class FilePermission(models.Model):
    file = models.ForeignKey(PrivateFile, on_delete=models.CASCADE, related_name="file_permissions")
    allowed_users = models.JSONField(default=list)

    def __str__(self):
        return f"{self.file} permissions"
    
    def has_access(self, email):
        return email in self.allowed_users


class AccessLog(models.Model):
    private_file = models.ForeignKey(PrivateFile, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    access_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.__str__()} accessed {self.private_file.file_name} @ {self.access_time}"
