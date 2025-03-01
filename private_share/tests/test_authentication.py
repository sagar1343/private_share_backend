import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestAuthentication:
    def test_only_authenticated_user_access_user_details(self):
        client = APIClient()
        response = client.get('/vault/users/2/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_only_owner_access_details(self):
        client = APIClient()
        user1 = get_user_model().objects.create(username="username1", email="user1@gmail.com", password="password1")
        user2 = get_user_model().objects.create(username="username2", email="user2@gmail.com", password="password2")

        client.force_authenticate(user=user1)
        response = client.get(f'/vault/users/{user1.id}/')
        assert response.status_code == status.HTTP_200_OK

        response = client.get(f'/vault/users/{user2.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_user_for_admin_user_only(self):
        client = APIClient()
        admin = get_user_model().objects.create_superuser(email='admin@gmail.com',
                                                          username='admin',
                                                          password='password')
        client.force_authenticate(user=admin)
        response = client.get('/vault/users/')
        assert response.status_code == status.HTTP_200_OK
