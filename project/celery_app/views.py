import jwt
import datetime
import pandas as pd

from celery.utils.log import get_logger
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

from celery_project.settings import WAITING_TIME
from .models import Contacts, UnprocessedContacts, FileMetadata
from .serializers import UserSerializer
from .tasks import (send_file, create_file_metadata,
                   create_contact, create_unprocessed_contact,
                   create_task, delete_processed_contacts)


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        username = request.data['username']
        response = Response()
        response.data = {"message": f"User with username '{username}' successfully registered."}
        return response


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None or not user.check_password(password):
            raise AuthenticationFailed(f"User credentials was incorrect!")

        payload = {
            'id': user.id,
            'user': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {"message": f"User successfully logged in."}
        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {"message": f"User successfully logged out."}
        return response


class JWTCheck(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthentication expired!')


class UploadFile(JWTCheck, FormView):
    def post(self, request):
        JWTCheck.get(self, request)
        file_contacts = request.FILES.get('file')
        response = Response()
        if file_contacts:
            token = request.COOKIES.get('jwt')
            payload = jwt.decode(token, options={"verify_signature": False})
            username = payload["user"]
            file_name = file_contacts

            df_contacts = pd.read_excel(file_contacts.file)
            contacts = df_contacts.where(pd.notnull(df_contacts), None)
            contacts = contacts.to_dict(orient='records')

            # Upload file to S3
            s3_file_name = send_file(file_name, file_contacts)
            # Add file metadata information to db
            create_file_metadata(username, s3_file_name)
            for contact in contacts:
                # TODO -> Read from Contacts DB
                contact = {key.lower().replace(" ", "_"): value for key, value in contact.items()}
                phone_number_exists = Contacts.objects.filter(phone_number=contact["phone_number"])
                email_address_exists = Contacts.objects.filter(phone_number=contact["email_address"])
                if phone_number_exists or email_address_exists:
                    create_unprocessed_contact(contact)
                    continue
                if not create_contact(contact):
                    message = f"Dear user '{username}' please check you input file data. Uploading failed."
                    return response
            message = f"Dear user '{username}' thank you for uploading contacts."
            unprocessed_contacts = list(UnprocessedContacts.objects.all().order_by('created_date'))
            if len(unprocessed_contacts) > 0:
                for unprocessed_contact in unprocessed_contacts:
                    unprocessed_contact_dict = {'name': unprocessed_contact.name, 
                                                'phone_number': unprocessed_contact.phone_number,
                                                'email_address': unprocessed_contact.email_address}
                    unprocessed_contact_date = unprocessed_contact.created_date

                    contacts = Contacts.objects.filter(phone_number=unprocessed_contact.phone_number, 
                                                    email_address=unprocessed_contact.email_address) \
                                                .order_by('-created_date').first()
                    contacts_created_date = contacts.created_date
                    time_delta = (unprocessed_contact_date - contacts_created_date).total_seconds()
                    if time_delta >= WAITING_TIME or time_delta < 0:
                        create_contact(unprocessed_contact_dict)
                        delete_processed_contacts(unprocessed_contact_dict, unprocessed_contact_date)
                    else:
                        logger = get_logger(__name__)
                        delay = time_delta
                        try:
                            task = create_task.apply_async((unprocessed_contact_dict, unprocessed_contact_date, delay), expires=1800, 
                                                            retry=True,retry_policy={
                                                                                'max_retries': 3,
                                                                                'interval_start': 0,
                                                                                'interval_step': 0.2,
                                                                                'interval_max': 0.2,
                                                                            })
                            task.wait(timeout=None, interval=0.5)
                        except create_task.OperationalError as exc:
                            logger.exception('Sending task raised: %r', exc)
            else:
                message = f"Dear user '{username}' thank you for uploading contacts."
        else:
            message = "File not found!"
        response.data = {"message": message}
        return response


class UserDataView(APIView):
    def get(self, request, username):
        JWTCheck.get(self, request)
        user = User.objects.filter(username=username).all()
        response = Response()
        if not len(user):
            response.data = {"message": "User not found."}
            return response
        user_file_info = FileMetadata.objects.filter(username=user[0].id).all().values('s3_path')
        file_info = []
        if not len(user_file_info):
            response.data = {"message": "You don't have any uploaded files."}
            return response

        for info in user_file_info:
            file_info.append(info)
        response.data = {"files": file_info}
        return response
