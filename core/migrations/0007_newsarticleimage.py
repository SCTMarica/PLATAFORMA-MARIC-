import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import core.models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_merge_20260723_1846"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsArticleImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("upload_token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("image", models.FileField(upload_to=core.models.news_image_upload_to)),
                ("alt_text", models.CharField(blank=True, max_length=200)),
                ("article", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="body_images", to="core.newsarticle")),
                ("uploaded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="uploaded_news_images", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Imagem de notícia",
                "verbose_name_plural": "Imagens de notícias",
                "ordering": ["created_at"],
            },
        ),
    ]
