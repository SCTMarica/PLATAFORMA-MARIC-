from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import MediaItem, NewsArticle, SignupForm, SiteSettings

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


class NewsArticleForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = NewsArticle
        fields = ("title", "slug", "summary", "content", "cover_image_url", "is_featured", "is_published", "published_at")
        labels = {
            "title": "Titulo",
            "slug": "Identificador da URL",
            "summary": "Resumo",
            "content": "Conteudo",
            "cover_image_url": "URL da imagem",
            "is_featured": "Destacar na pagina inicial",
            "is_published": "Publicado",
            "published_at": "Data de publicacao",
        }
        widgets = {
            "content": forms.Textarea(attrs={"rows": 6}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug") or slugify(self.cleaned_data.get("title", ""))
        if not slug:
            raise ValidationError("Informe um titulo ou identificador valido.")
        return slug


class BannerForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = ("title", "description", "image_url", "external_url", "sort_order", "is_active")
        labels = {
            "title": "Titulo",
            "description": "Descricao",
            "image_url": "URL da imagem",
            "external_url": "Link externo",
            "sort_order": "Ordem",
            "is_active": "Ativo",
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.media_type = MediaItem.MediaType.BANNER
        if commit:
            obj.save()
        return obj


class SignupFormAdminForm(StyledFormMixin, forms.ModelForm):
    fields_text = forms.CharField(
        label="Campos do formulario",
        widget=forms.Textarea(attrs={"rows": 7}),
        help_text="Use uma linha por campo: Rotulo|tipo|required. Tipos: text, email, phone, number, textarea.",
    )

    class Meta:
        model = SignupForm
        fields = ("title", "slug", "description", "fields_text", "is_active")
        labels = {
            "title": "Titulo",
            "slug": "Identificador da URL",
            "description": "Descricao",
            "is_active": "Ativo",
        }
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean_slug(self):
        slug = self.cleaned_data.get("slug") or slugify(self.cleaned_data.get("title", ""))
        if not slug:
            raise ValidationError("Informe um titulo ou identificador valido.")
        return slug

    def clean_fields_text(self):
        rows = [row.strip() for row in self.cleaned_data["fields_text"].splitlines() if row.strip()]
        schema = []
        allowed_types = {"text", "email", "phone", "number", "textarea"}
        for index, row in enumerate(rows, start=1):
            parts = [part.strip() for part in row.split("|")]
            label = parts[0] if parts else ""
            field_type = parts[1] if len(parts) > 1 and parts[1] else "text"
            required = len(parts) > 2 and parts[2].lower() in {"required", "obrigatorio", "sim", "true", "1"}
            if not label:
                raise ValidationError(f"Linha {index}: informe o rotulo do campo.")
            if field_type not in allowed_types:
                raise ValidationError(f"Linha {index}: tipo '{field_type}' nao e valido.")
            schema.append({"name": slugify(label).replace("-", "_"), "label": label, "type": field_type, "required": required})
        if not schema:
            raise ValidationError("Cadastre pelo menos um campo.")
        self.cleaned_schema = schema
        return self.cleaned_data["fields_text"]

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.fields_schema = self.cleaned_schema
        if commit:
            obj.save()
        return obj


def build_signup_submission_form(signup_form):
    fields = {}
    for item in signup_form.fields_schema:
        field_type = item.get("type", "text")
        required = bool(item.get("required"))
        label = item.get("label", item.get("name", "Campo"))
        name = item.get("name") or slugify(label).replace("-", "_")
        if field_type == "textarea":
            fields[name] = forms.CharField(label=label, required=required, widget=forms.Textarea(attrs={"rows": 4}))
        elif field_type == "email":
            fields[name] = forms.EmailField(label=label, required=required)
        elif field_type == "number":
            fields[name] = forms.FloatField(label=label, required=required)
        else:
            fields[name] = forms.CharField(label=label, required=required)

    return type("DynamicSignupSubmissionForm", (StyledFormMixin, forms.Form), fields)


class ContactForm(StyledFormMixin, forms.Form):
    name = forms.CharField(
        label="Nome",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Seu nome"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "voce@exemplo.com"}),
    )
    subject = forms.CharField(
        label="Assunto",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Como podemos ajudar?"}),
    )
    message = forms.CharField(
        label="Mensagem",
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "Escreva sua mensagem"}),
    )
