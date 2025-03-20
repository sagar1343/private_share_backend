import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from model_bakery import baker

from vault.models import Collection, PrivateFile, FilePermission


@pytest.mark.django_db
class TestFileShare:
    def test_user_can_download_file(self):
        owner = baker.make(get_user_model())
        user = baker.make(get_user_model())
        collection = baker.make(Collection, user=owner)
        test_file = SimpleUploadedFile(
            "test_file.txt", b"Test file", content_type="text/plain"
        )
        private_file = PrivateFile.objects.create(
            file_name="test_file.txt",
            file=test_file,
            password="securepass",
            expiration_time=timezone.now() + timezone.timedelta(days=1),
            max_download_count=3,
        )
        private_file.collections.add(collection)

        file_permission = FilePermission.objects.get(id=private_file.id)
        file_permission.allowed_users.add(user)

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/fileshare/{private_file.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.get("Content-Disposition") is not None

    def test_user_cannot_download_expired_file(self):
        owner = baker.make(get_user_model())
        user = baker.make(get_user_model())
        collection = baker.make(Collection, user=owner)
        test_file = SimpleUploadedFile(
            "test_file.txt", b"Test file content", content_type="text/plain"
        )
        expired_file = PrivateFile.objects.create(
            file_name="expired_file.txt",
            file=test_file,
            password="securepass",
            expiration_time=timezone.now() - timezone.timedelta(days=1),
            max_download_count=3,
        )
        expired_file.collections.add(collection)
        file_permission = FilePermission.objects.get(id=expired_file.id)
        file_permission.allowed_users.add(user)

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/fileshare/{expired_file.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
