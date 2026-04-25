from django.contrib import admin
from .models import Biodata, BiodataTemplate, BiodataTemplateSelection

@admin.register(Biodata)
class BiodataAdmin(admin.ModelAdmin):
    list_display = ("user", "language", "template_id", "created_at")
    list_filter = ("language", "created_at")
    search_fields = ("user__email", "personal_details")

@admin.register(BiodataTemplate)
class BiodataTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_at")

@admin.register(BiodataTemplateSelection)
class BiodataTemplateSelectionAdmin(admin.ModelAdmin):
    list_display = ("user", "biodata", "template", "selected_at")

