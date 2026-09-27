from django.shortcuts import get_object_or_404, render
import json
from .models import Article

CATEGORIES = [
    ('hygiene','آموزش های ضروری بهداشت','برای اینکه مراقبت روزانه از دندان و لثه را ساده و درست انجام دهید.'),
    ('implant','آشنایی با درمان ایمپلنت','آنچه قبل از شروع درمان ایمپلنت لازم است بدانید.'),
    ('brands','برند های ایمپلنت','آشنایی کوتاه و مستند با سیستم‌های مورد استفاده در مطب.'),
    ('disease','بیماری شناسی','شناخت ساده و کاربردی بیماری‌هایی که دندان، لثه و استخوان را درگیر می‌کنند.'),
]

def index(request):
    articles=Article.objects.filter(is_published=True)
    groups=[]
    for key,title,desc in CATEGORIES:
        groups.append({'key':key,'title':title,'desc':desc,'articles':articles.filter(category=key)})
    return render(request,'education/index.html',{'groups':groups})

def detail(request,slug):
    article=get_object_or_404(Article,is_published=True,slug=slug)
    related=Article.objects.filter(is_published=True,category=article.category).exclude(pk=article.pk)[:3]
    article_jsonld=json.dumps({'@context':'https://schema.org','@type':'Article','headline':article.title,'description':article.excerpt,'inLanguage':'fa-IR','author':{'@type':'Person','name':'دکتر سجاد پورکاوه'}}, ensure_ascii=False)
    return render(request,'education/detail.html',{'article':article,'related':related,'article_jsonld':article_jsonld})
