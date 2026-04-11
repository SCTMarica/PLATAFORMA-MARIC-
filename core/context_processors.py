from .models import SiteSettings, SocialLink


def site_branding(request):
    settings = SiteSettings.objects.order_by("id").first()
    social_links = SocialLink.objects.filter(is_active=True)
    return {
        "site_settings": settings,
        "social_links": social_links,
    }
