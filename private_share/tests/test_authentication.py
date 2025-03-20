import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from model_bakery import baker


@pytest.mark.django_db
class TestAuthentication:
    def test_only_authenticated_user_access_user_details(self):
        client = APIClient()
        response = client.get("/api/users/2/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_only_owner_access_their_details(self):
        client = APIClient()
        user1 = baker.make(get_user_model())

        client.force_authenticate(user=user1)
        response = client.get(f"/api/users/{user1.id}/")
        assert response.status_code == status.HTTP_200_OK

    def test_user_cannot_access_another_users_details(self):
        client = APIClient()
        user1 = baker.make(get_user_model())
        user2 = baker.make(get_user_model())

        client.force_authenticate(user=user1)
        response = client.get(f"/api/users/{user2.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
