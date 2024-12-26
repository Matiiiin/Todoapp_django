from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('auth' ,views.AuthUserViewSet ,'auth')
urlpatterns = []
urlpatterns += router.urls