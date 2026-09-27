from django.db import migrations


def update_about(apps, schema_editor):
    SiteContent = apps.get_model("appointments", "SiteContent")
    obj = SiteContent.objects.filter(key="about").first()
    if obj:
        obj.body = obj.body.replace("عضو هیئت علمی دانشگاه", "استادیار دانشکده دندانپزشکی بجنورد")
        obj.save(update_fields=["body", "updated_at"])


def reverse_update(apps, schema_editor):
    SiteContent = apps.get_model("appointments", "SiteContent")
    obj = SiteContent.objects.filter(key="about").first()
    if obj:
        obj.body = obj.body.replace("استادیار دانشکده دندانپزشکی بجنورد", "عضو هیئت علمی دانشگاه")
        obj.save(update_fields=["body", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [("appointments", "0006_ensure_default_schedule")]
    operations = [migrations.RunPython(update_about, reverse_update)]
