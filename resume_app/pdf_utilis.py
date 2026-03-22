# from weasyprint import HTML
# import tempfile


# def generate_pdf_from_html(html_content):

#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

#     HTML(string=html_content).write_pdf(temp_file.name)

#     return temp_file.name
from xhtml2pdf import pisa
import os
import uuid

def generate_pdf_from_html(html_content):
    file_name = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join("temp", file_name)

    # create temp folder if not exists
    os.makedirs("temp", exist_ok=True)

    with open(file_path, "w+b") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

    if pisa_status.err:
        return None

    return file_path