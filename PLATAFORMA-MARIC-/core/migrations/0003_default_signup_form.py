from django.db import migrations


def create_default_signup_form(apps, schema_editor):
    SignupForm = apps.get_model("core", "SignupForm")

    SignupForm.objects.get_or_create(
        slug="inscricao-cidadao",
        defaults={
            "title": "Inscrição Cidadão",
            "description": "Formulário padrão criado automaticamente",
            "is_active": True,
            "fields_schema": [
                {
                    "name": "nome",
                    "label": "Nome Completo",
                    "type": "text",
                    "required": True,
                },
                {
                    "name": "email",
                    "label": "E-mail",
                    "type": "email",
                    "required": True,
                },
                {
                    "name": "telefone",
                    "label": "Telefone",
                    "type": "text",
                    "required": False,
                },
            ],
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_signup_forms"),
    ]

    operations = [
        migrations.RunPython(
            create_default_signup_form,
            migrations.RunPython.noop
        ),
    ]
