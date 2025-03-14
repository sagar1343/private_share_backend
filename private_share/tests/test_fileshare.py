import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from vault.models import Collection, PrivateFile, FilePermission


@pytest.mark.django_db
class TestFileShare:
    def test_user_can_download_file(self):
        owner = get_user_model().objects.create_user(
            username="owner",
            email="owner@gmail.com",
            password="password"
        )
        user = get_user_model().objects.create_user(
            username="username",
            email="user@gmail.com",
            password="password1"
        )
        collection = Collection.objects.create(title="collection1", user=owner)

        test_file = SimpleUploadedFile(
            "test_file.txt", b"Test file content", content_type="text/plain"
        )

        private_file = PrivateFile.objects.create(
            file_name="test_file.txt",
            file=test_file,
            password="securepass",
            expiration_time=timezone.now() + timezone.timedelta(days=1),
            max_download_count=3
        )
        private_file.collections.add(collection)
        private_file.save()

        file_permission, created = FilePermission.objects.get_or_create(file=private_file)
        file_permission.allowed_users.add(user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/fileshare/{private_file.id}/")

        assert response.status_code == status.HTTP_200_OK, f"Unexpected response: {response.content}"
        assert response.get("Content-Disposition") is not None, "File response is not being returned"

    def test_user_cannot_download_expired_file(self):
        """Test that a user cannot download a file after expiration time has passed"""
        owner = get_user_model().objects.create_user(
            username="owner",
            email="owner@gmail.com",
            password="password"
        )
        user = get_user_model().objects.create_user(
            username="username",
            email="user@gmail.com",
            password="password1"
        )
        collection = Collection.objects.create(title="collection1", user=owner)

        test_file = SimpleUploadedFile(
            "test_file.txt", b"Test file content", content_type="text/plain"
        )

        expired_file = PrivateFile.objects.create(
            file_name="expired_file.txt",
            file=test_file,
            password="securepass",
            expiration_time=timezone.now() - timezone.timedelta(days=1),  # Expired
            max_download_count=3
        )
        expired_file.collections.add(collection)
        expired_file.save()

        file_permission, created = FilePermission.objects.get_or_create(file=expired_file)
        file_permission.allowed_users.add(user)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/fileshare/{expired_file.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN, f"Expected forbidden, got {response.status_code}"
        assert "This file has expired" in response.json().get("message", ""), "Expiration message missing"
