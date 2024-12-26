import sys

from rest_framework.viewsets import GenericViewSet , ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from task.models import Task
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskSerializer
from .paginations import DefaultPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
class TaskListModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend ,SearchFilter]
    filterset_fields = ['title']
    search_fields = ['title' ,'author__first_name']
    lookup_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user.profile)
    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)
    def perform_update(self, serializer):
        serializer.save(author=self.request.user.profile)
    def perform_destroy(self, instance):
        if instance.author.user == self.request.user:
            return super().perform_destroy(instance)
