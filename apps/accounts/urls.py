from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "register/",
        views.register_view,
        name="register",
    ),

    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),

    path(
        "profile/edit/",
        views.edit_profile_view,
        name="edit_profile",
    ),

    path(
        "change-password/",
        views.change_password_view,
        name="change_password",
    ),

    # ======================================================
    # Forgot Password
    # ======================================================

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/forgot_password.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url="/accounts/password-reset/done/",
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/reset/done/",
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path(
    "create-render-admin/",
    views.create_render_admin,
    name="create_render_admin",
    ),

]