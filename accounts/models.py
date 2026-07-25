from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, _user_has_module_perms, _user_has_perm
from django.core.exceptions import ValidationError
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, username, password):
        if not email:
            raise ValueError("Please Enter a valid email")
        if not password:
            raise ValueError("Please enter a valid password")
        if not username:
            raise ValueError("Please enter a valid username")
        if not first_name:
            raise ValueError("Please enter a valid name")
        if not last_name:
            raise ValueError("Please enter a valid surname")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=self.model.normalize_username(username)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, username, password):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, first_name, last_name, username, password):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password
        )
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    profile_image = models.FileField(upload_to='accounts/images', blank=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(max_length=50)
    date_joined = models.DateTimeField(auto_now_add=True, editable=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        if self.is_active and self.is_admin:
            return True
        return _user_has_module_perms(self, app_label)

    def has_perm(self, app_label, obj=None):
        if self.is_active and self.is_admin:
            return True
        return _user_has_perm(self, app_label, obj)
