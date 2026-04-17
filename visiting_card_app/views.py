import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView
from django.conf import settings

from .models import VisitingCard, VisitingCardTemplate, VisitingCardTemplateSelection
from .serializers import (
    VisitingCardSerializer,
    VisitingCardTemplateSerializer,
    VisitingCardTemplateSelectionSerializer
)
from .utils import generate_visiting_card_html, generate_pdf_from_html

logger = logging.getLogger(__name__)

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user', None) == request.user

# ==========================================
# Full Save - one API call saves everything
# POST /api/visiting-cards/save/
# ==========================================
class VisitingCardSaveView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        data = request.data
        vc_id = data.get("id")
        user = request.user
        
        # Prepare fields
        fields = [
            "card_for", "card_type", "language", "full_name", "designation",
            "email", "phone", "company_name", "company_website",
            "company_email", "company_phone", "street", "city",
            "district", "pincode", "slogan"
        ]
        
        vc_data = {field: data.get(field, "") for field in fields}
        
        # specific handling
        if "additional_fields" in data:
            import json
            try:
                # the form data might send json strings
                if isinstance(data["additional_fields"], str):
                    vc_data["additional_fields"] = json.loads(data["additional_fields"])
                else:
                    vc_data["additional_fields"] = data["additional_fields"]
            except Exception:
                pass
                
        if vc_id and vc_id != 'null':
            try:
                vc = VisitingCard.objects.get(id=vc_id, user=user)
                for key, value in vc_data.items():
                    if value is not None and value != "":
                        setattr(vc, key, value)
                if "logo" in request.FILES:
                    vc.logo = request.FILES["logo"]
                vc.save()
            except VisitingCard.DoesNotExist:
                return Response({"status": False, "message": "Visiting Card not found"}, status=404)
        else:
            vc = VisitingCard.objects.create(user=user, **vc_data)
            if "logo" in request.FILES:
                vc.logo = request.FILES["logo"]
                vc.save()

        serializer = VisitingCardSerializer(vc)
        return Response({
            "status": True,
            "message": "Visiting card saved successfully",
            "data": serializer.data
        }, status=200 if vc_id else 201)

# ==========================================
# CRUD ViewSet
# ==========================================
class VisitingCardViewSet(viewsets.ModelViewSet):
    serializer_class = VisitingCardSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return VisitingCard.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ==========================================
# Templates List
# GET /api/visiting-cards/templates/
# ==========================================
class VisitingCardTemplateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = VisitingCardTemplate.objects.all().order_by('id')
        serializer = VisitingCardTemplateSerializer(templates, many=True, context={'request': request})
        return Response({
            "status": True,
            "data": serializer.data
        })

# ==========================================
# Select Template
# POST /api/visiting-cards/select-template/
# ==========================================
class SelectVisitingCardTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        template_id = request.data.get("template_id")
        vc_id = request.data.get("visiting_card_id")

        if not template_id or not vc_id:
            return Response({"error": "template_id and visiting_card_id required"}, status=400)

        try:
            template = VisitingCardTemplate.objects.get(id=template_id)
            vc = VisitingCard.objects.get(id=vc_id, user=request.user)
        except VisitingCardTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=404)
        except VisitingCard.DoesNotExist:
            return Response({"error": "Visiting Card not found"}, status=404)

        obj, created = VisitingCardTemplateSelection.objects.update_or_create(
            visiting_card=vc,
            defaults={"user": request.user, "template": template}
        )

        vc.template_id = str(template_id)
        vc.save(update_fields=['template_id'])

        return Response({
            "status": True,
            "message": "Template selected successfully",
            "data": {
                "visiting_card_id": vc.id,
                "template_id": template.id,
                "template_name": template.name,
            }
        })

# ==========================================
# Generate PDF
# GET /api/visiting-cards/generate/{vc_id}/
# ==========================================
class VisitingCardPreviewDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vc = VisitingCard.objects.filter(user=request.user).order_by('-id').first()

        if not vc:
            return Response({"error": "No Visiting Card found"}, status=404)

        templates = VisitingCardTemplate.objects.all()

        preview_list = []

        for template in templates:
            preview_list.append({
                "template_id": template.id,
                "template_name": template.name,
                "user_data": {
                    "full_name": vc.full_name,
                    "designation": vc.designation,
                    "email": vc.email,
                    "phone": vc.phone,
                    "company_name": vc.company_name,
                    "city": vc.city,
                    "pincode": vc.pincode,
                    "slogan": vc.slogan
                }
            })

        return Response({
            "status": True,
            "data": preview_list
        })
class GenerateVisitingCardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vc_id):
        print("🔥 HELLO NEW DEPLOY - ENTERED GENERATE API")
        try:
            vc = VisitingCard.objects.get(id=vc_id, user=request.user)
        except VisitingCard.DoesNotExist:
            return Response({"error": "Visiting Card not found"}, status=404)
            
        if vc.generated_pdf_key:
            return Response({
                "status": True,
                "message": "Visiting Card already generated",
                "download_url": vc.generated_pdf_key
            })
            
        try:
            selection = VisitingCardTemplateSelection.objects.get(visiting_card=vc)
        except:
             return Response({"error": "No template selected."}, status=400)
             
        template = selection.template
        if not template.file:
            return Response({"error": "Template file missing"}, status=500)

        try:
            with template.file.open("rb") as f:
                template_content = f.read().decode("utf-8")
        except Exception as e:
            return Response({"error": f"Template read failed: {str(e)}"}, status=500)

        rendered = generate_visiting_card_html(
            user=request.user,
            vc=vc,
            template_html=template_content
        )

        pdf_url = generate_pdf_from_html(rendered)
        if not pdf_url:
            return Response({"error": "PDF generation failed"}, status=500)

        vc.generated_pdf_key = pdf_url
        vc.save(update_fields=['generated_pdf_key'])
        print("STEP 1: PDF URL GENERATED:", pdf_url)
        print("STEP 2: URL LENGTH:", len(pdf_url))
        
        try:
            vc.generated_pdf_key = pdf_url
            print("STEP 3: Assign success")
        
            vc.save(update_fields=['generated_pdf_key'])
            print("STEP 4: Save success")
        
        except Exception as e:
            print("ERROR DURING SAVE:", str(e))
            raise

        return Response({
            "status": True,
            "message": "Visiting Card generated successfully",
            "download_url": pdf_url
        })
        
