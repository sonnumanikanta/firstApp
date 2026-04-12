from django.contrib import admin
from .models import VisitingCard, VisitingCardTemplate, VisitingCardTemplateSelection

admin.site.register(VisitingCard)
admin.site.register(VisitingCardTemplate)
admin.site.register(VisitingCardTemplateSelection)