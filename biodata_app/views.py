import json
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from rest_framework.views import APIView
from bs4 import BeautifulSoup
from django.conf import settings
import re
from visiting_card_app.utils import generate_pdf_from_html
from .models import Biodata, BiodataTemplate, BiodataTemplateSelection
from .serializers import BiodataSerializer, BiodataTemplateSerializer
from .util import generate_signed_url
from django.template import Template, Context

logger = logging.getLogger(__name__)

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user', None) == request.user

# ==========================================
# Full Save - atomic persistence
# POST /api/biodata/save/
# ==========================================
class BiodataSaveView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def normalize(self,data, expected):
        result = expected.copy()
        result.update(data or {})
        return result

    def post(self, request):
        data = request.data
        bio_id = data.get("id")
        user = request.user
        
        def _parse(val):
            if isinstance(val, str):
                try:
                    return json.loads(val)
                except:
                    return {}
            return val or {}
        EXPECTED_PERSONAL = {
                    "education": "",
                    "job_role": "",
                    "company_name": "",
                    "company_location": "",
                    "height": "",
                    "color": "",
                    "caste": "",
                    "star": "",
                    "additional_info": ""
                }

        EXPECTED_CONTACT = {
            "phone": "",
            "email": "",
            "address": ""
        }
        personal_raw = _parse(data.get("personalDetails") or data.get("personal_details"))
        contact_raw = _parse(data.get("contactDetails") or data.get("contact_details"))

        bio_data = {
            "language": data.get("language", "English"),
            "birth_details": _parse(data.get("birthDetails") or data.get("birth_details")),
            "personal_details": self.normalize(personal_raw, EXPECTED_PERSONAL),
            "family_details": _parse(data.get("familyDetails") or data.get("family_details")),
            "contact_details": self.normalize(contact_raw, EXPECTED_CONTACT),
        }
        # personal_raw = _parse(data.get("personalDetails") or data.get("personal_details"))
        # contact_raw = _parse(data.get("contactDetails") or data.get("contact_details"))

        # bio_data = {
        #     "language": data.get("language", "English"),
        #     "birth_details": _parse(data.get("birthDetails") or data.get("birth_details")),
        #     "personal_details": _parse(data.get("personalDetails") or data.get("personal_details")),
        #     "family_details": _parse(data.get("familyDetails") or data.get("family_details")),
        #     "contact_details": _parse(data.get("contactDetails") or data.get("contact_details")),
        # }
        
        if bio_id and bio_id != 'null':
            try:
                bio = Biodata.objects.get(id=bio_id, user=user)
                for key, value in bio_data.items():
                    setattr(bio, key, value)
                if "photo" in request.FILES:
                    bio.photo = request.FILES["photo"]
                bio.save()
            except Biodata.DoesNotExist:
                return Response({"status": False, "message": "Biodata not found"}, status=404)
        else:
            bio = Biodata.objects.create(user=user, **bio_data)
            if "photo" in request.FILES:
                bio.photo = request.FILES["photo"]
                bio.save()

        serializer = BiodataSerializer(bio)
        return Response({
            "status": True,
            "message": "Biodata saved successfully",
            "data": serializer.data
        }, status=200 if bio_id else 201)

# ==========================================
# CRUD ViewSet
# ==========================================
class BiodataViewSet(viewsets.ModelViewSet):
    serializer_class = BiodataSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Biodata.objects.filter(user=self.request.user).order_by('-created_at')

# ==========================================
# Templates and Generation logic
# ==========================================
class BiodataTemplateListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        templates = BiodataTemplate.objects.all().order_by('id')
        serializer = BiodataTemplateSerializer(templates, many=True, context={'request': request})
        return Response({"status": True, "data": serializer.data})

class SelectBiodataTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        template_id = request.data.get("template_id")
        bio_id = request.data.get("biodata_id")

        if not template_id or not bio_id:
            return Response({"error": "Missing parameters"}, status=400)

        template = BiodataTemplate.objects.get(id=template_id)
        bio = Biodata.objects.get(id=bio_id, user=request.user)

        BiodataTemplateSelection.objects.update_or_create(
            biodata=bio,
            defaults={"user": request.user, "template": template}
        )

        bio.template_id = str(template_id)
        bio.save(update_fields=['template_id'])

        return Response({"status": True, "message": "Template selected successfully", "data": {"biodata_id": bio.id, "template_id": template.id}})

class GenerateBiodataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, bio_id):
        bio = Biodata.objects.get(id=bio_id, user=request.user)

        # ✅ Fix key
        pdf_key = bio.generated_pdf_key
        if pdf_key:
            original_key = pdf_key 
            if pdf_key:
                if pdf_key.startswith("http"):
                    pdf_key = pdf_key.split(".com/")[-1]
            
                if pdf_key.startswith(settings.AWS_STORAGE_BUCKET_NAME + "/"):
                    pdf_key = pdf_key.replace(settings.AWS_STORAGE_BUCKET_NAME + "/", "")
                if pdf_key != original_key:
                    bio.generated_pdf_key = pdf_key
                    bio.save(update_fields=['generated_pdf_key'])    

    
        # ✅ Use corrected key
        if pdf_key:
            pdf_url = generate_signed_url(pdf_key)
            return Response({"status": True, "download_url": pdf_url})

        # ✅ Get template
        selection = BiodataTemplateSelection.objects.get(biodata=bio)
        template_content = selection.template.file.read().decode("utf-8")

        # ✅ Render HTML
        html = Template(template_content).render(
            Context({"user": request.user, "bio": bio})
        )

        # ✅ Generate PDF
        file_key = generate_pdf_from_html(html)

        if not file_key:
            return Response({"error": "Failed generating PDF"}, status=500)

        # ✅ Save key
        bio.generated_pdf_key = file_key
        bio.save(update_fields=['generated_pdf_key'])

        # ✅ Generate signed URL
        pdf_url = generate_signed_url(file_key)

        return Response({
            "status": True,
            "download_url": pdf_url
        })
class BiodataTemplatePreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, bio_id):
        try:
            bio = Biodata.objects.get(id=bio_id, user=request.user)
        except Biodata.DoesNotExist:
            return Response({"error": "Biodata not found"}, status=404)

        templates = BiodataTemplate.objects.all()

        preview_list = []

        for template in templates:
            if not template.file:
                continue

            try:
                template_content = template.file.read().decode("utf-8")
            except:
                continue

        
            html = Template(template_content).render(
                Context({
                    "user": request.user,
                    "bio": bio
                })
            )
            soup = BeautifulSoup(html, "html.parser")

            # remove title
            if soup.title:
                soup.title.decompose()

            text_preview = soup.get_text(separator="\n")

            lines = [line.strip() for line in text_preview.splitlines() if line.strip()]
            formatted_lines = []
            i = 0
            while i < len(lines):
                if i + 1 < len(lines) and lines[i].endswith(":"):
                    formatted_lines.append(f"{lines[i]} {lines[i+1]}")
                    i += 2
                else:
                    formatted_lines.append(lines[i])
                    i += 1

            clean_text = "\n".join(formatted_lines)

            

            preview_list.append({
                "template_id": template.id,
                "template_name": template.name,
                "preview_text": formatted_lines
            })

        return Response({
            "status": True,
            "data": preview_list
        })
