from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html

from .models import Event, MediaItem, NewsArticle, SiteSettings, SocialLink, User


admin.site.site_header = "Painel Plataforma Maric"
admin.site.site_title = "Admin Plataforma Maric"
admin.site.index_title = "Configuracao e gestao de conteudo"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Plataforma", {"fields": ("role", "phone")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "contact_email", "contact_phone", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Identidade do site",
            {
                "fields": ("site_name", "tagline", "logo_url"),
                "description": "Informacoes basicas exibidas no cabecalho e no rodape.",
            },
        ),
        (
            "Configuracao da home",
            {
                "fields": ("hero_title", "hero_subtitle", "footer_text"),
                "description": "Edite aqui os textos principais da home. As imagens do carrossel sao configuradas em Midias, usando o tipo Banner.",
            },
        ),
        (
            "Pagina institucional",
            {
                "fields": ("about_title", "about_content"),
            },
        ),
        (
            "Contato",
            {
                "fields": ("contact_email", "contact_phone", "whatsapp", "address"),
            },
        ),
        (
            "Aparencia",
            {
                "fields": ("primary_color", "secondary_color", "accent_color"),
            },
        ),
        (
            "Controle",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "is_published", "published_at")
    list_filter = ("is_featured", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "content")
    fieldsets = (
        (
            "Publicacao",
            {
                "fields": ("title", "slug", "is_published", "is_featured", "published_at"),
                "description": "Cadastre a noticia, defina se ela esta publicada e se deve receber destaque.",
            },
        ),
        (
            "Conteudo",
            {
                "fields": ("summary", "content", "cover_image_url"),
            },
        ),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_at", "location", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "description", "location")
    fieldsets = (
        (
            "Publicacao",
            {
                "fields": ("title", "slug", "is_published", "published_at"),
                "description": "Defina o nome do evento e se ele ja pode aparecer no portal.",
            },
        ),
        (
            "Detalhes do evento",
            {
                "fields": ("summary", "description", "cover_image_url"),
            },
        ),
        (
            "Agenda e acesso",
            {
                "fields": ("start_at", "end_at", "location", "registration_url"),
            },
        ),
    )


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "sort_order", "is_active", "image_preview")
    list_filter = ("media_type", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "description")
    fieldsets = (
        (
            "Uso no site",
            {
                "fields": ("media_type", "is_active", "sort_order"),
                "description": "Para o carrossel da home, selecione o tipo Banner e deixe o item ativo.",
            },
        ),
        (
            "Conteudo exibido",
            {
                "fields": ("title", "description", "external_url"),
                "description": "Titulo e descricao aparecem no carrossel da home.",
            },
        ),
        (
            "Arquivos e links de midia",
            {
                "fields": ("image_url", "image_preview", "video_url"),
            },
        ),
    )
    readonly_fields = ("image_preview",)

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if not obj.image_url:
            return "-"
        return format_html(
            '<img src="{}" alt="{}" style="width: 120px; height: 72px; object-fit: cover; border-radius: 8px; border: 1px solid #dbe2ea;">',
            obj.image_url,
            obj.title,
        )


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("label", "url", "icon_class")
    fieldsets = (
        (
            "Link exibido",
            {
                "fields": ("label", "url", "icon_class"),
                "description": "Use esta area para cadastrar links oficiais e redes sociais mostrados no portal.",
            },
        ),
        (
            "Exibicao",
            {
                "fields": ("sort_order", "is_active"),
            },
        ),
    )
