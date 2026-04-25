from django.db import models
from django.conf import settings

class Biodata(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="biodatas",
        null=True,
        blank=True
    )
    
    language = models.CharField(max_length=50, default="English")
    
    # Store dynamic nested objects directly to give frontend full structural control
    birth_details = models.JSONField(default=dict, blank=True)
    personal_details = models.JSONField(default=dict, blank=True)
    family_details = models.JSONField(default=dict, blank=True)
    contact_details = models.JSONField(default=dict, blank=True)
    
    # Photography
    photo = models.ImageField(upload_to="biodata/photos/", blank=True, null=True)

    # Template Information
    template_id = models.CharField(max_length=50, blank=True, null=True)
    generated_pdf_key = models.CharField(max_length=255, blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Biodata for {self.user.username}"


class BiodataTemplate(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True, null=True) # E.g. "Modern", "Traditional"
    file = models.FileField(upload_to="biodata_templates/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="biodata_thumbnails/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BiodataTemplateSelection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="biodata_template_selections"
    )
    biodata = models.OneToOneField(Biodata, on_delete=models.CASCADE)
    template = models.ForeignKey(
        BiodataTemplate,
        on_delete=models.CASCADE,
        related_name="selected_by"
    )
    
    selected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} selected {self.template.name}"
