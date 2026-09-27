from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0003_portfolio_content'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_start', models.DateField(unique=True, verbose_name='شروع هفته (شنبه)')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('note', models.CharField(blank=True, max_length=250, verbose_name='توضیح')),
            ],
            options={
                'ordering': ['-week_start'],
                'verbose_name': 'برنامه اختصاصی هفته',
                'verbose_name_plural': 'برنامه‌های اختصاصی هفته',
            },
        ),
        migrations.AddField(
            model_name='weeklyschedule',
            name='schedule_week',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='days', to='appointments.scheduleweek', verbose_name='هفته اختصاصی'),
        ),
    ]
