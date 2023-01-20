from django.contrib import admin
from .models import Contacts, UnprocessedContacts, FileMetadata

# Register your models here.
admin.site.register(Contacts)
admin.site.register(UnprocessedContacts)
admin.site.register(FileMetadata)
