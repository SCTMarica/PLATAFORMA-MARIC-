from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event, NewsArticle, SiteSettings


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteSettings.objects.create(
            hero_title="Transformando atendimento em presença digital",
            hero_subtitle="Base white-label pronta para personalização por instalação.",
        )
        NewsArticle.objects.create(
            title="Notícia de teste",
            slug="noticia-de-teste",
            summary="Resumo da notícia",
            content="Conteúdo completo da notícia",
        )
        Event.objects.create(
            title="Evento de teste",
            slug="evento-de-teste",
            summary="Resumo do evento",
            description="Descrição do evento",
            start_at=timezone.now() + timezone.timedelta(days=7),
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transformando atendimento")

    def test_news_detail_loads(self):
        response = self.client.get(reverse("core:news-detail", args=["noticia-de-teste"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conteúdo completo da notícia")

    def test_event_detail_loads(self):
        response = self.client.get(reverse("core:event-detail", args=["evento-de-teste"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Descrição do evento")
