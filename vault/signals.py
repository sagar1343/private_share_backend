from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from vault.models import PrivateFile, FilePermission


@receiver(m2m_changed, sender=PrivateFile.collections.through)
def create_file_permission_on_collection_change(sender, instance, action, **kwargs):
    if action == "post_add":
        permission, created = FilePermission.objects.get_or_create(file=instance)

        for collection in instance.collections.all():
            if collection.user:
                permission.allowed_users.add(collection.user)
