# Generated by Django 2.0.5 on 2018-06-25 02:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('m', '0005_webpage_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='webpage',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='webpages', to=settings.AUTH_USER_MODEL),
        ),
    ]