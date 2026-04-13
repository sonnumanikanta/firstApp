from django.db import models
from django.conf import settings

class VisitingCard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="visiting_cards",
        null=True,
        blank=True
    )
    
    # Card Configuration
    card_for = models.CharField(max_length=50, default="Individual")
    card_type = models.CharField(max_length=50, default="Single side")
    language = models.CharField(max_length=50, default="English")
    
    # Personal Details
    full_name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Company Details
    company_name = models.CharField(max_length=200, blank=True, null=True)
    company_website = models.URLField(blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    company_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Address Details
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    
    # Visuals
    slogan = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to="visiting_cards/logos/", blank=True, null=True)
    
    # Dynamic Form Array
    additional_fields = models.JSONField(default=list, blank=True)
    
    # Template Selection
    template_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Generated PDF
    generated_pdf_key = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

class VisitingCardTemplate(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="visiting_card_templates/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="visiting_card_thumbnails/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class VisitingCardTemplateSelection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="visiting_card_template_selections",
        null=True,
        blank=True

    )
    visiting_card = models.ForeignKey(VisitingCard, on_delete=models.CASCADE,)
    template = models.ForeignKey(
        VisitingCardTemplate,
        on_delete=models.CASCADE,
        related_name="selected_by"
    )
    
    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("visiting_card",)

    def __str__(self):
        return f"{self.user.username} selected {self.template.name}"
