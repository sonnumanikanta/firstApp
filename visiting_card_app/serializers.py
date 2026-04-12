from rest_framework import serializers
from .models import VisitingCard, VisitingCardTemplate, VisitingCardTemplateSelection

class VisitingCardSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = VisitingCard
        fields = [
            'id', 'user', 'card_for', 'card_type', 'language',
            'full_name', 'designation', 'email', 'phone',
            'company_name', 'company_website', 'company_email', 'company_phone',
            'street', 'city', 'district', 'pincode',
            'slogan', 'logo', 'additional_fields',
            'template_id', 'generated_pdf_key',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        return VisitingCard.objects.create(**validated_data)

class VisitingCardTemplateSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = VisitingCardTemplate
        fields = ['id', 'name', 'thumbnail_url']

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail:
            url = obj.thumbnail.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

class VisitingCardTemplateSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitingCardTemplateSelection
        fields = ['id', 'visiting_card', 'template', 'selected_at']
