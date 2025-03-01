import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from vault.models import Collection


@pytest.mark.django_db
class TestCollections:
    def test_list_collections_for_authenticated_user(self):
        User = get_user_model()

        user1 = User.objects.create(username="user1", email="user1@gmail.com", password="testpass1")
        user2 = User.objects.create(username="user2", email="user2@gmail.com", password="testpass2")

        Collection.objects.create(title="User1 Collection", user=user1)
        Collection.objects.create(title="User2 Collection", user=user2)

        client = APIClient()
        client.force_authenticate(user=user1)

        response = client.get(f'/vault/users/{user1.id}/collections/')
        assert response.status_code == status.HTTP_200_OK

        response = client.get(f'/vault/users/{user2.id}/collections/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
