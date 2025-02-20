from django.conf import settings
from django.db import models


# Create your models here.
class Collection(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PrivateFile(models.Model):
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="private_files")
    max_download_count = models.PositiveSmallIntegerField(default=3)
    download_count = models.PositiveSmallIntegerField(default=0)
    expiration_time = models.DateTimeField()
    collection = models.ManyToManyField(Collection)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name


class Recipient(models.Model):
    VIEW = "VIEW"
    DOWNLOAD = "DOWNLOAD"
    PERMISSION_CHOICES = {
        VIEW: "view",
        DOWNLOAD: "download",
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    permission_type = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default=PERMISSION_CHOICES[VIEW])
    private_file = models.ForeignKey(PrivateFile, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.__str__()


class AccessLog(models.Model):
    private_file = models.ForeignKey(PrivateFile, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    access_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.__str__()} accessed {self.private_file.file_name} @ {self.access_time}"
