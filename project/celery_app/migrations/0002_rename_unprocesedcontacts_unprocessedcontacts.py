# Generated by Django 4.1.5 on 2023-01-19 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("celery_app", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="UnprocesedContacts", new_name="UnprocessedContacts",
        ),
    ]
