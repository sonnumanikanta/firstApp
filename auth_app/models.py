from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.db import models


# ==========================
# Custom User Manager
# ==========================
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username.strip(), email=email, **extra_fields)
        user.set_password(password)  # ✅ hashes password automatically
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, email, password, **extra_fields)


# ==========================
# Custom User Model
# ==========================
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    # ✅ AbstractBaseUser already has a password field, so no need to redefine.
    # Remove redundant password field to avoid confusion.
    created_at = models.DateTimeField(auto_now_add=True)

    # Status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Optional profile fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)

    objects = UserManager()

    # ✅ Login with email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.username} ({self.email})"


# ==========================
# OTP Model (for Forget Password / 2FA)
# ==========================
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_otps")
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_code}"
class SignupOTP(models.Model):
    signup_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    full_name=models.CharField(max_length=200)
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    expiry_time = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)    