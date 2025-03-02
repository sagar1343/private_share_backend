from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient

from vault.models import Collection, FilePermission, PrivateFile


@pytest.mark.django_db
class TestPrivateFile:

    def test_file_size_validation(self):
        large_file = SimpleUploadedFile(
            "large_file.txt",
            b"A" * (6 * 1024 * 1024),
            content_type="text/plain"
        )
        user = get_user_model().objects.create(username='user', email='user@email', password='password')
        collection = Collection.objects.create(title='test', user=user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post("/api/files/",
                               {"file_name": "test_file", "file": large_file, collection: [collection.id],
                                "expiration_time": (now() + timedelta(days=7)).isoformat()},
                               format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_collection(self):
        user = get_user_model().objects.create(username='user', email='user@email', password='password')
        collection = Collection.objects.create(title='test', user=user)

        another_user = get_user_model().objects.create_user(username='anotheruser',
                                                            email='another@gmail',
                                                            password='password123')
        client = APIClient()

        client.force_authenticate(user=another_user)

        small_file = SimpleUploadedFile(
            "restricted_file.txt",
            b"Restricted access",
            content_type="text/plain"
        )

        response = client.post("/api/files/", {
            "file_name": "test_file",
            "file": small_file,
            "collection": [collection.id],
            "expiration_time": (now() + timedelta(days=7)).isoformat()
        }, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_check_permission_is_creating_for_private_file(self):
        user = get_user_model().objects.create_user(username="testuser", password="testpass")
        collection1 = Collection.objects.create(title='test', user=user)
        private_file = PrivateFile.objects.create(file_name="test", file="test.txt",
                                                  expiration_time=(now() + timedelta(days=7)).isoformat())
        private_file.collections.set([collection1])

        assert FilePermission.objects.filter(file=private_file).exists()
