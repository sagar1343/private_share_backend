from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.test import APIClient

from model_bakery import baker

from vault.models import Collection, PrivateFile, FilePermission
from vault.serializers import FilePermissionSerializer


@pytest.mark.django_db
class TestPermission:
    def test_user_permission_endpoint(self):
        user = baker.make(get_user_model())
        collection = baker.make(Collection, user=user)
        private_file = PrivateFile.objects.create(
            file_name="test",
            file="test.txt",
            expiration_time=(now() + timedelta(days=7)).isoformat(),
        )
        private_file.collections.add(collection)
        file_permission = FilePermission.objects.get(file=private_file.id)
        expected_response = FilePermissionSerializer(file_permission).data
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f"/api/files/{private_file.id}/permission/")

        assert response.status_code == 200
        assert response.data == expected_response
