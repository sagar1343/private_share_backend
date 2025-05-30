from datetime import timedelta
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker
from vault.models import Collection, FilePermission, PrivateFile


@pytest.mark.django_db
class TestPrivateFile:
    def test_file_upload_fails_when_size_exceeds_limit(self):
        large_file = SimpleUploadedFile(
            "large_file.txt", b"A" * (6 * 1024 * 1024), content_type="text/plain"
        )
        user = baker.make(get_user_model())
        collection = baker.make(Collection, user=user)

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            "/api/files/",
            {
                "file_name": "test_file",
                "file": large_file,
                "collection": [collection.id],
                "expiration_time": (timezone.now() + timedelta(days=7)),
            },
            format="multipart",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_cannot_upload_file_to_unauthorized_collection(self):
        user = baker.make(get_user_model())
        collection = baker.make(Collection, user=user)
        another_user = baker.make(get_user_model())

        client = APIClient()
        client.force_authenticate(user=another_user)

        small_file = SimpleUploadedFile(
            "restricted_file.txt", b"Restricted access", content_type="text/plain"
        )

        response = client.post(
            "/api/files/",
            {
                "file_name": "test_file",
                "file": small_file,
                "collection": [collection.id],
                "expiration_time": (timezone.now() + timedelta(days=7)),
            },
            format="multipart",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_file_permission_is_created_when_private_file_is_uploaded(self):
        user = baker.make(get_user_model())
        collection1 = baker.make(Collection, user=user)

        test_file = SimpleUploadedFile(
            "test.txt", b"Sample content", content_type="text/plain"
        )
        private_file = PrivateFile.objects.create(
            file_name="test",
            file=test_file,
            expiration_time=timezone.now() + timedelta(days=7),
        )
        private_file.collections.set([collection1])

        assert FilePermission.objects.filter(file=private_file).exists()
