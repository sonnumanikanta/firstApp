from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging
import os 
from django.conf import settings
from django.template.loader import render_to_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
logger = logging.getLogger(__name__)


def send_welcome_email(user_email: str, user_name: str):
    """
    Sends a formatted HTML welcome email to the user.
    """
    subject = "🎉 Welcome to Tempy!"

    # ✅ Load template from correct path
    html_content = render_to_string('emails/welcome_back.html', {'name': user_name})

    # ✅ Create email object with explicit sender
    # email = EmailMessage(
    #     subject=subject,
    #     body=html_content,
    #     from_email=settings.DEFAULT_FROM_EMAIL,
    #     to=[user_email]
    # )
    message = Mail(
    from_email=settings.DEFAULT_FROM_EMAIL,
    to_emails=user_email,
    subject=subject,
    html_content=html_content,
        )
    # email.content_subtype = "html"  # ensure HTML format

    try:
        email.send(fail_silently=False)
        logger.info("Welcome email sent to %s", user_email)
    except Exception as e:
        logger.error("Email send failed for %s: %s", user_email, e)


# def send_otp_email(user_email: str, user_name: str, otp_code: str):
#     """
#     Sends a formatted HTML OTP email for password reset.
#     """
#     subject = "🔐 Tempy Password Reset OTP"

#     # ✅ Load template from correct path
#     html_content = render_to_string(
#         'emails/password_reset_otp.html',
#         {'user_name': user_name, 'otp': otp_code}
#     )

#     # ✅ Create email object with explicit sender
#     email = EmailMessage(
#         subject=subject,
#         body=html_content,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[user_email]
#     )
#     email.content_subtype = "html"  # ensure HTML format

#     try:
#         email.send(fail_silently=False)
#         logger.info("OTP email sent to %s", user_email)
#     except Exception as e:
#         logger.error("OTP email send failed for %s: %s", user_email, e)
#         raise e
def send_otp_email(user_email: str, user_name: str, otp_code: str):
        """
        Sends a formatted HTML OTP email for password reset.
        """
    
        subject = "🔐 Tempy Password Reset OTP"
    
        # Load HTML template
        html_content = render_to_string(
            "emails/password_reset_otp.html",
            {"user_name": user_name, "otp": otp_code},
        )
    
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=user_email,
            subject=subject,
            html_content=html_content,
        )
        try:
            sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
            sg.send(message)
    
            logger.info("OTP email sent to %s", user_email)
    
        except Exception as e:
            print("SENDGRID ERROR:", str(e))
            logger.error("OTP email send failed for %s: %s", user_email, e)
            raise e
     







