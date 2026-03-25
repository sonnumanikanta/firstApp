from django.test import TestCase
from .services.analyze import analyze_resume_against_jd

class AtsEngineTests(TestCase):
    def test_basic_analysis(self):
        resume = "John Doe\nEmail: john@example.com\nSkills: Python, SQL, Power BI\nExperience: Built dashboards and analyzed KPIs."
        jd = "We need a Data Analyst with strong SQL, Power BI and stakeholder communication."
        out = analyze_resume_against_jd(resume, jd, target_role="Data Analyst")
        self.assertIn("scores", out)
        self.assertIn("ats_score", out["scores"])
