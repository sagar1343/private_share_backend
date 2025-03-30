from django.db.models.signals import post_save
from django.dispatch import receiver
from vault.models import PrivateFile, FilePermission


@receiver(post_save, sender=PrivateFile)
def create_file_permission_on_file_create(sender, instance, created, **kwargs):
    if created:
        FilePermission.objects.get_or_create(file=instance)
        print("File permission created")
