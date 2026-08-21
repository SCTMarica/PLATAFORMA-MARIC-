from django import template
from django.utils.safestring import mark_safe

from core.content_safety import sanitize_news_content


register = template.Library()


@register.filter
def render_news_content(value):
    return mark_safe(sanitize_news_content(value))
