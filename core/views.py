from django.views.generic import DetailView, ListView, TemplateView

from .models import Event, MediaItem, NewsArticle


class SiteContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_news"] = NewsArticle.objects.published()[:3]
        context["upcoming_events"] = Event.objects.published()[:3]
        return context


class HomeView(SiteContextMixin, TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hero_banners"] = MediaItem.objects.filter(
            media_type=MediaItem.MediaType.BANNER,
            is_active=True,
        )[:5]
        return context


class AboutView(SiteContextMixin, TemplateView):
    template_name = "core/about.html"


class NewsListView(ListView):
    template_name = "core/news_list.html"
    context_object_name = "news_list"
    paginate_by = 9

    def get_queryset(self):
        return NewsArticle.objects.published()


class NewsDetailView(DetailView):
    template_name = "core/news_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return NewsArticle.objects.published()


class EventListView(ListView):
    template_name = "core/event_list.html"
    context_object_name = "events"
    paginate_by = 9

    def get_queryset(self):
        return Event.objects.published()


class EventDetailView(DetailView):
    template_name = "core/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.published()


class MediaView(TemplateView):
    template_name = "core/media.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["videos"] = MediaItem.objects.filter(
            media_type=MediaItem.MediaType.VIDEO,
            is_active=True,
        )
        context["gallery_items"] = MediaItem.objects.filter(
            media_type=MediaItem.MediaType.GALLERY,
            is_active=True,
        )
        return context


class ContactView(TemplateView):
    template_name = "core/contact.html"


class LinksView(TemplateView):
    template_name = "core/links.html"


class LoginPlaceholderView(TemplateView):
    template_name = "core/auth/login.html"


class RegisterPlaceholderView(TemplateView):
    template_name = "core/auth/register.html"


class PortalPlaceholderView(TemplateView):
    template_name = "core/portal/index.html"
