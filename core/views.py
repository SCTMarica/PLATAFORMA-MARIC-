import calendar
import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView

from .forms import (
    BannerForm,
    EmailOrUsernameAuthenticationForm,
    NewsArticleForm,
    SignupFormAdminForm,
    SiteSettingsForm,
    UserRegistrationForm,
    build_signup_submission_form,
)
from .i18n import LANGUAGE_SESSION_KEY, normalize_language
from .models import Event, MediaItem, NewsArticle, SignupForm, SignupSubmission, SiteSettings, User


def bind_form_sections(form, sections):
    bound_sections = []
    for section in sections:
        bound_sections.append(
            {
                **section,
                "bound_fields": [
                    {"field": form[item["name"]], "cols": item.get("cols", "col-12")}
                    for item in section["fields"]
                ],
            }
        )
    return bound_sections


def get_user_landing_url(user):
    if getattr(user, "can_access_admin", False):
        return reverse("core:admin-dashboard")
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
    weekday_labels = ["D", "S", "T", "Q", "Q", "S", "S"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hero_banners"] = MediaItem.objects.filter(
            media_type=MediaItem.MediaType.BANNER,
            is_active=True,
        )[:5]
        today = timezone.localdate()
        month_range = calendar.monthrange(today.year, today.month)
        month_start = timezone.make_aware(timezone.datetime(today.year, today.month, 1, 0, 0))
        month_end = timezone.make_aware(timezone.datetime(today.year, today.month, month_range[1], 23, 59, 59))
        month_events = Event.objects.published().filter(start_at__gte=month_start, start_at__lte=month_end)
        events_by_day = {}
        for event in month_events:
            events_by_day.setdefault(timezone.localtime(event.start_at).day, []).append(event)

        context["home_calendar_label"] = f"{self.month_names[today.month]} {today.year}"
        context["home_calendar_weekdays"] = self.weekday_labels
        context["home_calendar_weeks"] = [
            [
                {
                    "day": day,
                    "events": events_by_day.get(day, []),
                    "is_today": day == today.day,
                }
                for day in week
            ]
            for week in calendar.Calendar(firstweekday=6).monthdayscalendar(today.year, today.month)
        ]
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


class SignupView(SiteContextMixin, ListView):
    template_name = "core/signup.html"
    context_object_name = "signup_forms"

    def get_queryset(self):
        return SignupForm.objects.filter(is_active=True)


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
        messages.info(
            request,
            "O cadastro publico esta desativado. Solicite acesso ao administrador do sistema.",
        )
        return redirect("core:login")


class UserLogoutView(LogoutView):
    next_page = "core:login"
    http_method_names = ["get", "post", "head", "options"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "Sessao encerrada com sucesso.")
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

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Voce nao tem permissao para acessar o painel administrativo.",
            )
            return redirect("core:portal")
        return super().handle_no_permission()


