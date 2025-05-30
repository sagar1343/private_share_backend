from django.utils import timezone
from celery import shared_task
from .models import PrivateFile
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import F


@shared_task
def delete_expired_files():
    """Permanently delete files that have not been recovered within 7 days of expiration."""
    grace_cutoff = timezone.now() - timezone.timedelta(days=7)
    expired_files = (
        PrivateFile.objects.filter(expiration_time__lt=grace_cutoff)
        .prefetch_related("collections")
    )

    channel_layer = get_channel_layer()

    for file_instance in expired_files:
        owner = file_instance.collections.first().user
        file_instance.file.delete(save=False)
        file_instance.delete()
        async_to_sync(channel_layer.group_send)(
            f"user-{owner.id}",
            {
                "type": "send_notification",
                "message": f"{file_instance.file_name} removed permanently due to inactivity.",
            },
        )

    print(f"Expired ({expired_files.count()}) files deleted successfully.")


@shared_task
def notify_owner_for_expired_files():
    """Check for files that have expired but are still in grace period and send notifications."""
    now = timezone.now()
    grace_cutoff = now - timezone.timedelta(days=7)
    notification_cooldown = now - timezone.timedelta(hours=12) 

    files = (
        PrivateFile.objects.filter(
            expiration_time__lt=now,
            expiration_time__gt=grace_cutoff,
            last_notification_sent__lt=notification_cooldown
        )
        .prefetch_related("collections")
    )
    
    channel_layer = get_channel_layer()
    for file in files:
        owner = file.collections.first().user
        days_left = (grace_cutoff - file.expiration_time).days
        async_to_sync(channel_layer.group_send)(
            f"user-{owner.id}",
            {
                "type": "send_notification",
                "message": f"Alert: {file.file_name} has expired. You have {days_left} days to restore it before permanent deletion.",
            },
        )
        file.last_notification_sent = now
        file.save(update_fields=['last_notification_sent'])


@shared_task
def notify_owner_before_files_expiration():
    """Check for files that are about to expire (within 24 hours) and send warnings."""
    now = timezone.now()
    warning_threshold = now + timezone.timedelta(hours=24)
    notification_cooldown = now - timezone.timedelta(hours=4)

    files = (
        PrivateFile.objects.filter(
            expiration_time__gt=now,
            expiration_time__lte=warning_threshold,
            last_notification_sent__lt=notification_cooldown
        )
        .prefetch_related("collections")
    )
    
    channel_layer = get_channel_layer()
    for file in files:
        owner = file.collections.first().user
        async_to_sync(channel_layer.group_send)(
            f"user-{owner.id}",
            {
                "type": "send_notification",
                "message": f"Warning: {file.file_name} will expire in 24 hours. Please restore it to prevent deletion.",
            },
        )
        file.last_notification_sent = now
        file.save(update_fields=['last_notification_sent'])
