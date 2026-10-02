from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .managers import UserManager


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrator"
    CUSTOMER = "CUSTOMER", "Customer"
    DRIVER = "DRIVER", "Driver"


class User(AbstractUser):
    objects = UserManager()

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True,
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    phone_validator = RegexValidator(
        regex=r"^\+?[0-9]{10,15}$",
        message="Enter a valid phone number.",
    )

    phone = models.CharField(
        max_length=15,
        validators=[phone_validator],
        blank=True,
        null=True,
    )

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    address = models.TextField(
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        default="India",
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )

    email_verified = models.BooleanField(
        default=False,
    )

    phone_verified = models.BooleanField(
        default=False,
    )

    is_online = models.BooleanField(
        default=False,
    )

    last_seen = models.DateTimeField(
        blank=True,
        null=True,
    )

    failed_login_attempts = models.PositiveIntegerField(
        default=0,
    )

    account_locked_until = models.DateTimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["role", "is_active"]),
        ]

    def clean(self):
        super().clean()

        if self.email:
            self.email = self.email.lower().strip()

        if self.phone:
            self.phone = self.phone.strip()

    def save(self, *args, **kwargs):
     if self.email:
        self.email = self.email.lower().strip()

     if not self.username:
        base = self.email.split("@")[0]
        username = base
        counter = 1

        while User.objects.filter(username=username).exclude(pk=self.pk).exists():
            username = f"{base}{counter}"
            counter += 1

        self.username = username

     self.full_clean()

     super().save(*args, **kwargs)

    @property
    def is_account_locked(self):
        if not self.account_locked_until:
            return False

        return timezone.now() < self.account_locked_until

    def verify_email(self):
        self.email_verified = True
        self.save(update_fields=["email_verified"])

    def verify_phone(self):
        self.phone_verified = True
        self.save(update_fields=["phone_verified"])

    @property
    def full_name(self):
        return " ".join(
            filter(None, [self.first_name, self.last_name])
        ) or self.email

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_tokens",
    )

    token = models.CharField(
        max_length=255,
        unique=True,
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
       ordering = ["-created_at"]

    indexes = [
        models.Index(fields=["token"]),
        models.Index(fields=["expires_at"]),
        models.Index(fields=["is_used"]),
    ]

    def __str__(self):
        return f"{self.user.email} Verification"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_tokens",
    )

    token = models.CharField(
        max_length=255,
        unique=True,
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    indexes = [
        models.Index(fields=["token"]),
        models.Index(fields=["expires_at"]),
        models.Index(fields=["is_used"]),
    ]

    def __str__(self):
        return f"{self.user.email} Password Reset"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class LoginHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_history",
    )

    ip_address = models.GenericIPAddressField()

    user_agent = models.TextField()

    login_time = models.DateTimeField(
        auto_now_add=True,
    )

    logout_time = models.DateTimeField(
        blank=True,
        null=True,
    )

    successful = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["-login_time"]

    indexes = [
        models.Index(fields=["user"]),
        models.Index(fields=["login_time"]),
        models.Index(fields=["successful"]),
    ]

    def __str__(self):
        return f"{self.user.email} - {self.login_time}"