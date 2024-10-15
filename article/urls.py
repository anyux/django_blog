#inclde path
from django.urls import path, re_path
from article.views import list, detail, create, delete, update

app_name = 'article'

urlpatterns =[
    path("list",list,name="list"),
    re_path(r"detail/(?P<pk>\d+)/$",detail,name="detail"),
    re_path(r"create/?$",create,name="create"),
    re_path(r"delete/(?P<pk>\d+)/?$",delete,name="delete"),
    re_path(r"update/(?P<pk>\d+)/?$",update,name="update"),

]