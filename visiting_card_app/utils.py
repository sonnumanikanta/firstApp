from django.template import Template, Context
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from xhtml2pdf import pisa
from io import BytesIO
import uuid
import logging

logger = logging.getLogger(__name__)

def generate_visiting_card_html(user, vc, template_html):
    template = Template(template_html)
    context = Context({
        "user": user,
        "vc": vc,
    })
    return template.render(context)

# def generate_pdf_from_html(html_content):
#     file_name = f"visiting_cards/{uuid.uuid4()}.pdf"
#     pdf_buffer = BytesIO()

#     pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

#     if pisa_status.err:
#         logger.error(f"Failed to generate PDF: {pisa_status.err}")
#         return None

#     # default_storage.save(file_name, ContentFile(pdf_buffer.getvalue()))
#     # return default_storage.url(file_name)
def generate_pdf_from_html(html_content):
    file_name = f"visiting_cards/{uuid.uuid4()}.pdf"
    pdf_buffer = BytesIO()

    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err:
        return None

    # ✅ upload ONLY here to Cloudflare
    from storages.backends.s3boto3 import S3Boto3Storage
    cloud_storage = S3Boto3Storage()

    cloud_storage.save(file_name, ContentFile(pdf_buffer.getvalue()))
    return cloud_storage.url(file_name)