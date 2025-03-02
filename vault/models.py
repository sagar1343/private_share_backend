from django.contrib.auth import get_user_model
from django.db import models


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
    file = models.FileField(upload_to="private_files")
    max_download_count = models.PositiveSmallIntegerField(default=3)
    download_count = models.PositiveSmallIntegerField(default=0)
    expiration_time = models.DateTimeField()
    collections = models.ManyToManyField(Collection)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name


class FilePermission(models.Model):
    file = models.ForeignKey(PrivateFile, on_delete=models.CASCADE)
    viewers = models.ManyToManyField(get_user_model(), blank=True, related_name="viewable_files")
    downloaders = models.ManyToManyField(get_user_model(), blank=True, related_name="downloadable_files")

    def __str__(self):
        return f"{self.file} permissions"


class AccessLog(models.Model):
    private_file = models.ForeignKey(PrivateFile, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)
    access_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.__str__()} accessed {self.private_file.file_name} @ {self.access_time}"
