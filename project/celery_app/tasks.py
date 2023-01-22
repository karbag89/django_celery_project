from time import sleep
from celery import shared_task
from celery_project.settings import FILE_URL
from datetime import datetime
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from rest_framework.response import Response
from .serializers import ContactSerializer, \
                         UnprocessedContactsSerializer, \
                         FileMetadataSerializer
from .models import UnprocessedContacts
# from celery.utils.log import get_task_logger


def insert_file_metadata(file_metadata):
    serializer = FileMetadataSerializer(data=file_metadata)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def insert_contacts(contacts, model="UnprocessedContacts"):
    if model == "Contacts":
        serializer = ContactSerializer(data=contacts)
    else:
        serializer = UnprocessedContactsSerializer(data=contacts)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def delete_processed_contacts(contacts, created_date):
    UnprocessedContacts.objects.filter(created_date=created_date,
                                    phone_number=contacts["phone_number"], 
                                    email_address=contacts["email_address"]).delete()


def send_file(file_name, file_contacts):
    date_time = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    s3_file_name = f"{date_time}_{file_name}"
    default_storage.save(s3_file_name, file_contacts)
    return s3_file_name


def create_file_metadata(username, s3_file_name):
    s3_path = FILE_URL + s3_file_name
    user = User.objects.filter(username=username)
    file_metadata = {'username': user[0].id,
                        's3_path': s3_path,}
    insert_file_metadata(file_metadata)
    response = Response()
    response.data = {
        "message": "File metadata created!"
    }
    return response


def create_contact(contacts):
    try:
        insert_contacts(contacts, "Contacts")
        return True
    except:
        return False


def create_unprocessed_contact(contacts):
    insert_contacts(contacts, "UnprocessedContacts")


@shared_task()
def create_task(contacts, created_date, durartion):
    sleep(durartion)
    create_contact(contacts)
    delete_processed_contacts(contacts, created_date)
    return True
