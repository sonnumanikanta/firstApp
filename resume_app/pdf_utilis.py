# from weasyprint import HTML
# import tempfile


# def generate_pdf_from_html(html_content):

#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

#     HTML(string=html_content).write_pdf(temp_file.name)

#     return temp_file.name

from xhtml2pdf import pisa
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import uuid
from io import BytesIO

def generate_pdf_from_html(html_content):
    file_name = f"{uuid.uuid4()}.pdf"

    pdf_buffer = BytesIO()

    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err:
        return None

    # save to R2 (not local temp folder)
    default_storage.save(file_name, ContentFile(pdf_buffer.getvalue()))

    # return URL instead of file path
    return default_storage.url(file_name)
