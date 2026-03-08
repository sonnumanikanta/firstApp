"""
URL configuration for tempy_backend project.
Includes routes for all apps and media file serving in development.
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # ✅ Auth routes
    path('auth/', include('auth_app.urls')),

    # ✅ EventForm routes
    path('eventform/', include('eventform_app.urls')),

    # ✅ Resume routes (CRUD + photo upload + ATS scoring)
    path('api/', include('resume_app.urls')),   # exposes /api/resumes/, /api/experiences/, /api/education/, /api/skills/

    # ✅ Other apps
    path('biodata/', include('biodata_app.urls')),
    path('invitations/', include('invitation_app.urls')),
    path('certificates/', include('certificate_app.urls')),
    path('visiting-cards/', include('visiting_card_app.urls')),
    path('funeral-notices/', include('funeral_app.urls')),
    path('business-documents/', include('businessdoc_app.urls')),
    path('socialcontent/', include('socialcontent_app.urls')),
    path('greetings/', include('greeting_app.urls')),
    path("admin/", admin.site.urls)
]

# ✅ Media files serving (for resume photo uploads in development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)