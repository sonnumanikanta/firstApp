from django.db import models

class ResumeAnalysis(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    target_role = models.CharField(max_length=120, blank=True, default="")
    ats_score = models.PositiveSmallIntegerField()
    role_match_score = models.PositiveSmallIntegerField()
    keyword_coverage = models.FloatField()
    resume_hash = models.CharField(max_length=64, db_index=True)
    jd_hash = models.CharField(max_length=64, db_index=True)
    payload = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["resume_hash", "jd_hash"]),
        ]