class AdminFilterListMixin:
    paginate_by = 12
    search_param = "search"
    search_fields = ()

    def get_search_query(self):
        return self.request.GET.get(self.search_param, "").strip()

    def apply_search(self, queryset):
        query = self.get_search_query()
        if not query or not self.search_fields:
            return queryset

        condition = Q()
        for field in self.search_fields:
            condition |= Q(**{f"{field}__icontains": query})
        return queryset.filter(condition)

    def get_preserved_query_string(self, exclude=None):
        params = self.request.GET.copy()
        params.pop("page", None)
        if exclude:
            for key in exclude:
                params.pop(key, None)
        return params.urlencode()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.get_search_query()
        context["query_string"] = self.get_preserved_query_string()
        return context


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "core/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        six_months_ago = now - timedelta(days=180)

        news_counts = {
            row["month"].strftime("%Y-%m"): row["count"]
            for row in NewsArticle.objects.filter(created_at__gte=six_months_ago)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        }

        month_labels = []
        month_keys = []
        month_names_pt = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        cursor = six_months_ago.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        while cursor <= now:
            month_keys.append(cursor.strftime("%Y-%m"))
            month_labels.append(f"{month_names_pt[cursor.month]}/{cursor.year % 100:02d}")
            if cursor.month == 12:
                cursor = cursor.replace(year=cursor.year + 1, month=1)
            else:
                cursor = cursor.replace(month=cursor.month + 1)

        news_by_month = [
            {"month": label, "count": news_counts.get(key, 0)}
            for key, label in zip(month_keys, month_labels)
        ]

        context.update(
            {
                "stats": {
                    "news_total": NewsArticle.objects.count(),
                    "news_published": NewsArticle.objects.filter(is_published=True).count(),
                    "news_draft": NewsArticle.objects.filter(is_published=False).count(),
                    "events_total": Event.objects.count(),
                    "events_upcoming": Event.objects.published()
                    .filter(start_at__gte=now)
                    .count(),
                    "users_total": User.objects.filter(is_active=True).count(),
                    "signup_forms_active": SignupForm.objects.filter(is_active=True).count(),
                    "signup_submissions": SignupSubmission.objects.count(),
                    "banners_active": MediaItem.objects.filter(
                        media_type=MediaItem.MediaType.BANNER,
                        is_active=True,
                    ).count(),
                },
                "news_by_month_json": json.dumps(news_by_month),
                "recent_news": NewsArticle.objects.order_by("-created_at")[:5],
                "upcoming_events": Event.objects.published()
                .filter(start_at__gte=now)
                .order_by("start_at")[:5],
                "recent_submissions": SignupSubmission.objects.select_related("form").order_by(
                    "-created_at"
                )[:5],
            }
        )
        return context


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


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["admin_page_icon"] = "settings"
        context["form_sections"] = bind_form_sections(
            form,
            [
                {
                    "title": "Identidade",
                    "icon": "settings",
                    "fields": [
                        {"name": "site_name", "cols": "col-md-6"},
                        {"name": "logo_url", "cols": "col-md-6"},
                        {"name": "tagline", "cols": "col-12"},
                    ],
                },
                {
                    "title": "Pagina inicial",
                    "icon": "home",
                    "fields": [
                        {"name": "hero_title", "cols": "col-12"},
                        {"name": "hero_subtitle", "cols": "col-12"},
                    ],
                },
                {
                    "title": "Sobre",
                    "icon": "news",
                    "fields": [
                        {"name": "about_title", "cols": "col-12"},
                        {"name": "about_content", "cols": "col-12"},
                    ],
                },
                {
                    "title": "Contato",
                    "icon": "contact",
                    "fields": [
                        {"name": "contact_email", "cols": "col-md-6"},
                        {"name": "contact_phone", "cols": "col-md-6"},
                        {"name": "whatsapp", "cols": "col-md-6"},
                        {"name": "address", "cols": "col-md-6"},
                    ],
                },
                {
                    "title": "Aparencia e rodape",
                    "icon": "palette",
                    "fields": [
                        {"name": "primary_color", "cols": "col-md-4"},
                        {"name": "secondary_color", "cols": "col-md-4"},
                        {"name": "accent_color", "cols": "col-md-4"},
                        {"name": "footer_text", "cols": "col-12"},
                    ],
                },
            ],
        )
        return context


class AdminNewsListView(AdminRequiredMixin, AdminFilterListMixin, ListView):
    template_name = "core/admin_news_list.html"
    context_object_name = "items"
    search_fields = ("title", "summary", "slug")

    def get_queryset(self):
        queryset = NewsArticle.objects.order_by("-created_at")
        queryset = self.apply_search(queryset)

        status = self.request.GET.get("status", "").strip()
        if status == "published":
            queryset = queryset.filter(is_published=True)
        elif status == "draft":
            queryset = queryset.filter(is_published=False)

        featured = self.request.GET.get("featured", "").strip()
        if featured == "yes":
            queryset = queryset.filter(is_featured=True)
        elif featured == "no":
            queryset = queryset.filter(is_featured=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "").strip()
        context["featured_filter"] = self.request.GET.get("featured", "").strip()
        context["filters_active"] = bool(context["status_filter"] or context["featured_filter"])
        return context


class AdminNewsCreateView(AdminRequiredMixin, CreateView):
    template_name = "core/admin_form.html"
    form_class = NewsArticleForm
    model = NewsArticle

    def form_valid(self, form):
        messages.success(self.request, "Noticia cadastrada com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:admin-news-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["admin_title"] = "Cadastrar noticia"
        context["admin_description"] = "Publique uma noticia e escolha se ela aparece em destaque na pagina inicial."
        context["submit_label"] = "Salvar noticia"
        context["active_admin_tab"] = "news"
        context["admin_back_url"] = reverse("core:admin-news-list")
        context["admin_back_label"] = "Voltar para noticias"
        context["admin_page_icon"] = "news"
        context["form_sections"] = bind_form_sections(
            form,
            [
                {
                    "title": "Informacoes basicas",
                    "icon": "news",
                    "fields": [
                        {"name": "title", "cols": "col-md-8"},
                        {"name": "slug", "cols": "col-md-4"},
                    ],
                },
                {
                    "title": "Conteudo",
                    "icon": "news",
                    "fields": [
                        {"name": "summary", "cols": "col-12"},
                        {"name": "content", "cols": "col-12"},
                        {"name": "cover_image_url", "cols": "col-12"},
                    ],
                },
                {
                    "title": "Publicacao",
                    "icon": "shield",
                    "fields": [
                        {"name": "is_featured", "cols": "col-md-4"},
                        {"name": "is_published", "cols": "col-md-4"},
                        {"name": "published_at", "cols": "col-md-4"},
                    ],
                },
            ],
        )
        return context


class AdminBannerListView(AdminRequiredMixin, AdminFilterListMixin, ListView):
    template_name = "core/admin_banner_list.html"
    context_object_name = "items"
    search_fields = ("title", "description")

    def get_queryset(self):
        queryset = MediaItem.objects.filter(media_type=MediaItem.MediaType.BANNER).order_by(
            "sort_order", "-created_at"
        )
        queryset = self.apply_search(queryset)

        status = self.request.GET.get("status", "").strip()
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "").strip()
        context["filters_active"] = bool(context["status_filter"])
        return context


