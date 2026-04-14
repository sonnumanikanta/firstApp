from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitingCardViewSet,
    VisitingCardSaveView,
    VisitingCardTemplateListView,
    SelectVisitingCardTemplateView,
    GenerateVisitingCardView
)

router = DefaultRouter()
router.register(r'', VisitingCardViewSet, basename="visitingcard")

urlpatterns = [
    path('save/', VisitingCardSaveView.as_view(), name='visiting-card-save'),
    path('templates/', VisitingCardTemplateListView.as_view(), name='visiting-card-templates'),
    path('select-template/', SelectVisitingCardTemplateView.as_view(), name='visiting-card-select-template'),
    path('generate/<int:vc_id>/', GenerateVisitingCardView.as_view(), name='generate-visiting-card'),
    path('preview-data/<int:vc_id>/', VisitingCardPreviewDataView.as_view()),
    path('', include(router.urls)),
]
