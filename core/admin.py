from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Event, MediaItem, NewsArticle, SiteSettings, SocialLink, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Plataforma", {"fields": ("role", "phone")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "contact_email", "contact_phone", "updated_at")


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "is_published", "published_at")
    list_filter = ("is_featured", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "content")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_at", "location", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "description", "location")


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "sort_order", "is_active")
    list_filter = ("media_type", "is_active")
    list_editable = ("sort_order", "is_active")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
