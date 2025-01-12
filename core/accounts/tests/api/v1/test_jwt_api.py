import json
import sys
from rest_framework.test import APIClient, force_authenticate
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


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
class TestJWTCreateApi:
    url = reverse("accounts:api-v1:jwt-create")

    def test_jwt_create_with_valid_data(self, api_client, common_user):
        user = common_user
        user.is_verified = True
        user.save()
        data = {
            "email": "tests@tests.com",
            "password": "123",
        }
        response = api_client.post(self.url, data=data)
        assert response.status_code == 201

    def test_jwt_create_with_invalid_data(self, api_client, common_user):
        user = common_user
        user.is_verified = True
        user.save()
        data = {
            "email": "tests@tests.com",
            "password": "1234",
        }
        response = api_client.post(self.url, data=data)
        assert response.status_code == 400
        assert "Invalid credentials" in response.json().get("detail")[0]


@pytest.mark.django_db
class TestJWTRefreshApi:
    url = reverse("accounts:api-v1:jwt-refresh")

    def test_jwt_access_create_with_valid_refresh_token(
        self, api_client, common_user
    ):
        user = common_user
        user.is_verified = True
        user.save()
        refresh_token = RefreshToken().for_user(user)
        data = {"refresh": refresh_token}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 200

    def test_jwt_access_create_with_invalid_refresh_token(
        self, api_client, common_user
    ):
        user = common_user
        user.is_verified = True
        user.save()
        invalid_refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM2NjY0NTI5LCJpYXQiOjE3MzY2NjQyMjksImp0aSI6IjczNzIyZGE0YmVkZDQyOGI5OTasdEwNzExM2E3ODRhNTY5IiwidXNlcl9pZCI6MX0.2BBi7tiWMDfwkyieeTGGCStPCXM3EZS8YecD5yrapbs"
        data = {"refresh": invalid_refresh_token}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 400
