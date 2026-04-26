from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from rest_framework.permissions import IsAuthenticated, BasePermission,AllowAny
from rest_framework.views import APIView
import boto3
import os 
from django.conf import settings
from .models import Resume, Experience, Education, Skill,ResumeTemplate,ResumeTemplateSelection
from .serializers import ResumeSerializer, ExperienceSerializer, EducationSerializer, SkillSerializer
from django.core.cache import cache
from rest_framework.permissions import IsAdminUser
from .utils import generate_resume_html
from rest_framework.views import APIView
from .pdf_utilis import generate_pdf_from_html

from django.contrib.auth import get_user_model

User = get_user_model()
class CreateAdmin(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        if User.objects.filter(username="admin").exists():
            return Response({"status": "admin already exists"})

        User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="12345"
        )
        return Response({"status": "admin created"})
# Permissions: only allow owner to access their own objects
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'owner', None) == request.user


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    parser_classes = [MultiPartParser, FormParser,JSONParser]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Scope to the logged-in user's resumes
        # return Resume.objects.filter(owner=self.request.user).order_by('id')
            user = self.request.user
            cache_key = f"resume_list_user_{user.id}"

            resumes = cache.get(cache_key)
            if resumes is not None:
                return resumes

            resumes = Resume.objects.filter(owner=user).order_by('id')
            cache.set(cache_key, resumes, timeout=300)  # 5 minutes
            return resumes

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='ats-score')
    def ats_score(self, request, pk=None):
        """
        Calculate ATS score for a resume and persist it.
        """
        resume = self.get_object()

        jd = request.data.get('job_description', '')  # frontend sends JD text
        jd_keywords = set(k.strip().lower() for k in jd.split() if len(k.strip()) > 2)

        # Collect resume text corpus
        corpus = [
            resume.summary or '',
            resume.full_name or '',
            resume.email or '',
            resume.phone or '',
            resume.linkedin or '',
            resume.github or '',
        ]
        for exp in resume.experiences.all():
            corpus.extend([exp.job_title or '', exp.company or '', exp.description or ''])
        for edu in resume.education.all():
            corpus.extend([edu.degree or '', edu.institution or '', edu.description or ''])
        for skill in resume.skills.all():
            corpus.append(skill.name or '')

        corpus_text = ' '.join(corpus).lower()
        match_count = sum(1 for k in jd_keywords if k in corpus_text)
        keyword_score = min(100, int((match_count / max(1, len(jd_keywords))) * 70))  # up to 70%

        # Section completeness
        completeness = 0
        completeness += 20 if resume.summary else 0
        completeness += 25 if resume.experiences.exists() else 0
        completeness += 20 if resume.education.exists() else 0
        completeness += 10 if resume.linkedin else 0
        completeness += 5 if resume.github else 0
        completeness += 15 if resume.skills.exists() else 0
        completeness_score = min(100, completeness)

        # Formatting hints (simple)
        formatting_score = 10
        if resume.photo:
            formatting_score -= 5  # many ATS recommend without photo
        if not resume.address:
            formatting_score -= 2

        # Weighted final score (0–100)
        final_score = min(100, int(keyword_score + (completeness_score * 0.2) + formatting_score))
        resume.ats_score = final_score
        resume.save(update_fields=['ats_score'])

        return Response({'ats_score': final_score}, status=status.HTTP_200_OK)


class ExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Experience.objects.filter(resume__owner=self.request.user)

    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume_id')
        if not resume_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'resume_id': 'This field is required.'})

        try:
            resume = Resume.objects.get(id=resume_id, owner=self.request.user)
        except Resume.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Resume not found or you do not own it.')

        serializer.save(resume=resume)


class EducationViewSet(viewsets.ModelViewSet):
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Education.objects.filter(resume__owner=self.request.user)
    
    def perform_create(self, serializer):
        resume_id = self.request.data.get('resume_id')
        if not resume_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'resume_id': 'This field is required.'})

        try:
            resume = Resume.objects.get(id=resume_id, owner=self.request.user)
        except Resume.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Resume not found or you do not own it.')

        serializer.save(resume=resume)


