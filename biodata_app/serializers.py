from rest_framework import serializers
from .models import Biodata, BiodataTemplate, BiodataTemplateSelection

class BiodataSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Biodata
        fields = [
            'id', 'user', 'language', 'birth_details',
            'personal_details', 'family_details', 'contact_details',
            'photo', 'template_id', 'generated_pdf_key',
            'created_at', 'updated_at'
        ]

class BiodataTemplateSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = BiodataTemplate
        fields = ['id', 'name', 'category', 'thumbnail_url']

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            url = obj.thumbnail.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None
