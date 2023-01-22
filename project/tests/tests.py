import pytest

from django.contrib.auth.models import User
from django.utils import timezone
from celery_app.models import Contacts, UnprocessedContacts


user_contacts = {'name': 'username',
                 'phone_number': '+374112233',
                 'email_address': 'username@username.com'}


@pytest.mark.django_db
def test_user_create():
    user = User.objects.create_user('username', 'username@username.com', 'password')
    assert User.objects.count() == 1
    assert user.username == 'username'
    assert user.email == 'username@username.com'


@pytest.mark.django_db
def test_an_admin_view(admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_contacts_create():
    contacts = Contacts.objects.create(name=user_contacts['name'],
                                       phone_number=user_contacts['phone_number'], 
                                       email_address=user_contacts['email_address'],
                                       created_date=timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert Contacts.objects.count() == 1
    assert contacts.name == user_contacts['name']
    assert contacts.phone_number == user_contacts['phone_number']
    assert contacts.email_address == user_contacts['email_address']


@pytest.mark.django_db
def test_unprocessed_contacts_create():
    unprocessed_contacts = UnprocessedContacts.objects.create(name=user_contacts['name'], 
                                                              phone_number=user_contacts['phone_number'], 
                                                              email_address=user_contacts['email_address'],
                                                              created_date=timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
    assert UnprocessedContacts.objects.count() == 1
    assert unprocessed_contacts.name == user_contacts['name']
    assert unprocessed_contacts.phone_number == user_contacts['phone_number']
    assert unprocessed_contacts.email_address == user_contacts['email_address']
