from django.core.cache import cache
from django.template import Template, Context

# def generate_resume_html(user,resume,template_id, template_html):
#     """
#     Generate resume HTML using user data and cache it in Redis
#     """

#     cache_key = f"resume_preview:user:{user.id}:template:{template_id}"

#     # Check Redis
#     cached_html = cache.get(cache_key)
#     if cached_html:
#         return cached_html

#     # Prepare context (USER DETAILS)
#     context = Context({
#         # Basic details
#         "full_name": user.full_name,
#         "email": user.email,
#         "phone": resume.phone if resume else "",
#         "summary": user.summary,

#         # Social links 
#         "linkedin": user.linkedin,
#         "github": user.github,

#         # Resume sections
#         "skills": user.skills.all(),
#         "experiences": user.experience_set.all(),
#         "education": user.education_set.all(),
#     })

#     html = Template(template_html).render(context)
#     cache.set(cache_key, html, timeout=600)

#     return html

def generate_resume_html(user, resume, template_id, template_html):


    if not template_html:
        return None
    data = {
        "full_name": resume.full_name or "",
        "email": resume.email or "",
        "phone": resume.phone or "",
        "summary": resume.summary or "",
        "linkedin": resume.linkedin or "",
        "github": resume.github or "",
        "skills": [s.name for s in resume.skills.all()],
        "experience": resume.experiences.all(),
        "education": resume.education.all(),
    }
    template = Template(template_html)
    rendered = template.render(Context(data))

    return rendered
