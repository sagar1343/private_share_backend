from django.utils import timezone
from celery import shared_task
from .models import PrivateFile


@shared_task
def delete_expired_files():
    grace_cutoff = timezone.now() - timezone.timedelta(days=7)
    expired_files = PrivateFile.objects.filter(expiration_time__lt=grace_cutoff)

    for file_instance in expired_files:
        file_instance.file.delete(save=False)
        file_instance.delete()

    print("Expired files deleted successfully.")
