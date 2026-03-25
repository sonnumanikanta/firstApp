from rest_framework import serializers

class AtsAnalyzeRequestSerializer(serializers.Serializer):
    resume_file = serializers.FileField(required=False, allow_empty_file=False)
    resume_text = serializers.CharField(required=False, allow_blank=False, trim_whitespace=True)
    job_description = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)
    target_role = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)

    def validate(self, attrs):
        if not attrs.get("resume_file") and not attrs.get("resume_text"):
            raise serializers.ValidationError("Provide either resume_file or resume_text.")
        return attrs
