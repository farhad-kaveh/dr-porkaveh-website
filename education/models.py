from django.db import models

class Article(models.Model):
    HYGIENE='hygiene'; IMPLANT='implant'; BRANDS='brands'; DISEASE='disease'
    CATEGORY_CHOICES=[
        (HYGIENE,'آموزش های ضروری بهداشت'),
        (IMPLANT,'آشنایی با درمان ایمپلنت'),
        (BRANDS,'برند های ایمپلنت'),
        (DISEASE,'بیماری شناسی'),
    ]
    title=models.CharField('عنوان',max_length=220)
    slug=models.SlugField('نشانی',max_length=220,unique=True,allow_unicode=True)
    category=models.CharField('دسته',max_length=20,choices=CATEGORY_CHOICES)
    excerpt=models.CharField('خلاصه',max_length=300)
    image=models.CharField('تصویر',max_length=220)
    body=models.TextField('متن')
    faq=models.JSONField('سوالات متداول',default=list,blank=True)
    sources=models.JSONField('منابع',default=list,blank=True)
    order=models.PositiveIntegerField('ترتیب',default=0)
    is_published=models.BooleanField('نمایش',default=True)
    class Meta:
        ordering=['category','order','id']
        verbose_name='مقاله آموزشی'; verbose_name_plural='مقالات آموزشی'
    def __str__(self): return self.title
