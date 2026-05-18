from django.urls import path

from .views import (
    AboutView,
    AdminPanelView,
    ContactView,
    EventDetailView,
    EventListView,
    HomeView,
    LinksView,
    MediaView,
    NewsDetailView,
    NewsListView,
    PortalView,
    SignupView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
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
    path("inscreva-se/", SignupView.as_view(), name="signup"),
    path("links/", LinksView.as_view(), name="links"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("sair/", UserLogoutView.as_view(), name="logout"),
    path("cadastro/", UserRegisterView.as_view(), name="register"),
    path("portal/", PortalView.as_view(), name="portal"),
    path("painel-admin/", AdminPanelView.as_view(), name="admin-panel"),
    path("idioma/", set_language, name="set-language"),
]
