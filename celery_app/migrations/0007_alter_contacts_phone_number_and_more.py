# Generated by Django 4.1.5 on 2023-01-19 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("celery_app", "0006_alter_contacts_email_address_alter_contacts_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contacts",
            name="phone_number",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="unprocessedcontacts",
            name="email_address",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="unprocessedcontacts",
            name="name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="unprocessedcontacts",
            name="phone_number",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
