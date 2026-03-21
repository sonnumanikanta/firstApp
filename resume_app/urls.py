from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResumeViewSet, ExperienceViewSet, EducationViewSet, SkillViewSet

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename="resume")
router.register(r'experiences', ExperienceViewSet, basename="experience")
router.register(r'education', EducationViewSet, basename="education")
router.register(r'skills', SkillViewSet, basename="skill")

urlpatterns = [
    path('', include(router.urls)),   # expose directly at root
]