class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    
    def get_queryset(self):
        return Skill.objects.filter(resume__owner=self.request.user).distinct()

    def create(self, request, *args, **kwargs):
        resume_id = request.data.get('resume_id')
        skills_data = request.data.get('skills', [])

        if not resume_id:
            return Response({"error": "resume_id required"}, status=400)

        try:
            resume = Resume.objects.get(id=resume_id, owner=request.user)
        except Resume.DoesNotExist:
            return Response({"error": "Resume not found"}, status=404)

        created_skills = []

        for skill_data in skills_data:
            name = skill_data.get("name")
            level = skill_data.get("level", "")  # ✅ optional

            if not name:
                continue

            # ✅ avoid duplicates
            if not resume.skills.filter(name=name).exists():
                skill = Skill.objects.create(
                    name=name,
                    level=level
                )
                resume.skills.add(skill)
                created_skills.append(name)

        return Response({
            "message": "Skills added successfully",
            "skills": created_skills
        }, status=201)
    # def get_queryset(self):
    #     # Skills attached to resumes owned by the user
    #     return Skill.objects.filter(resumes__owner=self.request.user).distinct()

    # def perform_create(self, serializer):
    #     resume_id = self.request.data.get('resume_id')
    #     if not resume_id:
    #         from rest_framework.exceptions import ValidationError
    #         raise ValidationError({'resume_id': 'This field is required.'})

    #     try:
    #         resume = Resume.objects.get(id=resume_id, owner=self.request.user)
    #     except Resume.DoesNotExist:
    #         from rest_framework.exceptions import PermissionDenied
    #         raise PermissionDenied('Resume not found or you do not own it.')

    #     skill = serializer.save()
    #     resume.skills.add(skill)
# class AdminResumeViewSet(viewsets.ModelViewSet):
#     queryset = AdminResume.objects.all()
#     serializer_class = AdminResumeSerializer
#     permission_classes = [IsAuthenticated, IsAdminUser]
#     parser_classes = [MultiPartParser, FormParser]        
# class ResumePreviewView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         previews = []

#         for template in AdminResume.objects.all():
#             template_html = template.resume_file.open().read().decode("utf-8")

#             rendered_html = generate_resume_html(
#                 user=user,
#                 template_id=template.id,
#                 template_html=template_html
#             )

#             previews.append({
#                 "template_id": template.id,
#                 "resume_preview": rendered_html
#             })

#         return Response(previews)
# def get_user_resume_data(user):
#     resume = Resume.objects.filter(owner=user).first()
#     if not resume:
#         return {}

#     return {
#         "full_name": resume.full_name,
#         "email": resume.email,
#         "phone": resume.phone,
#         "summary": resume.summary,
#         "linkedin": resume.linkedin,
#         "github": resume.github,
#         "skills": list(resume.skills.values_list("name", flat=True)),
#         "experience": list(resume.experiences.values(
#             "job_title", "company", "start_date", "end_date"
#         )),
#         "education": list(resume.education.values(
#             "degree", "institution", "start_year", "end_year"
#         )),
#     }
def get_user_resume_data(user,resume_id):
    from .models import Resume

    try:
            resume = Resume.objects.get(id=resume_id, owner=user)
    except Resume.DoesNotExist:
            return {

            "full_name": getattr(user, "full_name", "") or "",
            "email": user.email or "",
            "phone": "",
            "summary": "",
            "linkedin": "",
            "github": "",
            "skills": [],
            "experience": [],
            "education": [],
        }

    return {
        "full_name": resume.full_name or "",



        "email": resume.email or "",
        "phone": resume.phone or "",
        "summary": resume.summary or "",
        "linkedin": resume.linkedin or "",
        "github": resume.github or "",
        "skills": list(resume.skills.values_list("name", flat=True)),
        "experience": list(resume.experiences.values(
            "job_title", "company", "start_date", "end_date"
        )),
        "education": list(resume.education.values(
            "degree", "institution", "year_of_completion"
        )),
    }


class ResumePreviewListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")

        if not resume_id:
            return Response({"error": "resume_id required"}, status=400)

       
        user_data = get_user_resume_data(request.user,resume_id)
        templates = ResumeTemplate.objects.all()

        response = []
        for t in templates:
            response.append({
                "template_id": t.id,
                "template_name":  t.name,
                "thumbnail": t.file.url,
                "user_data": user_data
            })

        return Response(response)
class SelectTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        template_id = request.data.get("template_id")
        resume_id = request.data.get("resume_id")

        if not template_id or not resume_id:
            return Response(
                {"error": "template_id and resume_id required"},
                status=400
            )

        try:
            template = ResumeTemplate.objects.get(id=template_id)
            resume = Resume.objects.get(id=resume_id, owner=request.user)
        except ResumeTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=404)
        except Resume.DoesNotExist:
            return Response({"error": "Resume not found"}, status=404)

        obj, created = ResumeTemplateSelection.objects.update_or_create(
            user=request.user,
            resume=resume,
            defaults={"template": template}
        )

        return Response({"status": "Template selected"})
# class GenerateResumeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, resume_id):

#         # 1. Get resume
#         try:
#             resume = Resume.objects.get(id=resume_id, owner=request.user)
#         except Resume.DoesNotExist:
#             return Response({"error": "Resume not found"}, status=404)

#         # 2. Get selected template
#         try:
#             selection = ResumeTemplateSelection.objects.get(resume=resume)
#         except ResumeTemplateSelection.DoesNotExist:
#             return Response({"error": "Template not selected"}, status=400)

#         template = selection.template
#         file_ext = template.file.name.split(".")[-1].lower()
#         template_content=None
#         rendered = None
        
#         # 3. Read template HTML content
#         if file_ext == "html":
#                 template_content = template.file.read().decode("utf-8", errors="ignore")
#         # 4. Render resume HTML
#         rendered = generate_resume_html(
#             user=request.user,
#             resume=resume,
#             template_id=template.id,
#             template_html=template_content  
#         )

#         # 5. Return rendered result
#         return Response({
#                 "resume_id": resume.id,
#                 "template_id": template.id,
#                 "template_name": template.name,
#                 "template_file": template.file.url,
#                 "file_type": file_ext,
#                 "preview_html": rendered

#                     })



# class GenerateResumeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, resume_id):

#         # Get resume
#         try:
#             resume = Resume.objects.get(id=resume_id, owner=request.user)
#         except Resume.DoesNotExist:
#             return Response({"error": "Resume not found"}, status=404)

#         # Get selected template
#         try:
#             selection = ResumeTemplateSelection.objects.get(resume=resume)
#         except ResumeTemplateSelection.DoesNotExist:
#             return Response({"error": "Template not selected"}, status=400)

#         template = selection.template
#         file_ext = template.file.name.split(".")[-1].lower()

#         template_content = None
#         rendered = None
#         pdf_path = None

#         # Read HTML template
#         if file_ext == "html":
#             with template.file.open("rb") as f:
#                 template_content = f.read().decode("utf-8", errors="ignore")

#         # Generate HTML resume
#         if template_content:
#             rendered = generate_resume_html(
#                 user=request.user,
#                 resume=resume,
#                 template_id=template.id,
#                 template_html=template_content
#             )

#         # Generate PDF
#         if rendered:
#             pdf_path = generate_pdf_from_html(rendered)

#         # Connect to R2
#         client = boto3.client(
#             "s3",
#             endpoint_url=settings.AWS_S3_ENDPOINT_URL,
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#             region_name="auto"
#         )
#         if resume.generated_resume_key:
#             signed_url = client.generate_presigned_url(
#                 "get_object",
#                 Params={
#                 "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
#                 "Key": resume.generated_resume_key
#         },
#         ExpiresIn=3600
#     )

