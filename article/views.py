from lib2to3.fixes.fix_input import context

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, Http404
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect, resolve_url
from django.template.defaulttags import csrf_token
from django.urls import resolve

import markdown
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from article.forms import ArticlePostForm
from article.models import ArticlePost as ap
# Create your views here.

def list(request):
    """
    这是api的文档说明
    :param request: Django HttpRequest 对象
    :return: [
        {
            'id': article.get("id"),
            'title': article.get("title"),
            'body': article.get("body"),
            'created': article.get("created"),
            'updated': article.get("updated"),
            'author': article.get("author__username"),
            'link': resolve_url('article:detail', article.get("id")),
        }
    ]
    """
    # articles = ap.objects.all().values("id", "title", "body", "author__username")
    articles = ap.objects.all().values("id", "title", "body","created","updated","author__username")
    context = []
    for article in articles:
        print(article.keys())
        article_data = {
            'id': article.get("id"),
            'title': article.get("title"),
            'body': article.get("body"),
            'created': article.get("created"),
            'updated': article.get("updated"),
            'author': article.get("author__username"),
            'link': resolve_url('article:detail', article.get("id")),
        }
        context.append(article_data)
    return JsonResponse(context, safe=False)

def detail(request, pk):
    if not pk:
        redirect('article:list')
    try:
      article=ap.objects.get(pk=pk)
      article.body = markdown.markdown(
          article.body,
          extensions=[
              'markdown.extensions.extra',
              'markdown.extensions.codehilite',
          ]
      )
      # 使用 Django 的序列化工具将模型实例序列化为 JSON
      context = {
          'id': article.id,
          'title': article.title,
          'body': article.body,
          'created': article.created,
          'updated': article.updated,
          'author': article.author.username,
          'link': resolve_url('article:detail', pk)
      }
    except ap.DoesNotExist:
        context = {
            'id': None,
            'title': "",
            'body': "",
            'created': '',
            'updated': '',
            'author': '',
            'link': '',
        }
    finally:
        return JsonResponse(context, safe=False)

# @csrf_exempt
def create(request):
    if request.method == 'POST':
        article_post_form = ArticlePostForm(request.POST)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=1)
            new_article.save()
            return detail(request,new_article.id)
        else:
            context = {
                "status": "error",
                "message": article_post_form.errors,
            }
            return JsonResponse(context, safe=False)
    else:
        form = ArticlePostForm()
        form_field = {
            field_name: {
                'type': type(form.fields[field_name]).__name__,
                'label': form.fields[field_name].label,
                'required': form.fields[field_name].required,
            }for field_name in form.fields
        }
        csrf_token=get_token(request)
        context = {
            'form_field': form_field ,
            'status': 'success',
            'csrf_token': csrf_token
        }
        return JsonResponse(context, safe=False)


@require_http_methods(['POST'])
def delete(request, pk):
    try:
        ap.objects.get(pk=pk).delete()
        article = ap.objects.filter(id=pk, is_deleted=False).first()

        if article:
            article.is_deleted = True  # 标记为已删除
            article.save()
            message = {
                'status': 'success',
                'message': 'Article id: {} deleted successfully'.format(pk),
            }
        else:
            message = {
                'status': 'error',
                'message': 'Article id: {} not found or already deleted'.format(pk),
            }
    except ap.DoesNotExist:
        message = {
            'id': None,
            'title': "",
            'body': "",
            'created': '',
            'updated': '',
            'author': '',
            'link': '',
        }
    finally:
        print(message)
        print(article)
        return JsonResponse(message, safe=False)


@require_http_methods(['POST','GET'])
def update(request, pk):
    if request.method == 'GET':
        return detail(request, pk)


