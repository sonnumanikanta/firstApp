"""Optional async integration.
If you already use Celery/RQ, you can move heavy analysis into a worker.

Example Celery task (pseudo):
- from celery import shared_task
- @shared_task
- def analyze_task(resume_text, jd_text, target_role=""):
-     return analyze_resume_against_jd(resume_text, jd_text, target_role)

We keep this file as a placeholder so your backend team knows where to put async code.
"""
