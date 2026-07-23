from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import ContactMessage, Event, MediaItem, NewsArticle, SiteSettings, SocialLink, User, SignupForm, SignupSubmission


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
                "fields": ("contact_email", "contact_email_destination", "contact_phone", "whatsapp", "address"),
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


@admin.register(SignupForm)
class SignupFormAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (
            "Informações do Formulário",
            {
                "fields": ("title", "slug", "description", "is_active"),
            },
        ),
        (
            "Estrutura (Avançado)",
            {
                "fields": ("fields_schema",),
                "description": "Schema JSON com a estrutura do formulário.",
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(SignupSubmission)
class SignupSubmissionAdmin(admin.ModelAdmin):
    list_display = ("get_citizen_name", "get_protocol", "get_form_title", "created_at")
    list_filter = ("form", "created_at")
    search_fields = ("form__title", "data")
    readonly_fields = ("form", "created_at", "formatted_answers")
    
    fieldsets = (
        (
            None,
            {
                "fields": ("form", "created_at", "data"),
            },
        ),
        (
            "Dados Preenchidos",
            {
                "fields": ("formatted_answers",),
            },
        ),
    )

    def get_citizen_name(self, obj):
        return obj.data.get("nome_completo", "Não informado")
    get_citizen_name.short_description = "Nome do Cidadão"

    def get_protocol(self, obj):
        return obj.data.get("id_cadastro", "-")
    get_protocol.short_description = "Protocolo"

    def get_form_title(self, obj):
        return obj.form.title
    get_form_title.short_description = "Formulário"

    def formatted_answers(self, obj):
        if not obj.data:
            return "Nenhuma resposta"
        
        html = '''
        <style>
            .field-data {
                display: none !important;
            }
            .submission-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                width: 100%;
                margin-top: 10px;
            }
            @media (max-width: 1200px) {
                .submission-grid { grid-template-columns: repeat(3, 1fr); }
            }
            @media (max-width: 900px) {
                .submission-grid { grid-template-columns: repeat(2, 1fr); }
            }
            @media (max-width: 600px) {
                .submission-grid { grid-template-columns: 1fr; }
            }
            .submission-card {
                position: relative;
                background: var(--darkened-bg, rgba(0, 0, 0, 0.03));
                padding: 16px;
                padding-right: 40px;
                border-radius: 8px;
                border: 1px solid var(--border-color, #e0e0e0);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .submission-card:hover {
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }
            .edit-icon {
                position: absolute;
                top: 12px;
                right: 12px;
                cursor: pointer;
                color: #ffffff;
                opacity: 0.2;
                transition: opacity 0.2s, transform 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .submission-card:hover .edit-icon {
                opacity: 0.6;
            }
            .edit-icon:hover {
                opacity: 1 !important;
                transform: scale(1.1);
            }
            .inline-edit-input {
                width: 100%;
                padding: 4px;
                border: 1px solid var(--primary, #1351b4);
                border-radius: 4px;
                background: var(--body-bg, #fff);
                color: var(--body-fg, #222);
                font-size: 1.05rem;
                box-sizing: border-box;
                font-family: inherit;
            }
            .inline-edit-input:focus {
                outline: none;
            }
            .submission-label {
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                color: var(--body-quiet-color, #777);
                margin-bottom: 6px;
                font-weight: 700;
            }
            .submission-value {
                font-size: 1.05rem;
                font-weight: 500;
                color: var(--body-fg, #222);
                word-break: break-word;
                line-height: 1.4;
                min-height: 20px;
            }
        </style>
        <div class="submission-grid">
        '''
        
        for key, value in obj.data.items():
            clean_key = str(key).replace('_', ' ').title()
            if not value:
                display_value = '<span style="color: var(--body-quiet-color); font-style: italic;">Não informado</span>'
            else:
                display_value = str(value)
                
            html += f'''
                <div class="submission-card" data-key="{key}">
                    <div class="edit-icon" title="Editar este campo">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                    </div>
                    <div class="submission-label">{clean_key}</div>
                    <div class="submission-value">{display_value}</div>
                </div>
            '''
        
        html += '''
        </div>
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            var dataTextarea = document.querySelector('.field-data textarea');
            if (!dataTextarea) return;

            var editIcons = document.querySelectorAll('.edit-icon');
            editIcons.forEach(function(icon) {
                icon.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var card = this.closest('.submission-card');
                    var valContainer = card.querySelector('.submission-value');
                    var key = card.getAttribute('data-key');
                    var currentText = valContainer.innerText.trim();
                    
                    if (valContainer.querySelector('input')) return;
                    
                    var input = document.createElement('input');
                    input.className = 'inline-edit-input';
                    input.type = 'text';
                    input.value = currentText === 'Não informado' ? '' : currentText;
                    
                    var saveEdit = function() {
                        var newVal = input.value.trim();
                        if (newVal === '') {
                            valContainer.innerHTML = '<span style="color: var(--body-quiet-color); font-style: italic;">Não informado</span>';
                        } else {
                            valContainer.innerText = newVal;
                        }
                        
                        try {
                            var dataObj = JSON.parse(dataTextarea.value);
                            dataObj[key] = newVal;
                            dataTextarea.value = JSON.stringify(dataObj);
                        } catch(err) {
                            console.error('Erro ao atualizar JSON', err);
                        }
                    };
                    
                    input.addEventListener('blur', saveEdit);
                    input.addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            input.blur();
                        }
                    });
                    
                    valContainer.innerHTML = '';
                    valContainer.appendChild(input);
                    input.focus();
                });
            });
        });
        </script>
        '''
        return mark_safe(html)
    formatted_answers.short_description = "Dados Preenchidos"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject", "message")
    list_editable = ("status",)
    readonly_fields = ("name", "email", "subject", "message", "created_at", "updated_at")
    fieldsets = (
        (
            "Mensagem recebida",
            {
                "fields": ("name", "email", "subject", "message"),
            },
        ),
        (
            "Gerenciamento",
            {
                "fields": ("status", "created_at", "updated_at"),
            },
        ),
    )
    actions = ["mark_as_read", "mark_as_replied", "mark_as_archived"]

    @admin.action(description="Marcar como lida")
    def mark_as_read(self, request, queryset):
        queryset.update(status=ContactMessage.Status.READ)

    @admin.action(description="Marcar como respondida")
    def mark_as_replied(self, request, queryset):
        queryset.update(status=ContactMessage.Status.REPLIED)

    @admin.action(description="Arquivar")
    def mark_as_archived(self, request, queryset):
        queryset.update(status=ContactMessage.Status.ARCHIVED)
