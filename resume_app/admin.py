from django.contrib import admin
from .models import Resume, Experience, Education, Skill, ResumeTemplate


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "owner", "created_at")


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("id", "job_title", "company", "resume")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("id", "degree", "institution", "resume")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "level")


@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
