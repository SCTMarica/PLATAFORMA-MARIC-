from django.db import migrations


def add_id_cadastro_field(apps, schema_editor):
    SignupForm = apps.get_model("core", "SignupForm")

    try:
        form = SignupForm.objects.get(slug="inscricao-cidadao")
    except SignupForm.DoesNotExist:
        
        return

    
    field_names = [f.get("name") for f in form.fields_schema]
    if "id_cadastro" in field_names:
        return

    form.fields_schema = form.fields_schema + [
        {
            "name": "id_cadastro",
            "label": "ID de Cadastro",
            "type": "text",
            "required": False,
        }
    ]
    form.save()


def remove_id_cadastro_field(apps, schema_editor):
    
    SignupForm = apps.get_model("core", "SignupForm")

    try:
        form = SignupForm.objects.get(slug="inscricao-cidadao")
    except SignupForm.DoesNotExist:
        return

    form.fields_schema = [
        f for f in form.fields_schema if f.get("name") != "id_cadastro"
    ]
    form.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_default_signup_form"),
    ]

    operations = [
        migrations.RunPython(
            add_id_cadastro_field,
            remove_id_cadastro_field,
        ),
    ]
