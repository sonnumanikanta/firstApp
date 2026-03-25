from django.urls import path
from .views import AtsAnalyzeView

urlpatterns = [
    path("analyze/", AtsAnalyzeView.as_view(), name="ats-analyze"),
]
