from django.urls import path
from .views import (auth_view, CustomLogoutView, verify_otp, resend_otp, forgot_password, reset_password, resend_reset_otp, verify_existing_account)
urlpatterns = [
    path('auth/', auth_view, name='auth'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('verify/<int:user_id>/', verify_otp, name='verify_otp'),
    path('resend-otp/<int:user_id>/', resend_otp, name='resend_otp'),
    path('verify-account/', verify_existing_account, name='verify_account'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<int:user_id>/', reset_password, name='reset_password'),
    path('reset-password/resend/<int:user_id>/', resend_reset_otp, name='resend_reset_otp'),
]

