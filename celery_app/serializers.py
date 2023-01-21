from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from .models import Contacts, UnprocessedContacts, FileMetadata


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = ['id', 'name', 'phone_number', 'email_address']

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number', [])
        validated_data["created_date"] = datetime.now(tz=timezone.utc)
        instance = self.Meta.model(**validated_data)
        if phone_number is not None:
            instance.save()
        return instance


class UnprocessedContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnprocessedContacts
        fields = ['id', 'name', 'phone_number', 'email_address']

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number', [])
        validated_data["created_date"] = datetime.now(tz=timezone.utc)
        instance = self.Meta.model(**validated_data)
        if phone_number is not None:
            instance.save()
        return instance


class FileMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileMetadata
        fields = ['id', 'username', 's3_path']

    def create(self, validated_data):
        validated_data["created_date"] = datetime.now()
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
