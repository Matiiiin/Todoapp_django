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
from task.models import Task


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
@pytest.fixture
def task(common_user):
    return Task.objects.create(author=common_user.profile , title='test' , status='NEW')

@pytest.mark.django_db
class TestTaskCreateApi:
    url = reverse('tasks:api-v1:task-list')
    def test_create_a_task_with_valid_data(self,api_client ,common_user):
        data = {
            'title':'test',
            'status':'NEW',
        }
        api_client.force_authenticate(user=common_user)
        response = api_client.post(self.url , data=data)
        assert response.status_code == 201
        assert Task.objects.filter(author__user=common_user , title='test' , status='NEW').exists()
    def test_create_a_task_with_anonymous_user(self,api_client ,common_user):
        data = {
            'title':'test',
            'status':'NEW',
        }
        response = api_client.post(self.url , data=data)
        assert response.status_code == 401

    def test_create_a_task_with_invalid_data(self,api_client ,common_user):
        data = {
            'title':'test',
            'status':'asd',
        }
        api_client.force_authenticate(user=common_user)
        response = api_client.post(self.url , data=data)
        assert response.status_code == 400
        assert Task.objects.filter(author__user=common_user , title='test' , status='NEW').exists() == False
@pytest.mark.django_db
class TestTaskRetrieveApi:
    def test_retrieve_a_task_as_authorized_user(self, api_client, common_user, task):
        api_client.force_authenticate(user=common_user)
        response = api_client.get(reverse('tasks:api-v1:task-detail', args=[task.id]))
        assert response.status_code == 200
        assert response.json()['title'] == task.title
        assert response.json()['status'] == task.status

    def test_retrieve_a_task_as_anonymous_user(self, api_client, task):
        response = api_client.get(reverse('tasks:api-v1:task-detail', args=[task.id]))
        assert response.status_code == 401
@pytest.mark.django_db

class TestTaskUpdateApi:
    def test_update_a_task_with_valid_data(self, api_client, common_user, task):
        data = {
            'title': 'updated title',
            'status': 'DONE',
        }
        api_client.force_authenticate(user=common_user)
        response = api_client.put(reverse('tasks:api-v1:task-detail', args=[task.id]), data=data)
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.title == 'updated title'
        assert task.status == 'DONE'

    def test_update_a_task_with_invalid_data(self, api_client, common_user, task):
        data = {
            'title': 'updated title',
            'status': 'qwe',
        }
        api_client.force_authenticate(user=common_user)
        response = api_client.put(reverse('tasks:api-v1:task-detail', args=[task.id]), data=data)
        assert response.status_code == 400

    def test_update_a_task_as_anonymous_user(self, api_client, task):
        data = {
            'title': 'updated title',
            'status': 'NEW',
        }
        response = api_client.put(reverse('tasks:api-v1:task-detail', args=[task.id]), data=data)
        assert response.status_code == 401


@pytest.mark.django_db
class TestTaskDeleteApi:
    def test_delete_a_task_as_authorized_user(self, api_client, common_user, task):
        api_client.force_authenticate(user=common_user)
        response = api_client.delete(reverse('tasks:api-v1:task-detail', args=[task.id]))
        assert response.status_code == 204
        assert Task.objects.filter(id=task.id).exists() == False

    def test_delete_a_task_as_anonymous_user(self, api_client, task):
        response = api_client.delete(reverse('tasks:api-v1:task-detail', args=[task.id]))
        assert response.status_code == 401
