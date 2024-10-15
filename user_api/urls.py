from django.urls import path,re_path,include

from celery_ssh.urls import app_name
from user_api import views
from rest_framework import routers

app_name='user_api'

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]