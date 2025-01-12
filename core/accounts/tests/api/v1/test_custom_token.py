import json
import sys
from rest_framework.test import APIClient , force_authenticate
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
    user = get_user_model().objects.create_user(email='test@test.com' , password='123')
    return user

@pytest.mark.django_db
class TestCustomTokenLogin:
    url = reverse('accounts:api-v1:token-login')
    def test_token_login_with_valid_credentials(self ,api_client , common_user):
        data = {
            'email':'test@test.com',
            'password':'123'
        }
        response = api_client.post(self.url , data=data)
        assert  response.status_code == 200
        assert 'token' in response.json()
        assert common_user.auth_token.key == response.json().get('token')
        assert Token.objects.filter(user=common_user).exists()

    def test_token_login_with_invalid_credentials(self ,api_client , common_user):
        data = {
            'email':'test@test.com',
            'password':'1234'
        }
        response = api_client.post(self.url , data=data)
        assert  response.status_code == 400
@pytest.mark.django_db
class TestCustomTokenLogout:
    url = reverse('accounts:api-v1:token-logout')
    def test_custom_token_logout_with_anonymous_user(self , api_client):
        response = api_client.post(self.url)
        assert response.status_code == 401
    def test_custom_token_logout_with_authenticated_user(self ,api_client , common_user):
        auth_token = Token.objects.get_or_create(user=common_user)[0]
        response = api_client.post(self.url , headers={'Authorization':f'Token {auth_token}'})
        assert Token.objects.filter(key=auth_token).exists() == False
        assert response.status_code == 200