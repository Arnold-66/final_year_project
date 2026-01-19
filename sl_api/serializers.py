# serializers.py - Updated with proper fields
from rest_framework import serializers
from .models import Sign

class SignSerializer(serializers.ModelSerializer):
    sigml_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Sign
        fields = ['id', 'word', 'sigml_file_url', 'category', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_sigml_file_url(self, obj):
        """Return the full URL to the sigml file"""
        request = self.context.get('request')
        if request and obj.sigml_file:
            return request.build_absolute_uri(obj.sigml_file.url)
        elif obj.sigml_file:
            # If no request context, return relative URL
            return obj.sigml_file.url
        return None

class SignDetailSerializer(serializers.ModelSerializer):
    sigml_file_url = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()

    class Meta:
        model = Sign
        fields = ['id', 'word', 'sigml_file_url', 'filename', 'category', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_sigml_file_url(self, obj):
        request = self.context.get('request')
        if request and obj.sigml_file:
            return request.build_absolute_uri(obj.sigml_file.url)
        elif obj.sigml_file:
            return obj.sigml_file.url
        return None

    def get_filename(self, obj):
        if obj.sigml_file:
            return obj.sigml_file.name.split('/')[-1]
        return None