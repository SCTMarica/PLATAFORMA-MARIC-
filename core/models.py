from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "cliente_final", "Cliente final"
        SUPERVISOR = "supervisor_coordenador", "Supervisor/Coordenador"
        MASTER = "administrador_master", "Administrador master"

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    phone = models.CharField(max_length=20, blank=True)

    @property
    def can_access_admin(self):
        return self.is_active and (
            self.is_superuser or self.is_staff or self.role in {self.Role.SUPERVISOR, self.Role.MASTER}
        )

    def save(self, *args, **kwargs):
        if self.role == self.Role.MASTER:
            self.is_superuser = True
            self.is_staff = True
        elif self.role == self.Role.SUPERVISOR:
            self.is_staff = True
        elif not self.is_superuser:
            self.is_staff = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username


class SiteSettings(TimeStampedModel):
    site_name = models.CharField(max_length=150, default="Plataforma Maric")
    tagline = models.CharField(max_length=200, blank=True)
    hero_title = models.CharField(max_length=200)
    hero_subtitle = models.TextField(blank=True)
    about_title = models.CharField(max_length=200, default="Sobre a instituição")
    about_content = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=7, default="#0d6efd")
    secondary_color = models.CharField(max_length=7, default="#0b132b")
    accent_color = models.CharField(max_length=7, default="#f59e0b")
    footer_text = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Configuração do site"
        verbose_name_plural = "Configurações do site"

    def __str__(self):
        return self.site_name


class PublishedContentQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(is_published=True).filter(
            models.Q(published_at__isnull=True) | models.Q(published_at__lte=now)
        )


class NewsArticle(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.CharField(max_length=255)
    content = models.TextField()
    cover_image_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    objects = PublishedContentQuerySet.as_manager()

    class Meta:
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:news-detail", args=[self.slug])


class Event(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.CharField(max_length=255)
    description = models.TextField()
    cover_image_url = models.URLField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    registration_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    objects = PublishedContentQuerySet.as_manager()

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["start_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:event-detail", args=[self.slug])


class MediaItem(TimeStampedModel):
    class MediaType(models.TextChoices):
        BANNER = "banner", "Banner"
        VIDEO = "video", "Vídeo"
        GALLERY = "gallery", "Galeria"

    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=20, choices=MediaType.choices)
    description = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    external_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Mídia"
        verbose_name_plural = "Mídias"
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"


class SocialLink(TimeStampedModel):
    label = models.CharField(max_length=80)
    url = models.URLField()
    icon_class = models.CharField(max_length=50, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Link social/externo"
        verbose_name_plural = "Links sociais/externos"
        ordering = ["sort_order", "label"]

    def __str__(self):
        return self.label


class SignupForm(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    fields_schema = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Formulario de inscricao"
        verbose_name_plural = "Formularios de inscricao"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:signup-form-detail", args=[self.slug])


class SignupSubmission(TimeStampedModel):
    form = models.ForeignKey(SignupForm, on_delete=models.CASCADE, related_name="submissions")
    data = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Inscricao enviada"
        verbose_name_plural = "Inscricoes enviadas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.form.title} - {self.created_at:%d/%m/%Y %H:%M}"
