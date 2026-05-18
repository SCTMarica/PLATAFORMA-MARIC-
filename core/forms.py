from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import SiteSettings

User = get_user_model()


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_classes} form-control".strip()


class EmailOrUsernameAuthenticationForm(StyledFormMixin, AuthenticationForm):
    username = forms.CharField(label="Email ou usuário")

    error_messages = {
        "invalid_login": "Informe um email/usuário e senha válidos.",
        "inactive": "Esta conta está inativa.",
    }

    def clean(self):
        login = self.cleaned_data.get("username", "").strip()
        password = self.cleaned_data.get("password")

        if login and password:
            username = login
            if "@" in login:
                matched_user = User.objects.filter(email__iexact=login).order_by("id").first()
                if matched_user:
                    username = matched_user.get_username()

            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserRegistrationForm(StyledFormMixin, forms.ModelForm):
    full_name = forms.CharField(label="Nome completo", max_length=150)
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "phone")
        labels = {
            "email": "Email",
            "phone": "Telefone",
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise ValidationError("Informe um email válido.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Já existe uma conta cadastrada com este email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data["full_name"].strip()
        name_parts = full_name.split(maxsplit=1)
        user.first_name = name_parts[0]
        user.last_name = name_parts[1] if len(name_parts) > 1 else ""
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.role = User.Role.CLIENT
        user.is_active = True
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user


class SiteSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            "site_name",
            "tagline",
            "hero_title",
            "hero_subtitle",
            "about_title",
            "about_content",
            "contact_email",
            "contact_phone",
            "whatsapp",
            "address",
            "logo_url",
            "primary_color",
            "secondary_color",
            "accent_color",
            "footer_text",
        )
        labels = {
            "site_name": "Nome do site",
            "tagline": "Descricao curta",
            "hero_title": "Titulo da pagina inicial",
            "hero_subtitle": "Subtitulo da pagina inicial",
            "about_title": "Titulo da pagina sobre",
            "about_content": "Conteudo da pagina sobre",
            "contact_email": "Email de contato",
            "contact_phone": "Telefone",
            "whatsapp": "WhatsApp",
            "address": "Endereco",
            "logo_url": "URL da logo",
            "primary_color": "Cor primaria",
            "secondary_color": "Cor secundaria",
            "accent_color": "Cor de destaque",
            "footer_text": "Texto do rodape",
        }
        widgets = {
            "tagline": forms.Textarea(attrs={"rows": 2}),
            "hero_subtitle": forms.Textarea(attrs={"rows": 3}),
            "about_content": forms.Textarea(attrs={"rows": 5}),
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
            "accent_color": forms.TextInput(attrs={"type": "color"}),
        }
