import pytest

from django.contrib.auth.models import User


@pytest.mark.django_db
def test_user_create():
  User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
  assert User.objects.count() == 1


@pytest.mark.django_db
def test_an_admin_view(admin_client):
    response = admin_client.get('/admin/')
    print(response)
    assert response.status_code == 200
