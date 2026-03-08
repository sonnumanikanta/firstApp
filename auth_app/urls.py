from django.urls import path
from .views import (
    home,
    SignupRequestOTPView,
    SignupVerifyOTPView,
    SignupSetPasswordView,
    ForgetPasswordView,
    ResetPasswordView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    # EventFormView,
)

urlpatterns = [
    path('', home, name='home'),

    # User Auth APIs
    # path('signup/', SignupView.as_view(), name='signup'),
    path('signup/request-otp/', SignupRequestOTPView.as_view()),
    path('signup/verify-otp/', SignupVerifyOTPView.as_view()),
    path('signup/set-password/', SignupSetPasswordView.as_view()),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),

    # Password Reset APIs
    path('forget-password/', ForgetPasswordView.as_view(), name='forget_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Event Form APIs
    # path('event-form/', EventFormView.as_view(), name='event_form'),

]
