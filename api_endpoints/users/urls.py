from django.urls import path
from users.views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('create_alert/', create_alert, name='create_alert'),
    path('delete_alert/', delete_alert, name='delete_alert'),
    path('fetch_alerts/', fetch_alerts, name='fetch_alerts'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login_token_refresh'),
]