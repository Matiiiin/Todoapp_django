from rest_framework.routers import DefaultRouter
from . import views

app_name = "api-v1"
router = DefaultRouter()
router.register("task", views.TaskListModelViewSet, "task")
urlpatterns = []
urlpatterns += router.urls
