from rest_framework import serializers
from .models import Resume, Experience, Education, Skill


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            'id', 'resume', 'job_title', 'company', 'location',
            'start_date', 'end_date', 'description'
        ]
        extra_kwargs = {
            'resume': {'read_only': True}
        }


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'resume', 'degree', 'institution', 'year_of_completion',
            'score', 'location', 'description'
        ]
        extra_kwargs = {
            'resume': {'read_only': True}
        }


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'level']


class ResumeSerializer(serializers.ModelSerializer):
    experiences = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)   # nested skills
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Resume
        fields = [
            'id', 'owner',
            'full_name', 'email', 'phone', 'address',
            'linkedin', 'github', 'photo', 'summary',
            'template_type', 'ats_score', 'created_at',
            'experiences', 'education', 'skills'
        ]

    def create(self, validated_data):
        # owner will be injected in view from request.user
        return Resume.objects.create(**validated_data)
# class UploadedResumeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UploadedResume
#         fields = ["id", "resume_file", "uploaded_at"]
# from .models import AdminResume

# class AdminResumeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdminResume
#         fields = ["id", "resume_file"]  