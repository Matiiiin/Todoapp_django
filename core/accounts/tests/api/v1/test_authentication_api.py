from rest_framework.test import APIClient
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def common_user():
    user = get_user_model().objects.create_user(
        email="tests@tests.com", password="123"
    )
    return user


@pytest.mark.django_db
class TestRegisterApi:
    url = reverse("accounts:api-v1:auth-register")

    def test_register_api_with_valid_data(self, api_client):
        data = {
            "email": "tests@tests.com",
            "password1": "123",
            "password2": "123",
        }
        response = api_client.post(self.url, data=data)
        user = get_user_model().objects.filter(email=data["email"])
        assert response.status_code == 201
        assert user.exists() == True
        assert user.get().is_authenticated == True
        assert user.get().is_verified == False

    def test_register_api_with_invalid_data(self, api_client):
        data = {
            "email": "tests@tests.com",
            "password1": "123",
        }
        response = api_client.post(self.url, data=data)
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginApi:
    url = reverse("accounts:api-v1:auth-login")

    def test_login_api_with_valid_data(self, api_client, common_user):
        user = common_user
        user.is_verified = True
        user.save()
        data = {"email": "tests@tests.com", "password": "123"}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 200

    def test_login_api_with_invalid_data(self, api_client, common_user):
        user = common_user
        user.is_verified = True
        user.save()
        data = {"email": "tests@tests.com", "password": "1234"}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 400

    def test_login_api_with_unverified_user(self, api_client, common_user):
        user = common_user
        data = {"email": "tests@tests.com", "password": "1234"}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogoutApi:
    url = reverse("accounts:api-v1:auth-logout")

    def test_logout_api_with_anonymous_user(self, api_client):
        response = api_client.post(self.url)
        assert response.status_code == 401

    def test_logout_with_authenticated_user(self, api_client, common_user):
        user = common_user
        api_client.force_authenticate(user=user)
        response = api_client.post(self.url)
        assert response.status_code == 200
