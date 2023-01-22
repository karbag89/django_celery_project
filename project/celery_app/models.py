from django.conf import settings
from django.db import models


# Create your models here.
class Contacts(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    email_address = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField('created date')


class UnprocessedContacts(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    email_address = models.CharField(max_length=255, null=True, blank=True)
    created_date = models.DateTimeField('created date')


class FileMetadata(models.Model):
    username = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE)
    s3_path = models.CharField(max_length=255)
    created_date = models.DateTimeField('created date')
