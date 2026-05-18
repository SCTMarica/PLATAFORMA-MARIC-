from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .forms import EmailOrUsernameAuthenticationForm, UserRegistrationForm
from .i18n import LANGUAGE_SESSION_KEY, normalize_language
from .models import Event, MediaItem, NewsArticle, User


def get_user_landing_url(user):
    if getattr(user, "can_access_admin", False):
        return reverse("admin:index")
    return reverse("core:portal")


def sync_user_access_flags(user):
    updated_fields = []
    if user.role == User.Role.MASTER:
        if not user.is_staff:
            user.is_staff = True
            updated_fields.append("is_staff")
        if not user.is_superuser:
            user.is_superuser = True
            updated_fields.append("is_superuser")
    elif user.role == User.Role.SUPERVISOR and not user.is_staff:
        user.is_staff = True
        updated_fields.append("is_staff")

    if updated_fields:
        user.save(update_fields=updated_fields)


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


class UserLoginView(LoginView):
    template_name = "core/auth/login.html"
    authentication_form = EmailOrUsernameAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return get_user_landing_url(self.request.user)

    def form_valid(self, form):
        sync_user_access_flags(form.get_user())
        messages.success(self.request, "Acesso realizado com sucesso.")
        return super().form_valid(form)


class UserRegisterView(FormView):
    template_name = "core/auth/register.html"
    form_class = UserRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_user_landing_url(request.user))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Cadastro concluído. Seu acesso já está ativo.")
        return redirect(get_user_landing_url(user))


class UserLogoutView(LogoutView):
    next_page = "core:home"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "Sessão encerrada com sucesso.")
        return super().dispatch(request, *args, **kwargs)


class PortalView(LoginRequiredMixin, TemplateView):
    template_name = "core/portal/index.html"
    login_url = "core:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_role_label"] = self.request.user.get_role_display()
        return context


@require_POST
def set_language(request):
    language_code = normalize_language(request.POST.get("language"))
    request.session[LANGUAGE_SESSION_KEY] = language_code

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("core:home")
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("core:home")
    return redirect(next_url)
