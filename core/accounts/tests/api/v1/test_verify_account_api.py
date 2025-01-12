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
class TestVerifyAccountResendRequestApi:
    url = reverse("accounts:api-v1:verify-account-resend")

    def test_verify_account_resend_api_with_valid_data(
        self, api_client, common_user
    ):
        data = {"email": "tests@tests.com"}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 200

    def test_verify_account_resend_api_with_invalid_data(
        self, api_client, common_user
    ):
        data = {"email": "test2@tests.com"}
        response = api_client.post(self.url, data=data)
        assert response.status_code == 404


@pytest.mark.django_db
class TestVerifyAccountConfirmApi:
    def test_verify_account_confirmation_with_valid_data(
        self, api_client, common_user
    ):
        assert common_user.is_verified == False
        token = str(RefreshToken.for_user(common_user))
        url = reverse(
            "accounts:api-v1:verify-account", kwargs={"token": token}
        )
        response = api_client.get(url)
        common_user.refresh_from_db()
        assert common_user.is_verified
        assert response.status_code == 200

    def test_verify_account_confirmation_with_invalid_token(
        self, api_client, common_user
    ):
        token = "eyJhbGciOiJIUzI1NiIsInasdR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNjc1OTk4OSwiaWF0IjoxNzM2NjczNTg5LCJqdGkiOiIxNzdjZGU5OWVlYjEasas0MzMzOThkZjY1ZDhkYTg2Mjg0NCIsInVzZXJfaWQiOjF9.WIpApklVsxbl_sQoj7wjlJd-PEUL5fkc7A2sad4_SgxviY"
        url = reverse(
            "accounts:api-v1:verify-account", kwargs={"token": token}
        )
        response = api_client.get(url)
        assert response.status_code == 400
