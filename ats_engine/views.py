import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.conf import settings

from .serializers import AtsAnalyzeRequestSerializer
from .services.analyze import analyze_resume_against_jd, parse_file_to_text
from .models import ResumeAnalysis

CACHE_TTL_SECONDS = getattr(settings, "ATS_ENGINE_CACHE_TTL_SECONDS", 60 * 60)  # 1 hour

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

class AtsAnalyzeView(APIView):
    """Main endpoint.
    Heavy work can be moved to async tasks; this synchronous version is simplest to integrate.
    """
    def post(self, request):
        ser = AtsAnalyzeRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        jd_text = data["job_description"]
        target_role = data.get("target_role", "") or ""

        if data.get("resume_text"):
            resume_text = data["resume_text"]
        else:
            resume_text = parse_file_to_text(data["resume_file"])

        resume_hash = _sha256(resume_text)
        jd_hash = _sha256(jd_text)
        cache_key = f"ats:{resume_hash}:{jd_hash}:{target_role}"

        cached = cache.get(cache_key)
        if cached:
            return Response(cached, status=status.HTTP_200_OK)

        result = analyze_resume_against_jd(
            resume_text=resume_text,
            job_description=jd_text,
            target_role=target_role,
        )

        # Optional persistence
        if getattr(settings, "ATS_ENGINE_PERSIST_RESULTS", True):
            ResumeAnalysis.objects.create(
                target_role=target_role,
                ats_score=int(result["scores"]["ats_score"]),
                role_match_score=int(result["scores"]["role_match_score"]),
                keyword_coverage=float(result["scores"]["keyword_coverage"]),
                resume_hash=resume_hash,
                jd_hash=jd_hash,
                payload=result,
            )

        cache.set(cache_key, result, CACHE_TTL_SECONDS)
        return Response(result, status=status.HTTP_200_OK)
