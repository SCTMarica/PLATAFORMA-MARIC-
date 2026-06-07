from django import template

from core.i18n import get_language_from_request, translate

register = template.Library()


@register.simple_tag(takes_context=True)
def tr(context, key):
    request = context.get("request")
    language_code = context.get("current_language") or get_language_from_request(request)
    return translate(key, language_code)
