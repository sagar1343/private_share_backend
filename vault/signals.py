from django.db.models.signals import post_save
from django.dispatch import receiver

from vault.models import PrivateFile, FilePermission


@receiver(post_save, sender=PrivateFile)
def create_file_permission(sender, **kwargs):
    if kwargs['created']:
        FilePermission.objects.create(file=kwargs['instance'])
