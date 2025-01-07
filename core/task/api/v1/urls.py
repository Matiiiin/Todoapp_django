from rest_framework.routers import DefaultRouter
from . import views

app_name = "api-v1"
router = DefaultRouter()
router.register("task", views.TaskListModelViewSet, "api_v1_task")
urlpatterns = []
urlpatterns += router.urls
