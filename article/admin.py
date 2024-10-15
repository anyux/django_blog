from django.contrib import admin

# Register your models here.

from .models import ArticlePost

@admin.register(ArticlePost)
class ArticlePostAdmin(admin.ModelAdmin):
    # 在这里你可以自定义后台显示和操作的行为
    list_display = ['title', 'created', 'updated']  # 列表中显示的字段
    search_fields = ['title']  # 搜索字段
    list_filter = ['created']  # 过滤器