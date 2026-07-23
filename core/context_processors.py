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
    "hero_badge": "Portal institucional",
    "hero_button_label": "Conheca mais",
    "hero_panel_title": "Pronto para comecar?",
    "hero_panel_item_1": "Informacoes sempre atualizadas",
    "hero_panel_item_2": "Canais oficiais em um so lugar",
    "hero_panel_item_3": "Atendimento mais proximo",
    "about_home_heading": "Sobre nos",
    "about_home_summary_title": "",
    "about_home_highlight": "",
    "about_home_paragraph_1": "",
    "about_home_paragraph_2": "",
    "about_home_image_url": "",
    "signup_button_label": "Inscreva-se",
    "signup_info_title": "Como participar",
    "signup_info_text": "",
    "signup_address_title": "Informacoes sobre os locais participantes",
    "signup_address_text": "",
    "news_eyebrow": "Noticias",
    "news_title": "Ultimas noticias",
    "news_button_label": "Ver todas",
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
