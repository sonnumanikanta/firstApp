from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Resume(models.Model):
    # Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")

    # Personal details
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    photo = models.ImageField(upload_to="resumes/", blank=True, null=True)
    resume_file = models.FileField(
        upload_to="uploaded_resumes/",
        blank=True,
        null=True
    )



    # Summary
    summary = models.TextField(blank=True, null=True)

    # Template & ATS
    template_type = models.CharField(max_length=50, blank=True, null=True)
    ats_score = models.IntegerField(blank=True, null=True)

    # Skills (Many-to-Many relation)
    skills = models.ManyToManyField("Skill", related_name="resumes", blank=True)

    # System
    created_at = models.DateTimeField(auto_now_add=True)
    generated_resume_key = models.CharField(max_length=255, blank=True, null=True)


    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.full_name} ({self.owner.username})"


class Skill(models.Model):
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=50, blank=True, null=True)  # Beginner, Intermediate, Expert

    def __str__(self):
        return self.name


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="experiences")
    job_title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="education")
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=150)
    year_of_completion = models.IntegerField(blank=True, null=True)
    score = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-year_of_completion']

    def __str__(self):
        return f"{self.degree} - {self.institution}"
class ResumeTemplate(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to="resume_templates/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

  
class ResumeTemplateSelection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="selected_template"
    )
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE) 

    template = models.ForeignKey(
        ResumeTemplate,
        on_delete=models.CASCADE,
        related_name="selected_by"
    )

    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("resume",)

    def __str__(self):
        return f"{self.user.username} selected {self.template.id}"

# class ResumeTemplateSelection(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="template_selections"
#     )
#     resume = models.ForeignKey(
#         Resume,
#         on_delete=models.CASCADE,
#         related_name="template_selections"
#     )
#     template = models.ForeignKey(
#         ResumeTemplate,
#         on_delete=models.CASCADE,
#         related_name="selections"
#     )

#     selected_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("user", "resume")  # one active template per resume

#     def __str__(self):
#         return f"{self.user.username} → {self.template.name}"

# class AdminResume(models.Model):
#     resume_file = models.FileField(upload_to="admin_resumes/")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Admin Resume {self.id}"    
# class ResumeTemplate(models.Model):
#     name = models.CharField(max_length=100)
#     file = models.FileField(upload_to ="resume_templates/")
#     thumbnail = models.ImageField(
#         upload_to="resume_thumbnails/",
#         blank=True,
#         null=True
#     )
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name      
