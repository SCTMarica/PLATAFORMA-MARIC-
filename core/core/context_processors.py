from types import SimpleNamespace

from .i18n import SUPPORTED_LANGUAGES, get_language_from_request
from .models import SiteSettings, SocialLink


DEFAULT_SITE_SETTINGS = {
    "site_name": "Nome do Site",
    "tagline": "Base white-label institucional com portal preparado para evolucao.",
    "hero_title": "Transforme sua presença institucional em uma plataforma pronta para evoluir.",
    "hero_subtitle": "Frontend público, CMS simples no admin e estrutura preparada para login, cadastro e portal restrito.",
    "about_title": "Sobre a instituição",
    "about_content": "Preencha as informações institucionais no admin para personalizar esta instalação.",
    "contact_email": "contato@exemplo.com",
    "contact_phone": "(00) 0000-0000",
    "whatsapp": "(00) 00000-0000",
    "address": "Endereço institucional",
    "logo_url": "",
    "primary_color": "#0d6efd",
    "secondary_color": "#0b132b",
    "accent_color": "#f59e0b",
    "footer_text": "Base institucional white-label pronta para personalização.",
}


def site_branding(request):
    settings = SiteSettings.objects.order_by("id").first()
    site_settings = SimpleNamespace(**DEFAULT_SITE_SETTINGS)

    if settings:
        for key, value in DEFAULT_SITE_SETTINGS.items():
            setattr(site_settings, key, getattr(settings, key, value) or value)

    social_links = SocialLink.objects.filter(is_active=True)
    return {
        "site_settings": site_settings,
        "social_links": social_links,
    }


def translation_context(request):
    current_language = get_language_from_request(request)
    return {
        "current_language": current_language,
        "available_languages": SUPPORTED_LANGUAGES.values(),
    }
