from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from rest_framework.permissions import IsAuthenticated, BasePermission

from .models import Resume, Experience, Education, Skill
from .serializers import ResumeSerializer, ExperienceSerializer, EducationSerializer, SkillSerializer


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
        return Resume.objects.filter(owner=self.request.user).order_by('id')

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
        # Skills attached to resumes owned by the user
        return Skill.objects.filter(resumes__owner=self.request.user).distinct()

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

        skill = serializer.save()
        resume.skills.add(skill)
