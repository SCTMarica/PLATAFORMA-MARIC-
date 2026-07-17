import calendar
import logging
from datetime import date

import httpx
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView

logger = logging.getLogger(__name__)

from .forms import (
    BannerForm,
    ContactForm,
    EmailOrUsernameAuthenticationForm,
    InitialAdminRegistrationForm,
    NewsArticleForm,
    SignupFormAdminForm,
    SiteSettingsForm,
    StyledPasswordResetForm,
    StyledSetPasswordForm,
    UserRegistrationForm,
    build_signup_submission_form,
)
from .i18n import LANGUAGE_SESSION_KEY, normalize_language
from .models import Event, MediaItem, NewsArticle, SignupForm, SignupSubmission, SiteSettings, User


def get_user_landing_url(user):
    if getattr(user, "can_access_admin", False):
        return reverse("core:admin-panel")
    return reverse("core:portal")


def admin_users_exist():
    return User.objects.filter(is_active=True).filter(
        Q(is_staff=True) | Q(is_superuser=True) | Q(role__in=[User.Role.SUPERVISOR, User.Role.MASTER])
    ).exists()


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


class EventCalendarView(TemplateView):
    template_name = "core/event_calendar.html"
    month_names = [
        "",
        "Janeiro",
        "Fevereiro",
        "Marco",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    def get_month_date(self):
        today = timezone.localdate()
        try:
            year = int(self.request.GET.get("ano", today.year))
            month = int(self.request.GET.get("mes", today.month))
            return date(year, month, 1)
        except (TypeError, ValueError):
            return date(today.year, today.month, 1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_month = self.get_month_date()
        previous_month = date(current_month.year - 1, 12, 1) if current_month.month == 1 else date(current_month.year, current_month.month - 1, 1)
        next_month = date(current_month.year + 1, 1, 1) if current_month.month == 12 else date(current_month.year, current_month.month + 1, 1)
        month_range = calendar.monthrange(current_month.year, current_month.month)
        month_start = timezone.make_aware(timezone.datetime(current_month.year, current_month.month, 1, 0, 0))
        month_end = timezone.make_aware(
            timezone.datetime(current_month.year, current_month.month, month_range[1], 23, 59, 59)
        )
        events = Event.objects.published().filter(start_at__gte=month_start, start_at__lte=month_end)
        events_by_day = {}
        for event in events:
            events_by_day.setdefault(timezone.localtime(event.start_at).day, []).append(event)

        weeks = []
        for week in calendar.Calendar(firstweekday=6).monthdayscalendar(current_month.year, current_month.month):
            weeks.append(
                [
                    {
                        "day": day,
                        "date": date(current_month.year, current_month.month, day) if day else None,
                        "events": events_by_day.get(day, []),
                    }
                    for day in week
                ]
            )

        context.update(
            {
                "weeks": weeks,
                "current_month": current_month,
                "current_month_label": f"{self.month_names[current_month.month]} {current_month.year}",
                "previous_month": previous_month,
                "next_month": next_month,
                "weekday_labels": ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sab"],
                "month_events": events,
            }
        )
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["web3forms_key"] = settings.WEB3FORMS_KEY
        return context


class SignupView(SiteContextMixin, ListView):
    template_name = "core/signup.html"
    context_object_name = "signup_forms"

    def get_queryset(self):
        return SignupForm.objects.filter(is_active=True)


class LinksView(TemplateView):
    template_name = "core/links.html"


class FileUploadView(TemplateView):
    template_name = "core/file_upload.html"


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_create_initial_admin"] = not admin_users_exist()
        return context


class InitialAdminSetupView(FormView):
    template_name = "core/auth/initial_admin.html"
    form_class = InitialAdminRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if admin_users_exist():
            messages.info(request, "O administrador inicial ja foi configurado. Use a recuperacao de senha se precisar.")
            return redirect("core:login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Administrador inicial criado com sucesso.")
        return redirect("core:admin-panel")


class UserPasswordResetView(PasswordResetView):
    template_name = "core/auth/password_reset_form.html"
    form_class = StyledPasswordResetForm
    email_template_name = "core/auth/password_reset_email.txt"
    subject_template_name = "core/auth/password_reset_subject.txt"
    success_url = reverse_lazy("core:password-reset-done")
    from_email = settings.DEFAULT_FROM_EMAIL


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = "core/auth/password_reset_done.html"


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "core/auth/password_reset_confirm.html"
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy("core:password-reset-complete")


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "core/auth/password_reset_complete.html"


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


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "core:login"

    def test_func(self):
        return getattr(self.request.user, "can_access_admin", False)


class AdminPanelView(AdminRequiredMixin, UpdateView):
    template_name = "core/admin_panel.html"
    form_class = SiteSettingsForm
    model = SiteSettings

    def get_object(self, queryset=None):
        obj = SiteSettings.objects.order_by("id").first()
        if obj is None:
            obj = SiteSettings.objects.create(
                hero_title="Transforme sua presenca institucional em uma plataforma pronta para evoluir."
            )
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Conteudo do site atualizado com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:admin-panel")


class AdminNewsCreateView(AdminRequiredMixin, CreateView):
    template_name = "core/admin_form.html"
    form_class = NewsArticleForm
    model = NewsArticle

    def form_valid(self, form):
        messages.success(self.request, "Noticia cadastrada com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:admin-panel")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admin_title"] = "Cadastrar noticia"
        context["admin_description"] = "Publique uma noticia e escolha se ela aparece em destaque na pagina inicial."
        context["submit_label"] = "Salvar noticia"
        context["active_admin_tab"] = "news"
        return context


class AdminBannerCreateView(AdminRequiredMixin, CreateView):
    template_name = "core/admin_form.html"
    form_class = BannerForm
    model = MediaItem

    def form_valid(self, form):
        messages.success(self.request, "Imagem do carrossel cadastrada com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:admin-panel")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admin_title"] = "Cadastrar imagem do carrossel"
        context["admin_description"] = "Adicione titulo, imagem e ordem de exibicao para o carrossel da pagina inicial."
        context["submit_label"] = "Salvar imagem"
        context["active_admin_tab"] = "banner"
        return context


class AdminSignupFormCreateView(AdminRequiredMixin, CreateView):
    template_name = "core/admin_form.html"
    form_class = SignupFormAdminForm
    model = SignupForm

    def form_valid(self, form):
        messages.success(self.request, "Formulario de inscricao criado com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:admin-panel")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admin_title"] = "Criar formulario de inscricao"
        context["admin_description"] = "Defina os campos que o cliente devera preencher. Cada envio ficara salvo no banco."
        context["submit_label"] = "Salvar formulario"
        context["active_admin_tab"] = "forms"
        return context


class SignupFormDetailView(FormView):
    template_name = "core/signup_form_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.signup_form = get_object_or_404(SignupForm, slug=kwargs["slug"], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return build_signup_submission_form(self.signup_form)

    def post(self, request, *args, **kwargs):
        self.signup_form = get_object_or_404(SignupForm, slug=kwargs["slug"], is_active=True)
        
        cleaned_data = {}
        
        # Add all POST data to cleaned_data
        for key, value in request.POST.items():
            if key != "csrfmiddlewaretoken":
                cleaned_data[key] = value
                
        # Also capture uploaded file names (since we don't have a storage logic for this yet)
        for key, file_obj in request.FILES.items():
            cleaned_data[key] = file_obj.name

        import random
        import string
        from django.utils import timezone
        
        chars = string.ascii_uppercase + string.digits
        random_suffix = ''.join(random.choices(chars, k=5))
        generated_id = f"MARICA-{timezone.now().year}-{random_suffix}"
        cleaned_data["id_cadastro"] = generated_id
            
        SignupSubmission.objects.create(form=self.signup_form, data=cleaned_data)
        
        messages.success(self.request, f"Inscrição enviada com sucesso! Seu ID de Cadastro é: {generated_id}")
            
        return redirect("core:signup")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["signup_form"] = self.signup_form
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


class SearchView(SiteContextMixin, TemplateView):
    template_name = "core/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        context["query"] = q
        
        if q:
            context["news_results"] = NewsArticle.objects.published().filter(
                Q(title__icontains=q) | Q(summary__icontains=q) | Q(content__icontains=q)
            ).distinct()
            
            context["event_results"] = Event.objects.published().filter(
                Q(title__icontains=q) | Q(summary__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q)
            ).distinct()
            
            context["form_results"] = SignupForm.objects.filter(is_active=True).filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            ).distinct()
        else:
            context["news_results"] = []
            context["event_results"] = []
            context["form_results"] = []
            
        context["total_results"] = len(context["news_results"]) + len(context["event_results"]) + len(context["form_results"])
        return context
