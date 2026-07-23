from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core import mail

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
        self.assertNotContains(response, "Calendario de eventos")
        self.assertNotContains(response, "Abrir calendario completo")

    def test_news_detail_loads(self):
        response = self.client.get(reverse("core:news-detail", args=["noticia-de-teste"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conteudo completo da noticia")

    def test_event_detail_loads(self):
        response = self.client.get(reverse("core:event-detail", args=["evento-de-teste"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Descricao do evento")

    def test_event_list_links_to_calendar_inside_events_topic(self):
        response = self.client.get(reverse("core:event-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evento de teste")
        self.assertContains(response, reverse("core:event-calendar"))
        self.assertContains(response, "Calend")

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

    def test_registration_creates_authenticated_client_user(self):
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

        self.assertRedirects(response, reverse("core:portal"))
        user = User.objects.get(email="maria@example.com")
        self.assertEqual(user.role, User.Role.CLIENT)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_login_accepts_email_for_client_and_redirects_to_portal(self):
        response = self.client.post(
            reverse("core:login"),
            {"username": "cliente@example.com", "password": "SenhaSegura123!"},
        )

        self.assertRedirects(response, reverse("core:portal"))

    def test_admin_login_redirects_to_admin_panel(self):
        response = self.client.post(
            reverse("core:login"),
            {"username": "admin@example.com", "password": "SenhaSegura123!"},
        )

        self.assertRedirects(response, reverse("core:admin-panel"))

    def test_login_hides_initial_admin_button_when_admin_exists(self):
        response = self.client.get(reverse("core:login"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("core:initial-admin-setup"))
        self.assertContains(response, reverse("core:password-reset"))

    def test_initial_admin_setup_is_blocked_when_admin_exists(self):
        response = self.client.get(reverse("core:initial-admin-setup"))

        self.assertRedirects(response, reverse("core:login"))

    def test_portal_requires_authentication(self):
        response = self.client.get(reverse("core:portal"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("core:login"), response.url)

    def test_admin_panel_requires_admin_user(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse("core:admin-panel"))

        self.assertEqual(response.status_code, 403)

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

    def test_admin_panel_embeds_visual_home_preview(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("core:admin-panel"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prévia da página inicial")
        self.assertContains(response, f'{reverse("core:home")}?admin_preview=1')
        self.assertContains(response, 'data-admin-editor-section="general"')
        self.assertContains(response, 'data-admin-editor-section="colors"')
        self.assertContains(response, 'data-editor-panel="colors"')
        self.assertNotContains(response, 'id="admin-identity-section"')

        preview = self.client.get(reverse("core:home"), {"admin_preview": "1"})
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.headers["X-Frame-Options"], "SAMEORIGIN")
        self.assertContains(preview, 'data-editor-section="hero"')
        self.assertContains(preview, 'data-editor-section="footer"')

    def test_public_home_does_not_show_editor_controls(self):
        response = self.client.get(reverse("core:home"), {"admin_preview": "1"})
        self.assertNotContains(response, "preview-edit-button")

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
        self.assertRedirects(news_response, reverse("core:admin-panel"))
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
        self.assertRedirects(banner_response, reverse("core:admin-panel"))
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
        self.assertRedirects(form_response, reverse("core:admin-panel"))
        self.assertTrue(SignupForm.objects.filter(slug="oficina").exists())

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

    def test_password_reset_sends_email_for_existing_user(self):
        response = self.client.post(reverse("core:password-reset"), {"email": "admin@example.com"})

        self.assertRedirects(response, reverse("core:password-reset-done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("senha", mail.outbox[0].subject.lower())

    def test_password_reset_does_not_send_email_for_unknown_user(self):
        response = self.client.post(reverse("core:password-reset"), {"email": "naoexiste@example.com"})

        self.assertRedirects(response, reverse("core:password-reset-done"))
        self.assertEqual(len(mail.outbox), 0)


class InitialAdminSetupTests(TestCase):
    def test_login_shows_initial_admin_button_when_no_admin_exists(self):
        response = self.client.get(reverse("core:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("core:initial-admin-setup"))

    def test_initial_admin_setup_creates_master_user_and_logs_in(self):
        response = self.client.post(
            reverse("core:initial-admin-setup"),
            {
                "full_name": "Admin Inicial",
                "email": "admin.inicial@example.com",
                "phone": "21999999999",
                "password": "SenhaSegura123!",
                "confirm_password": "SenhaSegura123!",
            },
        )

        self.assertRedirects(response, reverse("core:admin-panel"))
        user = User.objects.get(email="admin.inicial@example.com")
        self.assertEqual(user.role, User.Role.MASTER)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_initial_admin_setup_blocks_after_first_admin_exists(self):
        User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="SenhaSegura123!",
            role=User.Role.MASTER,
        )

        response = self.client.post(
            reverse("core:initial-admin-setup"),
            {
                "full_name": "Outro Admin",
                "email": "outro@example.com",
                "phone": "21999999999",
                "password": "SenhaSegura123!",
                "confirm_password": "SenhaSegura123!",
            },
        )

        self.assertRedirects(response, reverse("core:login"))
        self.assertFalse(User.objects.filter(email="outro@example.com").exists())
