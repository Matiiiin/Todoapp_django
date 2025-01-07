from django.urls import path ,include
from . import views
app_name = 'accounts'
urlpatterns = [
    path('' ,include("django.contrib.auth.urls")),
    path('register/' ,views.RegisterView.as_view() ,name='register'),
    path('api/v1/' ,include('accounts.api.v1.urls'))
]