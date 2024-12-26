from django.urls import path ,include
from . import views
app_name = 'accounts'
urlpatterns = [
    path('register/' ,views.RegisterView.as_view() ,name='register'),
    path('api/v1/' ,include('accounts.api.v1.urls'))
]