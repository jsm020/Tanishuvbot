
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, telegram_id, name, gender, age, latitude, longitude, password=None, **extra_fields):
        if not telegram_id:
            raise ValueError('The Telegram ID must be set')
        user = self.model(
            telegram_id=telegram_id,
            name=name,
            gender=gender,
            age=age,
            latitude=latitude,
            longitude=longitude,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_id, name, gender, age, latitude, longitude, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(telegram_id, name, gender, age, latitude, longitude, password, **extra_fields)

from django.contrib.auth.models import PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)  # ' ' / 'female'
    age = models.PositiveIntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_banned = models.BooleanField(default=False)

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = ['name', 'gender', 'age', 'latitude', 'longitude']

    def __str__(self):
        return f"{self.name} ({self.telegram_id})"

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    def get_by_natural_key(self, telegram_id):
        return self.objects.get(telegram_id=telegram_id)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
