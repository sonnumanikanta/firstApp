import logging
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.utils import timezone
import random, datetime
from .response_utils import success_response, error_response
from rest_framework.permissions import AllowAny

from .a_serializers import (
    SignupSerializer,
    ForgetPasswordSerializer,
    ResetPasswordSerializer,
    # EventFormSerializer,
)
from .models import User, PasswordResetOTP,SignupOTP
# from eventform_app.models import EventForm
from .email_utils import send_welcome_email, send_otp_email

logger = logging.getLogger(__name__)


def home(request):
    return HttpResponse("WELCOME TO THE TEMPY BACKEND")


# class SignupView(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         serializer = SignupSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         user = serializer.save()
#         try:
#             send_welcome_email(user.email, user.username)
#         except Exception as e:
#             print("Signup email send failed:", e)

#         return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
# class SignupView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         full_name = request.data.get("full_name")
#         email = request.data.get("email")

#         if not full_name or not email:
#             return Response(
#                 {"error": "Full name and email are required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if User.objects.filter(email=email).exists():
#             return Response(
#                 {"error": "Email already registered"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         return Response(
#             {
#                 "message": "Basic details accepted",
#                 "full_name": full_name,
#                 "email": email
#             },
#             status=status.HTTP_200_OK
#         )
# class SignupView(APIView):
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         full_name = request.data.get("full_name")
#         email = request.data.get("email")
#         otp = request.data.get("otp")
#         password = request.data.get("password")
#         # email = request.data.get("email")

#         if User.objects.filter(email=email).exists():
#             return Response(
#                 {"error": "Email already registered"},
#                 status=status.HTTP_400_BAD_REQUEST
#     )

#         # ================= PAGE 1 =================
#         # full_name + email → send OTP
#         if full_name and email and not otp and not password:

#             if User.objects.filter(email=email).exists():
#                 return Response(
#                     {"error": "Email already registered"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             otp_code = str(random.randint(100000, 999999))
#             expiry = timezone.now() + datetime.timedelta(minutes=5)

#             signup_otp = SignupOTP.objects.create(
#                 email=email,
#                 otp_code=otp_code,
#                 expiry_time=expiry
#             )

#             send_otp_email(email, full_name, otp_code)

#             return Response(
#                 {
#                     "message": "OTP sent",
#                     "signup_id": str(signup_otp.signup_id)  # hidden from user
#                 },
#                 status=status.HTTP_200_OK
#             )

#         # ================= PAGE 2 =================
#         # signup_id + otp + password → create user
#         signup_id = request.data.get("signup_id")

#         if signup_id and otp and password:

#             otp_obj = SignupOTP.objects.filter(
#                 signup_id=signup_id,
#                 otp_code=otp,
#                 is_verified=False,
#                 expiry_time__gte=timezone.now()
#             ).first()

#             if not otp_obj:
#                 return Response(
#                     {"error": "Invalid or expired OTP"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             user = User.objects.create(
#                 username=otp_obj.email.split("@")[0],
#                 email=otp_obj.email,
#                 password=make_password(password)
#             )

#             otp_obj.is_verified = True
#             otp_obj.save()

#             send_welcome_email(user.email, user.username)

#             return Response(
#                 {"message": "Signup successful"},
#                 status=status.HTTP_201_CREATED
#             )

#         return Response(
#             {"error": "Invalid signup request"},
#             status=status.HTTP_400_BAD_REQUEST
#         )
class SignupRequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        full_name = request.data.get("full_name")
        email = request.data.get("email")

        if not full_name or not email:
            return error_response("Full name & email required")

        if User.objects.filter(email=email).exists():
            return error_response("Email already registered")

        otp = str(random.randint(100000, 999999))

        obj = SignupOTP.objects.create(
            full_name=full_name,
            email=email,
            otp_code=otp,
            expiry_time=timezone.now() + datetime.timedelta(minutes=5)
        )

        try:
            send_otp_email(email, full_name, otp)
        except Exception as e:
            logger.error(f"OTP email send failed: {e}")
            obj.delete()  # remove unused OTP record

            return error_response("Failed to send OTP email", 500)

        return success_response(
            "OTP sent",
            {"signup_id": str(obj.signup_id)}
        )

# class SignupRequestOTPView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         full_name = request.data.get("full_name")
#         email = request.data.get("email")

#         if not full_name or not email:
#             return Response({"error": "Full name & email required"}, status=400)

#         if User.objects.filter(email=email).exists():
#             # return Response({"error": "Email already registered"}, status=400)
#             return error_response("Email already registered")

#         otp = str(random.randint(100000, 999999))

#         obj = SignupOTP.objects.create(
#             full_name=full_name,
#             email=email,
#             otp_code=otp,
#             expiry_time=timezone.now() + datetime.timedelta(minutes=5)
#         )

#         send_otp_email(email, full_name, otp)

#         return success_response(
#         "OTP sent",
#         {"signup_id": str(obj.signup_id)}
#         )
#         # return Response(
#         #     {"signup_id": str(obj.signup_id), "message": "OTP sent"},
#         #     status=200
#         # )
class SignupVerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        signup_id = request.data.get("signup_id")
        otp = request.data.get("otp")

        obj = SignupOTP.objects.filter(
            signup_id=signup_id,
            otp_code=otp,
            is_verified=False,
            expiry_time__gte=timezone.now()
        ).first()

        if not obj:
            return error_response({"error": "Invalid OTP"}, 400)

        obj.is_verified = True
        obj.save()

        return success_response({"message": "OTP verified"}, 200)
class SignupSetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        signup_id = request.data.get("signup_id")
        password = request.data.get("password")

        obj = SignupOTP.objects.filter(
            signup_id=signup_id,
            is_verified=True,
            is_used=False
        ).first()

        if not obj:
            return error_response({"error": "OTP not verified"},400)
        if User.objects.filter(email=obj.email).exists():
            return error_response("Email already registered")

        base_username = obj.email.split("@")[0]
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
        username=username,
        email=obj.email,
        password=password,
        full_name=obj.full_name
)
        

        send_welcome_email(user.email, user.username)

        return success_response({"message": "Signup successful"}, 201)        

class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Invalid request data")

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            return error_response({"error": "User not found"})

        otp = str(random.randint(100000, 999999))
        expiry = timezone.now() + datetime.timedelta(minutes=5)
        PasswordResetOTP.objects.create(user=user, otp_code=otp, expiry_time=expiry)

        try:
            send_otp_email(user.email, user.username, otp)
        except Exception as e:
            logger.error("OTP email send failed: %s", e)
            return error_response("Failed to send otp")

        return success_response({"message": "OTP sent to registered email"})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Invalid request data ")

        user = serializer.validated_data["user"]
        otp_obj = serializer.validated_data["otp_obj"]
        new_password = serializer.validated_data["new_password"]

        user.password = make_password(new_password)
        user.save()

        otp_obj.is_used = True
        otp_obj.save()

        return success_response({"message": "Password reset successful"})


# class EventFormView(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         serializer = EventFormSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Event form saved successfully"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request):
#         forms = EventForm.objects.all()
#         serializer = EventFormSerializer(forms, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            return success_response(
                "Login successful",
                data=response.data
            )

        return error_response("Invalid credentials")    
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            return success_response(
                "Token refreshed",
                data=response.data
            )

        return error_response("Invalid refresh token")
class CustomTokenVerifyView(TokenVerifyView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            return success_response("Token valid")

        return error_response("Invalid token")        


