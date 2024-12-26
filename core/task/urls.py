from django.urls import path ,include
from . import views
app_name= 'tasks'
urlpatterns = [
    path('list/' ,views.TaskListView.as_view() ,name='task-list'),
    path('<int:pk>/details' ,views.TaskDetailView.as_view() , name='task-detail'),
    path('<int:pk>/edit' ,views.TaskEditView.as_view() ,name='task-edit'),
    path('<int:pk>/delete' ,views.TaskDeleteView.as_view() ,name='task-delete'),
    path('create/',views.TaskCreateView.as_view() , name='task-create'),
    path('update_task_status/<int:pk>' ,views.update_status ,name='update_task_status'),
    path('api/v1/',include('task.api.v1.urls'))
]