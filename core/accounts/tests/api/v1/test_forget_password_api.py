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
from rest_framework.authtoken.models import Token


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def common_user():
    user = get_user_model().objects.create_user(
        email="test@test.com", password="123"
    )
    return user


@pytest.mark.django_db
class TestForgetPasswordRequestApi:
    url = reverse("accounts:api-v1:forget-password")

    def test_forget_password_api_with_valid_data(
        self, api_client, common_user
    ):
        data = {"email": "test@test.com"}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 200

    def test_forget_password_api_with_invalid_data(
        self, api_client, common_user
    ):
        data = {"email": "testt@test.com"}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 404


@pytest.mark.django_db
class TestForgetPasswordConfirmApi:
    def test_forget_password_confirm_api_with_valid_data(
        self, api_client, common_user
    ):
        token = str(RefreshToken.for_user(common_user))
        url = reverse(
            "accounts:api-v1:forget-password-confirm", kwargs={"token": token}
        )
        temp_password = "asd"
        common_user.set_password(temp_password)
        common_user.is_verified = True
        common_user.save()
        new_password = "1234"
        data = {
            "temporary_password": temp_password,
            "new_password": new_password,
        }
        response = api_client.post(url, data=data)
        common_user.refresh_from_db()
        assert response.status_code == 200
        assert common_user.check_password(new_password)

    def test_forget_password_confirm_api_with_invalid_token(
        self, api_client, common_user
    ):
        token = "eyJhbGciOiJIUzI1NiIsInasdR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNjc1OTk4OSwiaWF0IjoxNzM2NjczNTg5LCJqdGkiOiIxNzdjZGU5OWVlYjEasas0MzMzOThkZjY1ZDhkYTg2Mjg0NCIsInVzZXJfaWQiOjF9.WIpApklVsxbl_sQoj7wjlJd-PEUL5fkc7A2sad4_SgxviY"
        url = reverse(
            "accounts:api-v1:forget-password-confirm", kwargs={"token": token}
        )
        temp_password = "asd"
        common_user.set_password(temp_password)
        common_user.is_verified = True
        common_user.save()
        new_password = "1234"
        data = {
            "temporary_password": temp_password,
            "new_password": new_password,
        }
        response = api_client.post(url, data=data)
        assert response.status_code == 400

    def test_forget_password_confirm_api_with_invalid_data(
        self, api_client, common_user
    ):
        token = str(RefreshToken.for_user(common_user))
        url = reverse(
            "accounts:api-v1:forget-password-confirm", kwargs={"token": token}
        )
        temp_password = "asd"
        common_user.set_password(temp_password)
        common_user.is_verified = True
        common_user.save()
        new_password = "1234"
        data = {"temporary_password": "asdf", "new_password": new_password}
        response = api_client.post(url, data=data)
        assert response.status_code == 400
