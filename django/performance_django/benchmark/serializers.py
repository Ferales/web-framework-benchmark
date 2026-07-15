from rest_framework import serializers
from .models import User, FileModel
import base64


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FileModelSerializer(serializers.ModelSerializer):
    file_data = serializers.FileField()

    class Meta:
        model = FileModel
        fields = ['id', 'name', 'file_data']

    def create(self, validated_data):
        file_data = validated_data.pop('file_data')
        file_instance = FileModel.objects.create(
            file_data=file_data.read(),
            **validated_data
        )
        return file_instance
