from django.urls import path

from .views import (
    AboutView,
    ContactView,
    EventDetailView,
    EventListView,
    HomeView,
    LinksView,
    LoginPlaceholderView,
    MediaView,
    NewsDetailView,
    NewsListView,
    PortalPlaceholderView,
    RegisterPlaceholderView,
    set_language,
)

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("sobre/", AboutView.as_view(), name="about"),
    path("noticias/", NewsListView.as_view(), name="news-list"),
    path("noticias/<slug:slug>/", NewsDetailView.as_view(), name="news-detail"),
    path("eventos/", EventListView.as_view(), name="event-list"),
    path("eventos/<slug:slug>/", EventDetailView.as_view(), name="event-detail"),
    path("midia/", MediaView.as_view(), name="media"),
    path("contato/", ContactView.as_view(), name="contact"),
    path("links/", LinksView.as_view(), name="links"),
    path("login/", LoginPlaceholderView.as_view(), name="login"),
    path("cadastro/", RegisterPlaceholderView.as_view(), name="register"),
    path("portal/", PortalPlaceholderView.as_view(), name="portal"),
    path("idioma/", set_language, name="set-language"),
]
