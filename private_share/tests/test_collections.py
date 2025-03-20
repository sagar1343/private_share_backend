import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from model_bakery import baker
from vault.models import Collection


@pytest.mark.django_db
class TestCollections:
    def test_list_collections_for_authenticated_user(self):
        user1 = baker.make(get_user_model())
        user2 = baker.make(get_user_model())

        baker.make(Collection, user=user1)
        baker.make(Collection, user=user2)

        client = APIClient()
        client.force_authenticate(user=user1)

        response = client.get(f"/api/users/{user1.id}/collections/")
        assert response.status_code == status.HTTP_200_OK

        response = client.get(f"/api/users/{user2.id}/collections/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_prevent_duplicate_collections(self):
        user1 = baker.make(get_user_model())

        collection = baker.make(Collection, user=user1)

        api_client = APIClient()
        api_client.force_authenticate(user=user1)

        response = api_client.post(
            f"/api/users/{user1.id}/collections/", data={"title": collection.title}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
