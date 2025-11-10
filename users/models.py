from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator
from django.db import IntegrityError, models, transaction
from django.db.models.functions import Lower


class UserManager(BaseUserManager):
    """Custom manager with email-as-username semantics."""

    use_in_migrations = True

    @transaction.atomic
    def create_user(self, email: str, password: str | None = None, **extra):
        if not email:
            raise ValueError("Email is required")

        # Normalise email (BaseUserManager normalises domain; we also lower the whole address
        # to align with the case-insensitive DB constraint)
        email = self.normalize_email(email).strip().lower()

        user = self.model(email=email, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        # Run field validators (includes EmailValidator on the model field)
        user.full_clean()

        try:
            user.save(using=self._db)
        except IntegrityError as e:
            # If another request created the same (case-insensitive) email concurrently
            raise ValueError("A user with this email already exists") from e

        return user

    @transaction.atomic
    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)

        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # NOTE: unique=False here because we enforce *case-insensitive* uniqueness via a constraint below.
    email = models.EmailField(validators=[EmailValidator()], unique=False)

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    # Admin / auth flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Auth config
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []  # createsuperuser will only prompt for email + password

    objects = UserManager()

    class Meta:
        # Enforce **case-insensitive** uniqueness at the database level.
        # Postgres: creates a functional unique index on lower(email).
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="users_email_ci_unique",
            ),
        ]
        # Optional niceties:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:  # helpful in admin/logs
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.email
