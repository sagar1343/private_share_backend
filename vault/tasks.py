from django.utils import timezone
from celery import shared_task
from .models import PrivateFile
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import uuid
from django.db.models import Q


@shared_task
def delete_expired_files():
    """Permanently delete files that have not been recovered within 7 days of expiration."""
    grace_cutoff = timezone.now() - timezone.timedelta(days=7)
    expired_files = PrivateFile.objects.filter(
        expiration_time__lt=grace_cutoff
    ).prefetch_related("collections")

    channel_layer = get_channel_layer()

    for file_instance in expired_files:
        owner = file_instance.collections.first().user
        collection_id = file_instance.collections.first().id
        file_instance.file.delete(save=False)
        file_instance.delete()
        async_to_sync(channel_layer.group_send)(
            f"user-{owner.id}",
            {
                "type": "send_notification",
                "message": {
                    "id": str(uuid.uuid4()),
                    "type": "file_deletion",
                    "title": "File Permanently Deleted",
                    "message": f"{file_instance.file_name} removed permanently due to inactivity.",
                    "read": False,
                    "action_url": f"/collections/{collection_id}/files/{file_instance.id}",
                    "timestamp": str(timezone.now()),
                },
            },
        )

    print(f"Expired ({expired_files.count()}) files deleted successfully.")


@shared_task
def notify_owner_for_expired_files():
    """Check for files that have expired but are still in grace period and send notifications."""
    now = timezone.now()
    grace_cutoff = now - timezone.timedelta(days=7)
    notification_cooldown = now - timezone.timedelta(hours=12)

    files = PrivateFile.objects.filter(
        expiration_time__lt=now,
        expiration_time__gt=grace_cutoff,
    ).filter(
        Q(last_notification_sent__isnull=True) | Q(last_notification_sent__lt=notification_cooldown)
    ).prefetch_related("collections")

    channel_layer = get_channel_layer()

    for file in files:
        owner = file.collections.first().user
        collection_id = file.collections.first().id
        days_left = (grace_cutoff - file.expiration_time).days
        async_to_sync(channel_layer.group_send)(
            f"user-{owner.id}",
            {
                "type": "send_notification",
                "message": {
                    "id": str(uuid.uuid4()),
                    "title": "File Expired",
                    "type": "info",
                    "message": f"Alert: {file.file_name} has expired. You have {days_left} days to restore it before permanent deletion.",
                    "action_url": f"/collections/{collection_id}/files/{file.id}",
                    "read": False,
                    "timestamp": str(timezone.now()),
                },
            },
        )
        file.last_notification_sent = now
        file.save(update_fields=["last_notification_sent"])


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
        ).filter(
            Q(last_notification_sent__isnull=True) | Q(last_notification_sent__lt=notification_cooldown)
        )
        .prefetch_related("collections")
    )
    
    channel_layer = get_channel_layer()
    
    for file in files:
        owner = file.collections.first().user
        collection_id = file.collections.first().id
        async_to_sync(channel_layer.group_send)(
            f"user-{owner.id}",
            {
                "type": "send_notification",
                "message": {
                    "id": str(uuid.uuid4()),
                    "title": "File Expired",
                    "message": f"Warning: {file.file_name} will expire in 24 hours. Please restore it to prevent deletion.",
                    "type": "warning",
                    "read": False,
                    "action_url": f"/collections/{collection_id}/files/{file.id}",
                    "timestamp": str(timezone.now()),
                },
            },
        )
        file.last_notification_sent = now
        file.save(update_fields=["last_notification_sent"])
    