class AdminBannerCreateView(AdminRequiredMixin, CreateView):
    template_name = "core/admin_form.html"
    form_class = BannerForm
    model = MediaItem

    def form_valid(self, form):
        messages.success(self.request, "Imagem do carrossel cadastrada com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:admin-banner-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["admin_title"] = "Cadastrar imagem do carrossel"
        context["admin_description"] = "Adicione titulo, imagem e ordem de exibicao para o carrossel da pagina inicial."
        context["submit_label"] = "Salvar imagem"
        context["active_admin_tab"] = "banner"
        context["admin_back_url"] = reverse("core:admin-banner-list")
        context["admin_back_label"] = "Voltar para carrossel"
        context["admin_page_icon"] = "settings"
        context["form_sections"] = bind_form_sections(
            form,
            [
                {
                    "title": "Banner",
                    "icon": "image",
                    "fields": [
                        {"name": "title", "cols": "col-md-8"},
                        {"name": "sort_order", "cols": "col-md-4"},
                        {"name": "description", "cols": "col-12"},
                        {"name": "image_url", "cols": "col-12"},
                        {"name": "external_url", "cols": "col-12"},
                    ],
                },
                {
                    "title": "Visibilidade",
                    "icon": "shield",
                    "fields": [
                        {"name": "is_active", "cols": "col-md-6"},
                    ],
                },
            ],
        )
        return context


class AdminSignupFormListView(AdminRequiredMixin, AdminFilterListMixin, ListView):
    template_name = "core/admin_signup_form_list.html"
    context_object_name = "items"
    search_fields = ("title", "slug", "description")

    def get_queryset(self):
        queryset = SignupForm.objects.annotate(submission_count=Count("submissions")).order_by("-created_at")
        queryset = self.apply_search(queryset)

        status = self.request.GET.get("status", "").strip()
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "").strip()
        context["filters_active"] = bool(context["status_filter"])
        return context


class AdminSignupSubmissionListView(AdminRequiredMixin, AdminFilterListMixin, ListView):
    template_name = "core/admin_signup_submission_list.html"
    context_object_name = "items"
    search_fields = ("form__title", "form__slug")

    def get_queryset(self):
        queryset = SignupSubmission.objects.select_related("form").order_by("-created_at")
        queryset = self.apply_search(queryset)

        form_id = self.request.GET.get("form", "").strip()
        if form_id.isdigit():
            queryset = queryset.filter(form_id=int(form_id))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_filter"] = self.request.GET.get("form", "").strip()
        context["signup_forms"] = SignupForm.objects.order_by("title")
        context["filters_active"] = bool(context["form_filter"])
        return context


class AdminSignupFormCreateView(AdminRequiredMixin, CreateView):
    template_name = "core/admin_form.html"
    form_class = SignupFormAdminForm
    model = SignupForm

    def form_valid(self, form):
        messages.success(self.request, "Formulario de inscricao criado com sucesso.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("core:admin-signup-form-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["admin_title"] = "Criar formulario de inscricao"
        context["admin_description"] = "Defina os campos que o cliente devera preencher. Cada envio ficara salvo no banco."
        context["submit_label"] = "Salvar formulario"
        context["active_admin_tab"] = "forms"
        context["admin_back_url"] = reverse("core:admin-signup-form-list")
        context["admin_back_label"] = "Voltar para formularios"
        context["admin_page_icon"] = "forms"
        context["form_sections"] = bind_form_sections(
            form,
            [
                {
                    "title": "Informacoes",
                    "icon": "forms",
                    "fields": [
                        {"name": "title", "cols": "col-md-8"},
                        {"name": "slug", "cols": "col-md-4"},
                        {"name": "description", "cols": "col-12"},
                    ],
                },
                {
                    "title": "Campos do formulario",
                    "icon": "forms",
                    "fields": [
                        {"name": "fields_text", "cols": "col-12"},
                    ],
                },
                {
                    "title": "Status",
                    "icon": "shield",
                    "fields": [
                        {"name": "is_active", "cols": "col-md-6"},
                    ],
                },
            ],
        )
        return context


class SignupFormDetailView(FormView):
    template_name = "core/signup_form_detail.html"

    def dispatch(self, request, *args, **kwargs):
        self.signup_form = get_object_or_404(SignupForm, slug=kwargs["slug"], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return build_signup_submission_form(self.signup_form)

    def form_valid(self, form):
        SignupSubmission.objects.create(form=self.signup_form, data=form.cleaned_data)
        messages.success(self.request, "Inscricao enviada com sucesso.")
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
