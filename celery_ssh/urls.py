#inclde path
from django.urls import path, re_path
from article.views import list, detail, create, delete, update
from celery_ssh.views import task_cmd,task_status

app_name = 'celery_ssh'

urlpatterns =[
    re_path("^task_cmd/?$",task_cmd,name="task_cmd"),
    re_path("^task_status/(?P<task_id>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/?$",task_status,name="task_status"),
]