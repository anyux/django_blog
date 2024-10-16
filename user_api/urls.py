from django.urls import path,re_path,include

from celery_ssh.urls import app_name
from user_api import views
from rest_framework import routers
from user_api.views import DiskInfoViewSet,TaskStatusView,RunPlaybookView,RunAdHocCommandView

app_name='user_api'

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
br='[0-9a-fA-F]'
reg=rf'{br}{{8}}-{br}{{4}}-{br}{{4}}-{br}{{4}}-{br}{{12}}'

urlpatterns = [
    path('api/', include(router.urls)),
    re_path('^disk-info/?$', DiskInfoViewSet.as_view(), name='disk-info-post'),
    re_path('^disk-info/(?P<task_id>{})/?$'.format(reg), DiskInfoViewSet.as_view(), name='disk-info-get'),
    path('run-playbook/', RunPlaybookView.as_view(), name='run-playbook'),
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    re_path('^run-adhoc/?$', RunAdHocCommandView.as_view(), name='run-adhoc'),

]