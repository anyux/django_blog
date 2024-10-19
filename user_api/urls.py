from django.urls import path,re_path,include

from user_api import views
from rest_framework import routers
from user_api.views import UserviewAPIView,app1viewAPIView,app2viewAPIView

app_name='user_api'

br='[0-9a-fA-F]'
reg=rf'{br}{{8}}-{br}{{4}}-{br}{{4}}-{br}{{4}}-{br}{{12}}'

urlpatterns = [
    path('api/user/', UserviewAPIView.as_view(),name='user'),
    re_path('^api/user/(?P<pk>\d+)/?$', UserviewAPIView.as_view(),name='user'),
    re_path('^app/?$', app1viewAPIView.as_view(),name='user'),
    re_path('^get/(?P<pk>.*)/?$', app2viewAPIView.as_view(),name='user'),
]