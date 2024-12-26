from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register('task' ,views.TaskListModelViewSet , 'api_v1_task')
urlpatterns = []
urlpatterns += router.urls