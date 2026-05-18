from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event, MediaItem, NewsArticle, SiteSettings, User


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

    def test_news_detail_loads(self):
        response = self.client.get(reverse("core:news-detail", args=["noticia-de-teste"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conteudo completo da noticia")

    def test_event_detail_loads(self):
        response = self.client.get(reverse("core:event-detail", args=["evento-de-teste"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Descricao do evento")

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

    def test_admin_login_redirects_to_admin(self):
        response = self.client.post(
            reverse("core:login"),
            {"username": "admin@example.com", "password": "SenhaSegura123!"},
        )

        self.assertRedirects(response, reverse("admin:index"))

    def test_portal_requires_authentication(self):
        response = self.client.get(reverse("core:portal"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("core:login"), response.url)
