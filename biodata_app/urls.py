from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BiodataViewSet,
    BiodataSaveView,
    BiodataTemplateListView,
    SelectBiodataTemplateView,
    GenerateBiodataView,
    BiodataTemplatePreviewView
)

router = DefaultRouter()
router.register(r'', BiodataViewSet, basename="biodata")

urlpatterns = [
    path('save/', BiodataSaveView.as_view(), name='biodata-save'),
    path('templates/', BiodataTemplateListView.as_view(), name='biodata-templates'),
    path('select-template/', SelectBiodataTemplateView.as_view(), name='biodata-select-template'),
    path('template-previews/<int:bio_id>/', BiodataTemplatePreviewView.as_view()),
    path('generate/<int:bio_id>/', GenerateBiodataView.as_view(), name='generate-biodata'),
    path('', include(router.urls)),
]