#             return Response({
#                 "resume_id": resume.id,
#                 "message": "Already generated",
#                 "download_url": signed_url
#         })

#         # Template download URL
#         file_key = template.file.name

#         signed_url = client.generate_presigned_url(
#             "get_object",
#             Params={
#                 "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
#                 "Key": file_key
#             },
#             ExpiresIn=3600
#         )

#         resume_url = None

#         # Upload generated resume
#         if pdf_path:
#             object_key = f"generated_resumes/user_{request.user.id}_resume_{resume.id}.pdf"

#             client.upload_file(
#                 pdf_path,
#                 settings.AWS_STORAGE_BUCKET_NAME,
#                 object_key
#             )

#             resume_url = client.generate_presigned_url(
#                 "get_object",
#                 Params={
#                     "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
#                     "Key": object_key
#                 },
#                 ExpiresIn=3600
#             )

#         return Response({
#             "resume_id": resume.id,
#             "template_id": template.id,
#             "template_name": template.name,
#             "template_download_url": signed_url,
#             "generated_resume_url": resume_url,
#             "file_type": file_ext,
#             "preview_html": rendered
#         })
class GenerateResumeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, resume_id):
        try:
            print("🔥 STEP 1: Start")
    
            # Resume
            resume = Resume.objects.get(id=resume_id, owner=request.user)
            print("✅ STEP 2: Resume fetched")
    
            # Template selection
            selection = ResumeTemplateSelection.objects.get(resume=resume)
            template = selection.template
            print("✅ STEP 3: Template fetched")
    
            # # R2 client
            # client = boto3.client(
            #     "s3",
            #     endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            #     region_name="auto"
            # )
    
            # Template URL fix
            template_url = request.build_absolute_uri(template.file.url)
            print("STEP 4 URL:", template_url)
            try:
                with template.file.open("rb") as f:
                    template_content = template.file.read().decode("utf-8")
                    print("STEP 5: Template read success, length:", len(template_content))
            except Exception as e:
                print("❌ TEMPLATE READ ERROR:", str(e))
                return Response({
                    "error": "Template read failed",
                    "details": str(e)
                })
                        

    
            # Generate HTML
            rendered = generate_resume_html(
                user=request.user,
                resume=resume,
                template_id=template.id,
                template_html=template_content
            )
            print("✅ STEP 5: HTML generated")
            pdf_url = generate_pdf_from_html(rendered)
            if not pdf_url:
                return Response({
                    "error": "PDF generation failed"
                }, status=500)
            # object_key = f"generated_resumes/user_{request.user.id}_resume_{resume.id}.pdf"

            # client = boto3.client(
            #     "s3",
            #     endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            #     region_name="auto"
            # )
            # client.upload_file(
            #     pdf_url,
            #     settings.AWS_STORAGE_BUCKET_NAME,
            #     object_key
            # ) 
            # resume.generated_resume_key = object_key
            # resume.save()
            # download_url = client.generate_presigned_url(
            #     "get_object",
            #     Params={
            #         "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            #         "Key": object_key
            #     },
            #     ExpiresIn=3600
            # )
            return Response({
                "message": "Resume generated successfully",
                "download_url": pdf_url
            })
        except Exception as e:
            print("❌ FINAL ERROR:", str(e))
            return Response({
                "error": str(e)
            }, status=500)
            
            
    # def get(self, request, resume_id):

    #     # 1. Get resume
    #     try:
    #         resume = Resume.objects.get(id=resume_id, owner=request.user)
    #     except Resume.DoesNotExist:
    #         return Response({"error": "Resume not found"}, status=404)

    #     # 2. Get selected template
    #     try:
    #         selection = ResumeTemplateSelection.objects.get(resume=resume)
    #     except ResumeTemplateSelection.DoesNotExist:
    #         return Response({"error": "Template not selected"}, status=400)

    #     template = selection.template
    #     file_ext = template.file.name.split(".")[-1].lower()

    #     # 3. Connect to R2
    #     client = boto3.client(
    #         "s3",
    #         endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         region_name="auto"
    #     )
    #     # print("DEBUG KEY BEFORE IF:", resume.generated_resume_key)
        
    #     if resume.generated_resume_key:
    #         signed_url = client.generate_presigned_url(
    #             "get_object",
    #             Params={
    #                 "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
    #                 "Key": resume.generated_resume_key
    #             },
    #             ExpiresIn=3600
    #         )

    #         return Response({
    #             "resume_id": resume.id,
    #             "message": "Already generated",
    #             "download_url": signed_url
    #         })

    #     # # 5. Generate HTML
    #     # template_content = None
    #     # rendered = None
    #     # pdf_path = None

    #     # if file_ext == "html":
    #     #     with template.file.open("rb") as f:
    #     #         template_content = f.read().decode("utf-8", errors="ignore")

    #     # if template_content:
    #     #     rendered = generate_resume_html(
    #     #         user=request.user,
    #     #         resume=resume,
    #     #         template_id=template.id,
    #     #         template_html=template_content
    #     #     )

    #     # # 6. Generate PDF
    #     # if rendered:
    #     #     print("RENDERED HTML:", rendered[:500])       
    #     #     try:
    #     #         pdf_path = generate_pdf_from_html(rendered)
    #     #     except Exception as e:
    #     #         print("PDF ERROR:", str(e))
    #     #         return Response({
    #     #             "error": "PDF generation failed",
    #     #             "details": str(e),
    #     #             "html_preview": rendered
    #     #         })
    #         template_content = None
    #         rendered = None
    #         pdf_path = None

    #         try:
    # # 🔥 LOAD TEMPLATE FROM URL (R2 SAFE)
    #             if file_ext == "html":
    #                 import requests
    #                 template_url = template.file.url
    #                 response = requests.get(template_url)
    #                 template_content = response.text

    # # HTML generation
    #             if template_content:
    #                 rendered = generate_resume_html(
    #                     user=request.user,
    #                     resume=resume,
    #                     template_id=template.id,
    #                     template_html=template_content
    #                 )
    #             print("RENDERED HTML:", rendered[:300] if rendered else "None")
    # # PDF generation
    #             if rendered:
    #                 pdf_path = generate_pdf_from_html(rendered)

    #         except Exception as e:
    #                 print("🔥 ERROR:", str(e))
    #                 return Response({
    #                     "error": "Generation failed",
    #                     "details": str(e)
    #                 })
    #     # 7. Upload to R2
    #     resume_url = None

    #     if pdf_path:
    #         object_key = f"generated_resumes/user_{request.user.id}_resume_{resume.id}.pdf"
    #         print("PDF PATH:",pdf_path)
    #         client.upload_file(
    #             pdf_path,
    #             settings.AWS_STORAGE_BUCKET_NAME,
    #             object_key,
                
    #         )

    #         # 🔥 SAVE KEY (VERY IMPORTANT)
    #         resume.generated_resume_key = object_key
    #         resume.save()
    #         # print("SAVED KEY:", resume.generated_resume_key)

    #         resume_url = client.generate_presigned_url(
    #             "get_object",
    #             Params={
    #                 "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
    #                 "Key": object_key
    #             },
    #             ExpiresIn=3600
    #         )
    #     if pdf_path and os.path.exists(pdf_path):    
    #         os.remove(pdf_path)
        # # 8. Template download URL
        # template_url = client.generate_presigned_url(
        #     "get_object",
        #     Params={
        #         "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
        #         "Key": template.file.name
        #     },
        #     ExpiresIn=3600
        # )

        # return Response({
        #     "resume_id": resume.id,
        #     "template_id": template.id,
        #     "template_name": template.name,
        #     "template_download_url": template_url,
        #     "generated_resume_url": resume_url,
        #     "file_type": file_ext,
        #     "preview_html": rendered
        # })
        
        
