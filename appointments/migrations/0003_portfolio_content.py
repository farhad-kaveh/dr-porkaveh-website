from django.db import migrations, models


def seed_content(apps, schema_editor):
    SiteContent = apps.get_model('appointments', 'SiteContent')
    SiteContent.objects.get_or_create(
        key='about',
        defaults={
            'eyebrow': 'آشنایی با پزشک',
            'title': 'دکتر سجاد پورکاوه',
            'body': 'فارغ‌التحصیل از دانشگاه‌های مشهد و تبریز\nاستادیار دانشکده دندانپزشکی بجنورد',
        },
    )
    SiteContent.objects.get_or_create(
        key='education',
        defaults={
            'eyebrow': 'دانش و تجربه',
            'title': 'درمان تخصصی، بر پایه‌ی تشخیص دقیق',
            'body': 'محتوای آموزشی سایت در این بخش قرار می‌گیرد تا بیمار پیش از مراجعه، شناخت روشن‌تری از بیماری‌های لثه، ایمپلنت و روند درمان داشته باشد.',
            'button_text': 'مشاهده مطالب آموزشی',
            'button_url': '#contact',
        },
    )


class Migration(migrations.Migration):
    dependencies = [('appointments', '0002_casestudy_siteimage')]
    operations = [
        migrations.RenameField(model_name='casestudy', old_name='before_image', new_name='image'),
        migrations.RemoveField(model_name='casestudy', name='after_image'),
        migrations.AlterModelOptions(name='casestudy', options={'ordering': ['order', 'id'], 'verbose_name': 'نمونه‌کار', 'verbose_name_plural': 'نمونه‌کارها'}),
        migrations.AlterField(model_name='casestudy', name='image', field=models.ImageField(upload_to='cases/', verbose_name='عکس نمونه‌کار')),
        migrations.CreateModel(
            name='SiteContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('about', 'درباره ما / معرفی دکتر'), ('education', 'آموزش')], max_length=20, unique=True, verbose_name='بخش')),
                ('eyebrow', models.CharField(blank=True, max_length=120, verbose_name='عنوان کوچک')),
                ('title', models.CharField(max_length=250, verbose_name='عنوان اصلی')),
                ('body', models.TextField(verbose_name='متن')),
                ('button_text', models.CharField(blank=True, max_length=120, verbose_name='متن دکمه')),
                ('button_url', models.CharField(blank=True, max_length=250, verbose_name='لینک دکمه')),
                ('is_published', models.BooleanField(default=True, verbose_name='نمایش در سایت')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین ویرایش')),
            ],
            options={'ordering': ['key'], 'verbose_name': 'محتوای سایت', 'verbose_name_plural': 'محتوای سایت'},
        ),
        migrations.RunPython(seed_content, migrations.RunPython.noop),
    ]
