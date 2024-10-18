from django.urls import path,re_path,include

from task_api.views import TaskAPIView,TaskRunAPIView

app_name='task_api'

br='[0-9a-fA-F]'
reg=rf'{br}{{8}}-{br}{{4}}-{br}{{4}}-{br}{{4}}-{br}{{12}}'
t=re_path('^api/task/(?P<pk>{})/?$'.format(reg), TaskAPIView.as_view(),name='task_api'),
print(t)

urlpatterns = [
    re_path('^api/task/?$', TaskAPIView.as_view(),name='task_api'),
    re_path('^api/task/(?P<pk>{})/?$'.format(reg), TaskAPIView.as_view(),name='task_api'),
    re_path('^api/run_task/(?P<pk>{})?$'.format(reg), TaskRunAPIView.as_view(),name='task_run_api'),
]