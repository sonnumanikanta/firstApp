from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResumeViewSet, ExperienceViewSet, EducationViewSet, SkillViewSet,ResumePreviewListView,SelectTemplateView,GenerateResumeView
from .views import CreateAdmin


router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename="resume")
router.register(r'experiences', ExperienceViewSet, basename="experience")
router.register(r'education', EducationViewSet, basename="education")
router.register(r'skills', SkillViewSet, basename="skill")




urlpatterns = [
    path("create-admin/", CreateAdmin.as_view()),
    path('resumes/preview/', ResumePreviewListView.as_view(), name='resume-preview'),
    path("select-template/", SelectTemplateView.as_view()),
    path("generate-resume/<int:resume_id>/", GenerateResumeView.as_view()),
    path('', include(router.urls)), 
    
      # expose directly at root
]

