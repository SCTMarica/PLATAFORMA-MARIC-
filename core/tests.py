from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event, MediaItem, NewsArticle, SignupForm, SignupSubmission, SiteSettings, User


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create(
            hero_title="Transformando atendimento em presenca digital",
            hero_subtitle="Base white-label pronta para personalizacao por instalacao.",
        )
        NewsArticle.objects.create(
            title="Noticia de teste",
            slug="noticia-de-teste",
            summary="Resumo da noticia",
            content="Conteudo completo da noticia",
        )
        Event.objects.create(
            title="Evento de teste",
            slug="evento-de-teste",
            summary="Resumo do evento",
            description="Descricao do evento",
            start_at=timezone.now() + timezone.timedelta(days=7),
        )
        MediaItem.objects.create(
            title="Banner principal",
            media_type=MediaItem.MediaType.BANNER,
            description="Texto configuravel do banner",
            image_url="https://example.com/banner.jpg",
            external_url="https://example.com/detalhes",
            sort_order=1,
            is_active=True,
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transformando atendimento")
        self.assertContains(response, "homeCarousel")
        self.assertContains(response, "Banner principal")
        self.assertContains(response, "Calendario de eventos")
        self.assertContains(response, "Abrir calendario completo")

    def test_news_detail_loads(self):
        response = self.client.get(reverse("core:news-detail", args=["noticia-de-teste"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conteudo completo da noticia")

    def test_event_detail_loads(self):
        response = self.client.get(reverse("core:event-detail", args=["evento-de-teste"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Descricao do evento")

    def test_event_calendar_loads_month_events(self):
        event = Event.objects.get(slug="evento-de-teste")
        response = self.client.get(
            reverse("core:event-calendar"),
            {"ano": event.start_at.year, "mes": event.start_at.month},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Calendario de eventos")
        self.assertContains(response, "Evento de teste")

    def test_language_switcher_persists_selected_language(self):
        response = self.client.post(
            reverse("core:set-language"),
            {"language": "en", "next": reverse("core:home")},
        )
        self.assertRedirects(response, reverse("core:home"))
        self.assertEqual(self.client.session.get("site_language"), "en")

    def test_home_uses_selected_language_labels(self):
        session = self.client.session
        session["site_language"] = "es"
        session.save()

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear cuenta")
        self.assertContains(response, "Idioma")


class AuthenticationFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create(
            hero_title="Transformando atendimento em presenca digital",
            hero_subtitle="Base white-label pronta para personalizacao por instalacao.",
        )
        cls.client_user = User.objects.create_user(
            username="cliente",
            email="cliente@example.com",
            password="SenhaSegura123!",
            role=User.Role.CLIENT,
            first_name="Cliente",
        )
        cls.admin_user = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="SenhaSegura123!",
            role=User.Role.MASTER,
            first_name="Admin",
        )

    def test_registration_is_disabled_and_redirects_to_login(self):
        response = self.client.get(reverse("core:register"))

        self.assertRedirects(response, reverse("core:login"))
        self.assertFalse(User.objects.filter(email="maria@example.com").exists())

        response = self.client.post(
            reverse("core:register"),
            {
                "full_name": "Maria Silva",
                "email": "maria@example.com",
                "phone": "21999999999",
                "password": "SenhaSegura123!",
                "confirm_password": "SenhaSegura123!",
            },
        )

        self.assertRedirects(response, reverse("core:login"))
        self.assertFalse(User.objects.filter(email="maria@example.com").exists())

    def test_login_accepts_email_for_client_and_redirects_to_portal(self):
        response = self.client.post(
            reverse("core:login"),
            {"username": "cliente@example.com", "password": "SenhaSegura123!"},
        )

        self.assertRedirects(response, reverse("core:portal"))

    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post(
            reverse("core:login"),
            {"username": "admin@example.com", "password": "SenhaSegura123!"},
        )

        self.assertRedirects(response, reverse("core:admin-dashboard"))

    def test_portal_requires_authentication(self):
        response = self.client.get(reverse("core:portal"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("core:login"), response.url)

    def test_admin_dashboard_requires_admin_user(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse("core:admin-dashboard"))

        self.assertRedirects(response, reverse("core:portal"))

    def test_admin_panel_requires_admin_user(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse("core:admin-panel"))

        self.assertRedirects(response, reverse("core:portal"))

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.client_user)

        response = self.client.post(reverse("core:logout"))

        self.assertRedirects(response, reverse("core:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_panel_updates_site_settings(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("core:admin-panel"),
            {
                "site_name": "Novo Portal",
                "tagline": "Tagline atualizada",
                "hero_title": "Titulo atualizado",
                "hero_subtitle": "Subtitulo atualizado",
                "about_title": "Sobre atualizado",
                "about_content": "Conteudo atualizado",
                "contact_email": "novo@example.com",
                "contact_phone": "(21) 1111-2222",
                "whatsapp": "(21) 99999-0000",
                "address": "Rua atualizada",
                "logo_url": "",
                "primary_color": "#bc202e",
                "secondary_color": "#0b132b",
                "accent_color": "#f59e0b",
                "footer_text": "Rodape atualizado",
            },
        )

        self.assertRedirects(response, reverse("core:admin-panel"))
        settings = SiteSettings.objects.order_by("id").first()
        self.assertEqual(settings.site_name, "Novo Portal")
        self.assertEqual(settings.hero_title, "Titulo atualizado")

    def test_admin_can_create_news_banner_and_signup_form(self):
        self.client.force_login(self.admin_user)

        news_response = self.client.post(
            reverse("core:admin-news-create"),
            {
                "title": "Nova noticia",
                "slug": "nova-noticia",
                "summary": "Resumo",
                "content": "Conteudo",
                "cover_image_url": "",
                "is_featured": "on",
                "is_published": "on",
                "published_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            },
        )
        self.assertRedirects(news_response, reverse("core:admin-news-list"))
        self.assertTrue(NewsArticle.objects.filter(slug="nova-noticia").exists())

        banner_response = self.client.post(
            reverse("core:admin-banner-create"),
            {
                "title": "Banner novo",
                "description": "Descricao",
                "image_url": "https://example.com/banner.jpg",
                "external_url": "",
                "sort_order": 2,
                "is_active": "on",
            },
        )
        self.assertRedirects(banner_response, reverse("core:admin-banner-list"))
        self.assertTrue(MediaItem.objects.filter(title="Banner novo", media_type=MediaItem.MediaType.BANNER).exists())

        form_response = self.client.post(
            reverse("core:admin-signup-form-create"),
            {
                "title": "Oficina",
                "slug": "oficina",
                "description": "Inscricao da oficina",
                "fields_text": "Nome completo|text|required\nEmail|email|required\nIdade|number",
                "is_active": "on",
            },
        )
        self.assertRedirects(form_response, reverse("core:admin-signup-form-list"))
        self.assertTrue(SignupForm.objects.filter(slug="oficina").exists())

    def test_admin_list_pages_require_admin_user(self):
        self.client.force_login(self.client_user)

        for url_name in (
            "core:admin-news-list",
            "core:admin-banner-list",
            "core:admin-signup-form-list",
            "core:admin-signup-submission-list",
        ):
            response = self.client.get(reverse(url_name))
            self.assertRedirects(response, reverse("core:portal"))

    def test_admin_news_list_supports_search_and_filters(self):
        NewsArticle.objects.create(
            title="Noticia publicada",
            slug="noticia-publicada",
            summary="Resumo",
            content="Conteudo",
            is_published=True,
        )
        NewsArticle.objects.create(
            title="Rascunho interno",
            slug="rascunho-interno",
            summary="Resumo",
            content="Conteudo",
            is_published=False,
        )

        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("core:admin-news-list"), {"search": "Rascunho", "status": "draft"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rascunho interno")
        self.assertNotContains(response, "Noticia publicada")

    def test_signup_form_submission_is_saved(self):
        signup_form = SignupForm.objects.create(
            title="Curso livre",
            slug="curso-livre",
            fields_schema=[
                {"name": "nome", "label": "Nome", "type": "text", "required": True},
                {"name": "email", "label": "Email", "type": "email", "required": True},
            ],
        )

        response = self.client.post(
            reverse("core:signup-form-detail", args=[signup_form.slug]),
            {"nome": "Ana", "email": "ana@example.com"},
        )

        self.assertRedirects(response, reverse("core:signup"))
        submission = SignupSubmission.objects.get(form=signup_form)
        self.assertEqual(submission.data["nome"], "Ana")
