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
            expiration_time=timezone.now() + timezone.timedelta(days=1),
            max_download_count=3,
        )
        private_file.collections.add(collection)

        file_permission = FilePermission.objects.get(file=private_file)
        file_permission.allowed_users = [user.email]
        file_permission.save()

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/fileshare/{private_file.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data is not None

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
            expiration_time=timezone.now() - timezone.timedelta(days=1),
            max_download_count=3,
        )
        expired_file.collections.add(collection)
        file_permission = FilePermission.objects.get(file=expired_file)
        file_permission.allowed_users = [user.email]
        file_permission.save()

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/fileshare/{expired_file.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["message"] == "This file has expired"

    def test_user_cannot_download_file_without_permission(self):
        owner = baker.make(get_user_model())
        user = baker.make(get_user_model())
        collection = baker.make(Collection, user=owner)
        test_file = SimpleUploadedFile(
            "test_file.txt", b"Test file content", content_type="text/plain"
        )
        file = PrivateFile.objects.create(
            file_name="test_file.txt",
            file=test_file,
            expiration_time=timezone.now() + timezone.timedelta(days=1),
            max_download_count=3,
        )
        file.collections.add(collection)
        file_permission, _ = FilePermission.objects.get_or_create(file=file)
        file_permission.allowed_users = []
        file_permission.save()

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/fileshare/{file.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_cannot_download_file_after_max_downloads(self):
        owner = baker.make(get_user_model())
        user = baker.make(get_user_model())
        collection = baker.make(Collection, user=owner)
        test_file = SimpleUploadedFile(
            "test_file.txt", b"Test file content", content_type="text/plain"
        )
        file = PrivateFile.objects.create(
            file_name="test_file.txt",
            file=test_file,
            expiration_time=timezone.now() + timezone.timedelta(days=1),
            max_download_count=1,
            download_count=1,
        )
        file.collections.add(collection)
        file_permission = FilePermission.objects.get(file=file)
        file_permission.allowed_users = [user.email]
        file_permission.save()

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/fileshare/{file.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["message"] == "Download limit has been reached."
