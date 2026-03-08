from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.contrib.auth import authenticate
from django.utils import timezone

from .models import User, PasswordResetOTP
from eventform_app.models import EventForm


# ==========================
# Signup Serializer
# ==========================
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        val = value.strip()
        if User.objects.filter(username=val).exists():
            raise serializers.ValidationError("Username already exists.")
        return val

    def validate_email(self, value):
        val = value.strip().lower()
        if User.objects.filter(email=val).exists():
            raise serializers.ValidationError("Email already exists.")
        return val

    def create(self, validated_data):
        try:
            validated_data['password'] = make_password(validated_data['password'])
            user = User.objects.create(**validated_data)
            return user
        except IntegrityError:
            raise serializers.ValidationError({"error": "Username or email already exists"})


# ==========================
# Login Serializer
# ==========================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email").strip().lower()
        password = data.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data["user"] = user
        return data


# ==========================
# Forget Password Serializer
# ==========================
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        val = value.strip().lower()
        if not User.objects.filter(email=val).exists():
            raise serializers.ValidationError("No user found with this email")
        return val


# ==========================
# Reset Password Serializer
# ==========================
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data.get("email").strip().lower()
        otp_code = data.get("otp_code")
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError({"error": "User not found"})

        otp_obj = PasswordResetOTP.objects.filter(
            user=user, otp_code=otp_code, is_used=False
        ).order_by('-created_at').first()

        if not otp_obj:
            raise serializers.ValidationError({"error": "Invalid OTP"})
        if otp_obj.expiry_time < timezone.now():
            raise serializers.ValidationError({"error": "OTP expired"})

        data["user"] = user
        data["otp_obj"] = otp_obj
        return data


# ==========================
# EventForm Serializer
# ==========================
class EventFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventForm
        fields = ['event_name', 'contact_number', 'photo', 'event_date']

    def validate_contact_number(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Contact number must be at least 10 digits.")
        return value
