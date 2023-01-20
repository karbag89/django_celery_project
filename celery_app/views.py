import jwt
import datetime
import pandas as pd

from celery_project.settings import FILE_URL
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.views.generic.edit import FormView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed

from .models import Contacts, FileMetadata
from .serializers import UserSerializer, ContactSerializer, \
                         UnprocessedContactsSerializer, FileMetadataSerializer


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'user': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
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


def insert_contacts(contacts, model="UnprocessedContacts"):
    if model == "Contacts":
        serializer = ContactSerializer(data=contacts)
    else:
        serializer = UnprocessedContactsSerializer(data=contacts)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def insert_file_metadata(file_metadata):
    serializer = FileMetadataSerializer(data=file_metadata)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


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
            
            # Testing S3 uploading
            # TODO -> Need to create celery async 1-st job (upload file S3)
            date_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
            s3_file_name = f"{date_time}_{file_name}"
            s3_path = FILE_URL + s3_file_name
            default_storage.save(s3_file_name, file_contacts)

            user = User.objects.filter(username=username)
            file_metadata = {'username': user[0].id,
                             's3_path': s3_path,}
            insert_file_metadata(file_metadata) 

            for contact in contacts:
                # print("------------------------")
                # print(contact)
                # print("------------------------")
                # TODO -> Read from Contacts DB
                # contact_data = Contacts.objects.all()
                contact = {key.lower().replace(" ", "_"): value for key, value in contact.items()}
                # email_address = Contacts.objects.filter(phone_number=contact["email_address"]).latest('created_date')
                phone_number_exists = Contacts.objects.filter(phone_number=contact["phone_number"])
                email_address_exists = Contacts.objects.filter(phone_number=contact["email_address"])
                if phone_number_exists or email_address_exists:
                    # TODO -> Need to create celery async 2-nd job
                    insert_contacts(contact, "UnprocessedContacts")
                    continue
                # TODO -> Need to create celery async 3-th job
                insert_contacts(contact, "Contacts")
            response.data = {
                "message": "file uploaded!",
                "data": contacts
            }
        else:
            response.data = {
                'message': 'file not found!'
            }
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
            response.data = {"message": "You don't have any files uploaded."}
            return response

        for info in user_file_info:
            file_info.append(info)
        response.data = {"files": file_info}
        return response
