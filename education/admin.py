from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display=('title','category','order','is_published')
    list_filter=('category','is_published')
    list_editable=('order','is_published')
    search_fields=('title','excerpt','body')
    prepopulated_fields={'slug':('title',)}
